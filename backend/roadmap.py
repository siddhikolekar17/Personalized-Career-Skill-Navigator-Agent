"""Roadmap generation, scheduling and adaptive feedback.

The roadmap is rebuilt from scratch on every run from the *current* gaps, so it adapts
automatically when the user completes activities, changes requirements or turns on
fast-track mode. Nothing is stored except the list of completed resource ids.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

from backend import data
from backend.career_engine import describe_level
from backend.recommendations import TYPE_LABEL, explain_resource, select_resources

PHASE_INFO = {
    1: ("Phase 1: Foundations", "Build the basics and unblock everything that depends on them."),
    2: ("Phase 2: Core skills", "Apply the fundamentals in real projects."),
    3: ("Phase 3: Advanced and job-ready", "Specialise, earn credentials and prove it with a capstone."),
}


def capstone_item(career: dict) -> dict:
    title, hours = career["capstone"]
    return {
        "id": f"capstone-{data.slug(career['name'])}", "skill": "Capstone", "level": 3, "type": "project",
        "title": title, "provider": "Portfolio project", "hours": hours, "link": None, "gain": 0,
    }


def generate_roadmap(
    profile: dict, gaps: list[dict], completed_ids: set[str], career: dict, fast_track: bool = False
) -> dict:
    weekly = max(1, int(profile.get("weekly_hours") or 8))
    unmet = {g["skill"]: g for g in gaps if g["status"] != "Met"}

    picks_by_skill = {
        skill: select_resources(skill, g["current"], g["required"], completed_ids, profile, fast_track, g["priority"])
        for skill, g in unmet.items()
    }
    memo: dict[tuple, int] = {}

    def depth(skill: str, level: int, trail: tuple = ()) -> int:
        """Longest chain of prerequisites that still have steps at this phase level."""
        key = (skill, level)
        if key in memo:
            return memo[key]
        pres = [
            p for p in data.SKILLS[skill]["prereqs"]
            if p not in trail and any(r["level"] == level for r in picks_by_skill.get(p, []))
        ]
        memo[key] = 0 if not pres else 1 + max(depth(p, level, trail + (skill,)) for p in pres)
        return memo[key]

    entries = []
    for skill, picks in picks_by_skill.items():
        g = unmet[skill]
        for idx, res in enumerate(picks):
            entries.append((res["level"], depth(skill, res["level"]), -g["score"], skill, idx, res, g))
    entries.sort(key=lambda e: e[:5])
    ordered = [(e[5], e[6]) for e in entries]

    cap = capstone_item(career)
    cap_done = cap["id"] in completed_ids
    if not cap_done:
        ordered.append((cap, None))

    # Schedule sequentially by weekly study hours.
    phases: dict[int, list[dict]] = {}
    cumulative = 0.0
    for res, gap in ordered:
        start = int(cumulative // weekly) + 1
        cumulative += res["hours"]
        end = max(start, math.ceil(cumulative / weekly))
        if gap is None:
            why = (
                f"The capstone ties your new {career['name']} skills together into one showcase project "
                "and is best done last."
            )
            priority = "High"
        else:
            why, priority = explain_resource(res, gap, career["name"], profile), gap["priority"]
        phases.setdefault(res["level"], []).append(
            {**res, "start_week": start, "end_week": end, "why": why, "priority": priority}
        )

    relevant = {g["skill"] for g in gaps}
    completed_items = [
        data.RESOURCES[rid] for rid in sorted(completed_ids)
        if rid in data.RESOURCES and data.RESOURCES[rid]["skill"] in relevant
    ]
    if cap_done:
        completed_items.append(cap)

    remaining_hours = sum(res["hours"] for res, _ in ordered)
    completed_hours = sum(item["hours"] for item in completed_items)
    total = remaining_hours + completed_hours

    return {
        "phases": [
            {"level": lvl, "name": PHASE_INFO[lvl][0], "description": PHASE_INFO[lvl][1], "items": items}
            for lvl, items in sorted(phases.items())
        ],
        "pending_count": len(ordered),
        "total_hours": remaining_hours,
        "total_weeks": math.ceil(remaining_hours / weekly) if remaining_hours else 0,
        "weekly_hours": weekly,
        "completed_items": completed_items,
        "completed_hours": completed_hours,
        "progress_pct": round(100 * completed_hours / total, 1) if total else 100.0,
        "fast_track": fast_track,
    }


def build_adaptive_notes(
    profile: dict,
    career_name: str,
    gaps: list[dict],
    roadmap: dict,
    market_updates: list[dict],
    created_at: datetime | None = None,
    fast_track: bool = False,
    now: datetime | None = None,
) -> list[dict]:
    """Explain how the plan changed because of progress, requirements and pace."""
    notes: list[dict] = []

    for g in gaps:
        if g["current"] - g["base"] <= 0:
            continue
        if g["status"] == "Met" and g["base"] < g["required"]:
            notes.append({"kind": "progress", "text": (
                f"You closed the {g['skill']} gap through completed activities, "
                "so its remaining steps were removed from the roadmap.")})
        elif g["status"] != "Met":
            notes.append({"kind": "progress", "text": (
                f"{g['skill']} moved from {data.LEVELS[g['base']]} to {describe_level(g['current'])}. "
                "The roadmap now lists only what is still missing.")})

    for upd in market_updates:
        if upd["career"] == career_name:
            notes.append({"kind": "market", "text": (
                f"Requirement change: {upd['skill']} is now expected at {data.LEVELS[upd['required']]} level "
                f"(importance {upd['importance']}/5). {upd.get('note') or ''} Priorities were recalculated.").replace("  ", " ")})

    unmet = [g for g in gaps if g["status"] != "Met"]
    if unmet:
        top = unmet[0]
        notes.append({"kind": "focus", "text": (
            f"Your top priority right now is {top['skill']} (priority score {top['score']}).")})
    else:
        notes.append({"kind": "done", "text": (
            "All skill gaps are closed. Finish the capstone project and start applying.")})

    weekly = roadmap["weekly_hours"]
    if created_at is not None:
        now = now or datetime.now(timezone.utc)
        days = (now - created_at).total_seconds() / 86400
        expected = days / 7 * weekly
        done = roadmap["completed_hours"]
        if days < 1 or expected <= 0:
            notes.append({"kind": "pace", "text": "Your plan starts today. Complete a step to begin tracking pace."})
        elif done >= expected:
            notes.append({"kind": "pace", "text": (
                f"You are on or ahead of pace: {done:.0f} of about {expected:.0f} planned hours are done.")})
        elif done >= 0.5 * expected:
            notes.append({"kind": "slight", "text": (
                f"You are slightly behind: {done:.0f} of about {expected:.0f} planned hours are done.")})
        else:
            hint = "" if fast_track else " Turn on fast-track mode to drop optional practice steps."
            notes.append({"kind": "behind", "text": (
                f"You are behind pace: {done:.0f} of about {expected:.0f} planned hours are done.{hint}")})
    return notes


def roadmap_to_markdown(profile: dict, career_name: str, match: float, roadmap: dict) -> str:
    """Plain-text export of the roadmap for download."""
    lines = [
        f"# Learning roadmap for {profile['name']}",
        "",
        f"Target role: **{career_name}**  ",
        f"Current career match: **{match:.0f}%**  ",
        f"Remaining: **{roadmap['total_hours']} hours** (about {roadmap['total_weeks']} weeks "
        f"at {roadmap['weekly_hours']} hours a week)",
        "",
    ]
    if not roadmap["phases"]:
        lines.append("All roadmap steps are complete.")
    for phase in roadmap["phases"]:
        lines += [f"## {phase['name']}", f"_{phase['description']}_", ""]
        for item in phase["items"]:
            lines.append(
                f"- [ ] **{item['title']}** ({TYPE_LABEL[item['type']]}, {item['provider']}) - "
                f"{item['skill']}, {item['hours']} h, weeks {item['start_week']}-{item['end_week']}"
            )
            lines.append(f"  - Why: {item['why']}")
        lines.append("")
    if roadmap["completed_items"]:
        lines += ["## Completed", ""]
        lines += [f"- [x] {item['title']} ({item['skill']})" for item in roadmap["completed_items"]]
    return "\n".join(lines)
