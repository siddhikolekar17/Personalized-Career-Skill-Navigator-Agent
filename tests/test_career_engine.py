from backend import data
from backend.career_engine import (
    career_match, compute_skill_gaps, effective_levels, expand_prerequisites,
    extract_skills_from_text, get_requirements, rank_careers, resolve_career,
)


def _gaps(profile, completed=frozenset(), updates=None):
    career = resolve_career(profile)
    reqs = expand_prerequisites(get_requirements(career, updates))
    return compute_skill_gaps(profile, reqs, set(completed))


def _profile(skills, target="Data Analyst", interests=()):
    return {"name": "T", "skills": skills, "target_career": target, "interests": list(interests), "custom_career": None}


def test_knowledge_base_is_consistent():
    for name, meta in data.SKILLS.items():
        assert all(p in data.SKILLS for p in meta["prereqs"]), name
        levels = {r["level"] for r in data.RESOURCES_BY_SKILL[name]}
        assert levels == {1, 2, 3}, name
    for career, info in data.CAREERS.items():
        for skill, (imp, req) in info["requirements"].items():
            assert skill in data.SKILLS, (career, skill)
            assert 1 <= imp <= 5 and 1 <= req <= 3


def test_completing_a_full_level_adds_exactly_one_level():
    l1 = {r["id"] for r in data.RESOURCES_BY_SKILL["SQL"] if r["level"] == 1}
    assert effective_levels({}, l1)["SQL"] == 1.0
    assert effective_levels({"SQL": 1}, l1).get("SQL") == 1.0  # already past level 1: no double counting


def test_gap_status_labels():
    gaps = {g["skill"]: g for g in _gaps(_profile({"SQL": 2, "Excel": 1}))}
    assert gaps["SQL"]["status"] == "Met"
    assert gaps["Excel"]["status"] == "Underdeveloped"
    assert gaps["BI Tools"]["status"] == "Missing"


def test_prerequisites_are_added_as_foundation_gaps():
    gaps = {g["skill"]: g for g in _gaps(_profile({}, target="Machine Learning Engineer"))}
    assert gaps["Statistics"]["source"] == "prerequisite"   # needed by Machine Learning, not in the career list
    assert gaps["Linux"]["source"] == "prerequisite"        # needed by Docker
    assert "Machine Learning" in gaps["Statistics"]["needed_for"]


def test_priority_favours_important_and_unlocking_skills():
    gaps = _gaps(_profile({}, target="Data Scientist"))
    ranks = {g["skill"]: g["rank"] for g in gaps}
    assert ranks["Machine Learning"] < ranks["Deep Learning"]
    assert all(g["priority"] == "None" for g in gaps if g["status"] == "Met")


def test_interest_boosts_score():
    plain = {g["skill"]: g["score"] for g in _gaps(_profile({}, target="Data Scientist"))}
    boosted = {g["skill"]: g["score"] for g in _gaps(_profile({}, target="Data Scientist", interests=["Data & Analytics"]))}
    assert boosted["SQL"] > plain["SQL"]
    assert boosted["Communication"] == plain["Communication"]


def test_match_rises_with_skills_and_progress():
    empty = career_match(_gaps(_profile({})))
    some = career_match(_gaps(_profile({"SQL": 2, "Excel": 2})))
    full = career_match(_gaps(_profile({s: 3 for s in data.CAREERS["Data Analyst"]["requirements"]})))
    assert empty == 0 < some < full == 100.0
    done = {r["id"] for r in data.RESOURCES_BY_SKILL["SQL"] if r["level"] == 1}
    assert career_match(_gaps(_profile({}), done)) > empty


def test_market_update_changes_requirements():
    upd = [{"career": "Data Analyst", "skill": "Generative AI & LLMs", "importance": 3, "required": 1, "note": "x"}]
    gaps = {g["skill"]: g for g in _gaps(_profile({}), updates=upd)}
    assert gaps["Generative AI & LLMs"]["source"] == "market update"
    assert "Python" in gaps and gaps["Generative AI & LLMs"]["needed_for"] == []


def test_rank_careers_finds_best_fit():
    profile = _profile({"SQL": 3, "Excel": 3, "BI Tools": 2, "Data Visualization": 2, "Statistics": 2}, interests=["Data & Analytics"])
    assert rank_careers(profile, set())[0]["name"] == "Data Analyst"


def test_custom_career_is_supported():
    profile = _profile({"Python": 1}, target="Bio Analyst")
    profile["custom_career"] = {"name": "Bio Analyst", "requirements": {"Python": {"required": 2, "importance": 5}}}
    gaps = {g["skill"]: g for g in _gaps(profile)}
    assert gaps["Python"]["status"] == "Underdeveloped" and gaps["Python"]["gap"] == 1


def test_extract_skills_from_text():
    text = "Built ML models with scikit-learn and pandas, queried PostgreSQL, deployed via Docker on AWS. Used GitHub."
    found = set(extract_skills_from_text(text))
    assert {"Machine Learning", "Data Wrangling", "SQL", "Docker", "Cloud Computing", "Git & GitHub"} <= found
    assert "JavaScript" not in found


def test_every_gap_has_an_explanation():
    for g in _gaps(_profile({"SQL": 1})):
        assert g["reason"]
