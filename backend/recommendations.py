"""Choose learning resources for a skill gap and explain why they were chosen."""
from __future__ import annotations

from backend import data
from backend.career_engine import describe_level

STYLE_TO_TYPE = {
    "Structured courses": "course",
    "Hands-on projects": "project",
    "Certifications": "certification",
    "Mixed (balanced)": None,
}
TYPE_ORDER = {"course": 0, "project": 1, "certification": 2, "activity": 3}
TYPE_LABEL = {"course": "Course", "project": "Project", "certification": "Certification", "activity": "Practice"}
TYPE_WHY = {
    "course": "gives you structured theory and a clear path through the topic",
    "project": "turns the theory into portfolio proof you can show employers",
    "certification": "validates the skill with a credential employers recognise",
    "activity": "reinforces the skill through deliberate practice",
}


def select_resources(
    skill: str,
    current: float,
    required: int,
    completed_ids: set[str],
    profile: dict | None = None,
    fast_track: bool = False,
    priority: str = "Medium",
) -> list[dict]:
    """Resources that still move the user from ``current`` towards ``required``.

    A resource of level L is needed when ``current < L <= required`` and it has not
    been completed. Within a level, the user's preferred learning style comes first.
    Fast-track mode drops optional practice steps for non-high-priority skills.
    """
    preferred = STYLE_TO_TYPE.get((profile or {}).get("learning_style"))
    picks = []
    for res in data.RESOURCES_BY_SKILL.get(skill, []):
        if res["id"] in completed_ids or not (current < res["level"] <= required):
            continue
        if fast_track and res["type"] == "activity" and priority != "High":
            continue
        picks.append(res)
    picks.sort(key=lambda r: (r["level"], 0 if preferred and r["type"] == preferred else 1, TYPE_ORDER[r["type"]]))
    return picks


def explain_resource(res: dict, gap: dict, career_name: str, profile: dict | None = None) -> str:
    """Why this specific activity is recommended right now."""
    text = (
        f"{res['skill']} is a {gap['priority'].lower()}-priority gap for {career_name}: "
        f"you are at {describe_level(gap['current'])} and the role needs {data.LEVELS[gap['required']]}. "
        f"This {TYPE_LABEL[res['type']].lower()} {TYPE_WHY[res['type']]} "
        f"and builds {data.LEVELS[res['level']].lower()}-level ability."
    )
    preferred = STYLE_TO_TYPE.get((profile or {}).get("learning_style"))
    if preferred and preferred == res["type"]:
        text += " It also matches your preferred learning style."
    return text


def recommend_next_actions(roadmap: dict, n: int = 3) -> list[dict]:
    """The first ``n`` pending roadmap items, in the order they should be done."""
    items = [item for phase in roadmap["phases"] for item in phase["items"]]
    return items[:n]


def group_by_type(roadmap: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {t: [] for t in TYPE_ORDER}
    for phase in roadmap["phases"]:
        for item in phase["items"]:
            grouped[item["type"]].append(item)
    return grouped
