from datetime import datetime, timedelta, timezone

from backend import data
from backend.analysis import complete_activity, run_analysis
from backend.roadmap import build_adaptive_notes, roadmap_to_markdown


def _items(result):
    return [i for ph in result["roadmap"]["phases"] for i in ph["items"]]


def _profile(**over):
    p = dict(data.DEMO_PROFILE)
    p.update(over)
    return p


def test_roadmap_is_ordered_by_phase_and_weeks_never_go_backwards(tmp_db):
    result = run_analysis(_profile(), tmp_db)
    items = _items(result)
    assert items
    assert [i["level"] for i in items] == sorted(i["level"] for i in items)
    assert all(b["start_week"] >= a["start_week"] for a, b in zip(items, items[1:]))
    assert items[-1]["skill"] == "Capstone"


def test_prerequisite_comes_before_dependent_in_same_phase(tmp_db):
    result = run_analysis(_profile(skills={}, target_career="Machine Learning Engineer"), tmp_db)
    first_seen = {}
    for idx, i in enumerate(_items(result)):
        first_seen.setdefault((i["skill"], i["level"]), idx)
    assert first_seen[("Python", 1)] < first_seen[("Machine Learning", 1)]
    assert first_seen[("Machine Learning", 1)] < first_seen[("Deep Learning", 1)]


def test_completing_a_step_updates_roadmap_match_and_progress(tmp_db):
    p = _profile()
    before = run_analysis(p, tmp_db)
    first = _items(before)[0]
    after = complete_activity(p, first["id"], tmp_db)
    assert first["id"] not in {i["id"] for i in _items(after)}
    assert after["match"] >= before["match"]
    assert after["roadmap"]["progress_pct"] > before["roadmap"]["progress_pct"]
    assert after["roadmap"]["total_hours"] == before["roadmap"]["total_hours"] - first["hours"]
    assert len(after["history"]) == 2  # baseline + after completion


def test_closing_a_gap_removes_remaining_steps_and_adds_note(tmp_db):
    p = _profile(skills={"SQL": 1}, target_career="Data Analyst", interests=[])
    result = run_analysis(p, tmp_db)
    sql_steps = [i for i in _items(result) if i["skill"] == "SQL"]
    assert [i["level"] for i in sql_steps] == [2, 2]
    for step in sql_steps:
        result = complete_activity(p, step["id"], tmp_db)
    gap = next(g for g in result["gaps"] if g["skill"] == "SQL")
    assert gap["status"] == "Met"
    assert not [i for i in _items(result) if i["skill"] == "SQL"]
    assert any("closed the SQL gap" in n["text"] for n in result["notes"])


def test_weekly_hours_change_the_schedule(tmp_db):
    slow = run_analysis(_profile(weekly_hours=5), tmp_db)["roadmap"]["total_weeks"]
    fast = run_analysis(_profile(weekly_hours=20), tmp_db)["roadmap"]["total_weeks"]
    assert slow > fast


def test_fast_track_drops_optional_practice_for_non_high_priority(tmp_db):
    normal = _items(run_analysis(_profile(), tmp_db))
    fast = _items(run_analysis(_profile(), tmp_db, fast_track=True))
    assert len(fast) < len(normal)
    assert all(i["type"] != "activity" or i["priority"] == "High" for i in fast)


def test_learning_style_changes_order_within_a_level(tmp_db):
    def first_l2(style):
        items = _items(run_analysis(_profile(learning_style=style), tmp_db))
        return next(i for i in items if i["skill"] == "Statistics" and i["level"] == 2)["type"]
    assert first_l2("Hands-on projects") == "project"
    assert first_l2("Structured courses") == "course"


def test_market_update_reprioritises(tmp_db):
    from backend import database
    p = _profile(target_career="Data Analyst", skills={"SQL": 2})
    before = run_analysis(p, tmp_db)
    database.add_market_update("Data Analyst", "Generative AI & LLMs", 5, 2, "test", tmp_db)
    after = run_analysis(p, tmp_db)
    assert "Generative AI & LLMs" not in {g["skill"] for g in before["gaps"]}
    assert "Generative AI & LLMs" in {g["skill"] for g in after["gaps"]}
    assert after["match"] < before["match"]
    assert any(n["kind"] == "market" for n in after["notes"])


def test_pace_notes(tmp_db):
    p = _profile(weekly_hours=5)
    result = run_analysis(p, tmp_db)
    created = datetime(2026, 1, 1, tzinfo=timezone.utc)
    late = build_adaptive_notes(p, "Data Scientist", result["gaps"], result["roadmap"], [], created,
                                now=created + timedelta(days=14))
    assert any("behind pace" in n["text"] and "fast-track" in n["text"] for n in late)
    fresh = build_adaptive_notes(p, "Data Scientist", result["gaps"], result["roadmap"], [], created,
                                 now=created + timedelta(hours=2))
    assert any("starts today" in n["text"] for n in fresh)


def test_finished_roadmap_and_markdown_export(tmp_db):
    p = _profile(skills={s: 3 for s in data.CAREERS["Data Analyst"]["requirements"]}, target_career="Data Analyst")
    result = run_analysis(p, tmp_db)
    assert [i["skill"] for i in _items(result)] == ["Capstone"]
    result = complete_activity(p, _items(result)[0]["id"], tmp_db)
    assert result["roadmap"]["pending_count"] == 0 and result["roadmap"]["progress_pct"] == 100.0
    md = roadmap_to_markdown(p, "Data Analyst", result["match"], result["roadmap"])
    assert "All roadmap steps are complete" in md


def test_every_item_is_explained(tmp_db):
    assert all(i["why"] for i in _items(run_analysis(_profile(), tmp_db)))
