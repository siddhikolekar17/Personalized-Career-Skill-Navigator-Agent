"""Core engine: requirements, skill gaps, priorities, career match, explanations.

Model in one paragraph
----------------------
Every skill is rated on a 0-3 scale (None, Beginner, Intermediate, Advanced).
A user's *effective level* is their self-rated level plus the gains from learning
activities they have completed. A career requires each skill at some level with an
importance weight (1-5). The gap for a skill is ``required - effective``; its
priority score is ``importance * gap * (1 + 0.25 * skills it unlocks)`` with a small
boost when the skill matches the user's interests. Prerequisites of required skills
are added automatically as foundation gaps.
"""
from __future__ import annotations

import re

from backend import data

LEVELS = data.LEVELS
EPS = 1e-9


# ---------------------------------------------------------------- helpers
def describe_level(value: float) -> str:
    """Human label for a fractional level, e.g. 1.5 -> 'Beginner+'."""
    if value <= 0:
        return "None"
    if value < 1:
        return "Getting started"
    whole = min(int(value + EPS), 3)
    return LEVELS[whole] + ("+" if value - whole >= 0.25 and whole < 3 else "")


def readiness_label(match: float) -> str:
    if match < 30:
        return "Just starting"
    if match < 60:
        return "Building momentum"
    if match < 85:
        return "Nearly job-ready"
    return "Job-ready"


# ---------------------------------------------------------- career lookup
def resolve_career(profile: dict) -> dict:
    """Return the target career for a profile (built-in or user-defined)."""
    target = profile.get("target_career")
    custom = profile.get("custom_career")
    if custom and target == custom.get("name"):
        reqs = {
            skill: (int(v["importance"]), int(v["required"]))
            for skill, v in custom["requirements"].items()
            if skill in data.SKILLS
        }
        return {
            "name": target,
            "description": "A role you defined yourself.",
            "interests": [],
            "requirements": reqs,
            "capstone": (f"Capstone: a portfolio project that proves your {target} skills", 30),
            "certifications": [],
        }
    if target not in data.CAREERS:
        raise ValueError(f"Unknown career: {target!r}")
    return {"name": target, **data.CAREERS[target]}


def get_requirements(career: dict, market_updates: list[dict] | None = None) -> dict[str, dict]:
    """Base requirements of a career merged with any market updates for it."""
    reqs = {
        skill: {"importance": imp, "required": req, "source": "career", "note": ""}
        for skill, (imp, req) in career["requirements"].items()
    }
    for upd in market_updates or []:
        if upd["career"] != career["name"] or upd["skill"] not in data.SKILLS:
            continue
        reqs[upd["skill"]] = {
            "importance": int(upd["importance"]),
            "required": int(upd["required"]),
            "source": "market update",
            "note": upd.get("note") or "",
        }
    return reqs


def expand_prerequisites(reqs: dict[str, dict]) -> dict[str, dict]:
    """Add missing prerequisite skills (level 1) and record what each unlocks."""
    full = {skill: {**r, "needed_for": []} for skill, r in reqs.items()}
    queue = list(full)
    while queue:
        skill = queue.pop(0)
        for pre in data.SKILLS[skill]["prereqs"]:
            if pre not in full:
                full[pre] = {
                    "importance": max(2, full[skill]["importance"] - 1),
                    "required": 1,
                    "source": "prerequisite",
                    "note": "",
                    "needed_for": [],
                }
                queue.append(pre)
            if skill not in full[pre]["needed_for"]:
                full[pre]["needed_for"].append(skill)
    return full


# ------------------------------------------------------- effective levels
def effective_levels(profile_skills: dict[str, int], completed_ids: set[str]) -> dict[str, float]:
    """Self-rated level plus the gain from completed activities (capped at 3)."""
    eff = {s: float(l) for s, l in profile_skills.items() if s in data.SKILLS}
    for rid in completed_ids:
        res = data.RESOURCES.get(rid)
        if not res:
            continue  # e.g. capstone projects carry no skill gain
        if res["level"] > profile_skills.get(res["skill"], 0):
            eff[res["skill"]] = eff.get(res["skill"], 0.0) + res["gain"]
    return {s: min(3.0, round(v, 3)) for s, v in eff.items()}


# --------------------------------------------------------------- skill gaps
def compute_skill_gaps(profile: dict, reqs_full: dict[str, dict], completed_ids: set[str]) -> list[dict]:
    base = profile.get("skills", {})
    eff = effective_levels(base, completed_ids)
    interests = set(profile.get("interests", []))
    career_name = profile.get("target_career", "this role")

    gaps: list[dict] = []
    for skill, r in reqs_full.items():
        current = eff.get(skill, 0.0)
        required = r["required"]
        gap = max(0.0, required - current)
        if gap <= EPS:
            status = "Met"
        elif current <= 0:
            status = "Missing"
        else:
            status = "Underdeveloped"

        multiplier = 1 + 0.25 * len(r["needed_for"])
        category = data.SKILLS[skill]["category"]
        interest_match = category in interests
        if interest_match:
            multiplier *= 1.15
        score = round(r["importance"] * gap * multiplier, 2) if gap > EPS else 0.0

        gaps.append({
            "skill": skill, "category": category, "importance": r["importance"], "required": required,
            "base": int(base.get(skill, 0)), "current": current, "gap": round(gap, 3), "status": status,
            "score": score, "source": r["source"], "needed_for": r["needed_for"], "note": r["note"],
            "interest_match": interest_match,
        })

    top = max((g["score"] for g in gaps), default=0.0)
    for g in gaps:
        if g["status"] == "Met":
            g["priority"] = "None"
        else:
            ratio = g["score"] / top if top else 0
            g["priority"] = "High" if ratio >= 0.6 else "Medium" if ratio >= 0.3 else "Low"

    gaps.sort(key=lambda g: (-g["score"], g["skill"]))
    rank = 0
    for g in gaps:
        if g["score"] > 0:
            rank += 1
            g["rank"] = rank
        else:
            g["rank"] = None
        g["reason"] = explain_gap(g, career_name)
    return gaps


def explain_gap(g: dict, career_name: str) -> str:
    """Plain-language explanation of why a skill is (or is not) a priority."""
    skill, req = g["skill"], LEVELS[g["required"]]
    parts = []
    if g["source"] == "prerequisite":
        parts.append(f"{skill} is a foundation for {_join(g['needed_for'])}, so it has to come first.")
    else:
        parts.append(f"{career_name} needs {skill} at {req} level (importance {g['importance']}/5).")
    if g["status"] == "Met":
        parts.append(f"You already reach {describe_level(g['current'])}, so no action is needed.")
    elif g["status"] == "Missing":
        parts.append("You have no recorded experience with it yet.")
    else:
        parts.append(
            f"You are at {describe_level(g['current'])} (about {g['current']:.1f} of {g['required']}), "
            f"a gap of {g['gap']:.1f} level(s)."
        )
    if g["source"] != "prerequisite" and g["needed_for"] and g["status"] != "Met":
        parts.append(f"It also unlocks {_join(g['needed_for'])}, which raises its priority.")
    if g["interest_match"] and g["status"] != "Met":
        parts.append(f"It matches your interest in {g['category']}, so it gets a small boost.")
    if g["source"] == "market update":
        parts.append(f"Requirement added by a market update. {g['note']}".strip())
    return " ".join(parts)


def _join(items: list[str]) -> str:
    return ", ".join(items[:-1]) + f" and {items[-1]}" if len(items) > 1 else (items[0] if items else "")


# -------------------------------------------------------------- career match
def career_match(gaps: list[dict]) -> float:
    """Importance-weighted % of the career's own requirements already covered."""
    core = [g for g in gaps if g["source"] != "prerequisite"]
    total = sum(g["importance"] for g in core)
    if not total:
        return 0.0
    got = sum(g["importance"] * min(g["current"] / g["required"], 1.0) for g in core)
    return round(100 * got / total, 1)


def rank_careers(profile: dict, completed_ids: set[str], market_updates: list[dict] | None = None) -> list[dict]:
    """Score every built-in career for this profile (skills 75%, interests 25%)."""
    eff = effective_levels(profile.get("skills", {}), completed_ids)
    interests = set(profile.get("interests", []))
    results = []
    for name, info in data.CAREERS.items():
        career = {"name": name, **info}
        reqs = get_requirements(career, market_updates)
        total = sum(r["importance"] for r in reqs.values())
        got = sum(r["importance"] * min(eff.get(s, 0.0) / r["required"], 1.0) for s, r in reqs.items())
        match = 100 * got / total if total else 0.0
        overlap = sorted(set(info["interests"]) & interests)
        overlap_pct = 100 * len(overlap) / len(info["interests"]) if info["interests"] else 0.0
        results.append({
            "name": name, "description": info["description"], "match": round(match, 1),
            "fit": round(0.75 * match + 0.25 * overlap_pct, 1), "matched_interests": overlap,
        })
    return sorted(results, key=lambda c: -c["fit"])


# ------------------------------------------------------- skill detection
def extract_skills_from_text(text: str) -> list[str]:
    """Find library skills mentioned in free text (resume, bio, notes)."""
    lowered = (text or "").lower()
    found = []
    for skill, meta in data.SKILLS.items():
        for alias in meta["aliases"]:
            pattern = rf"(?<![a-z0-9+#]){re.escape(alias)}(?![a-z0-9+#])"
            if re.search(pattern, lowered):
                found.append(skill)
                break
    return found
