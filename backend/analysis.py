"""Single entry point that connects profile -> gaps -> roadmap -> notes.

The UI only needs these functions; it never touches the engine modules directly.
"""
from __future__ import annotations

from datetime import datetime

from backend import data, database
from backend.career_engine import (
    career_match,
    compute_skill_gaps,
    expand_prerequisites,
    get_requirements,
    rank_careers,
    readiness_label,
    resolve_career,
)
from backend.roadmap import build_adaptive_notes, generate_roadmap


def run_analysis(
    profile: dict, db_path: str | None = None, fast_track: bool = False, now: datetime | None = None
) -> dict:
    """Run the whole pipeline for one profile using the latest saved progress."""
    name = profile["name"]
    career = resolve_career(profile)
    completed = database.get_completed(name, db_path)
    updates = database.get_market_updates(None, db_path)

    reqs = expand_prerequisites(get_requirements(career, updates))
    gaps = compute_skill_gaps(profile, reqs, completed)
    match = career_match(gaps)
    roadmap = generate_roadmap(profile, gaps, completed, career, fast_track)
    notes = build_adaptive_notes(
        profile, career["name"], gaps, roadmap, updates,
        created_at=database.get_profile_created_at(name, db_path), fast_track=fast_track, now=now,
    )
    return {
        "career": career,
        "gaps": gaps,
        "match": match,
        "readiness": readiness_label(match),
        "roadmap": roadmap,
        "notes": notes,
        "career_ranking": rank_careers(profile, completed, updates),
        "history": database.get_history(name, db_path),
        "market_updates": [u for u in updates if u["career"] == career["name"]],
        "completed_ids": completed,
    }


def complete_activity(profile: dict, resource_id: str, db_path: str | None = None, fast_track: bool = False) -> dict:
    """Mark a roadmap step done, log the new career-match score, and re-plan."""
    name = profile["name"]
    if not database.get_history(name, db_path):  # baseline before the first change
        database.record_history(name, run_analysis(profile, db_path, fast_track)["match"], db_path)
    skill = data.RESOURCES.get(resource_id, {}).get("skill", "Capstone")
    database.mark_completed(name, resource_id, skill, db_path)
    result = run_analysis(profile, db_path, fast_track)
    database.record_history(name, result["match"], db_path)
    result["history"] = database.get_history(name, db_path)
    return result


def undo_activity(profile: dict, resource_id: str, db_path: str | None = None, fast_track: bool = False) -> dict:
    """Undo a completion and re-plan."""
    database.unmark_completed(profile["name"], resource_id, db_path)
    result = run_analysis(profile, db_path, fast_track)
    database.record_history(profile["name"], result["match"], db_path)
    result["history"] = database.get_history(profile["name"], db_path)
    return result
