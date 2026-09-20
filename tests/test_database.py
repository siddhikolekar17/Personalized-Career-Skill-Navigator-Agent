from backend import data, database


def test_save_and_load_profile_round_trip(tmp_db):
    database.save_profile(data.DEMO_PROFILE, tmp_db)
    loaded = database.load_profile("Demo Student", tmp_db)
    assert loaded == data.DEMO_PROFILE
    assert database.list_profiles(tmp_db) == ["Demo Student"]
    assert database.load_profile("Nobody", tmp_db) is None


def test_saving_again_keeps_created_at(tmp_db):
    database.save_profile(data.DEMO_PROFILE, tmp_db)
    created = database.get_profile_created_at("Demo Student", tmp_db)
    database.save_profile({**data.DEMO_PROFILE, "weekly_hours": 3}, tmp_db)
    assert database.get_profile_created_at("Demo Student", tmp_db) == created
    assert database.load_profile("Demo Student", tmp_db)["weekly_hours"] == 3


def test_progress_mark_unmark_reset(tmp_db):
    database.mark_completed("A", "python-l1-course", "Python", tmp_db)
    database.mark_completed("A", "python-l1-course", "Python", tmp_db)  # idempotent
    database.mark_completed("B", "sql-l1-course", "SQL", tmp_db)
    assert database.get_completed("A", tmp_db) == {"python-l1-course"}
    database.unmark_completed("A", "python-l1-course", tmp_db)
    assert database.get_completed("A", tmp_db) == set()
    database.record_history("B", 12.5, tmp_db)
    database.reset_progress("B", tmp_db)
    assert database.get_completed("B", tmp_db) == set() and database.get_history("B", tmp_db) == []


def test_market_updates_upsert_and_clear(tmp_db):
    database.add_market_update("Data Analyst", "SQL", 3, 2, "one", tmp_db)
    database.add_market_update("Data Analyst", "SQL", 5, 3, "two", tmp_db)
    database.add_market_update("Data Scientist", "Python", 4, 3, "", tmp_db)
    rows = database.get_market_updates("Data Analyst", tmp_db)
    assert len(rows) == 1 and rows[0]["importance"] == 5 and rows[0]["note"] == "two"
    assert len(database.get_market_updates(None, tmp_db)) == 2
    database.clear_market_updates("Data Analyst", tmp_db)
    assert len(database.get_market_updates(None, tmp_db)) == 1


def test_history_is_ordered(tmp_db):
    for v in (10, 20, 30):
        database.record_history("A", v, tmp_db)
    assert [h["match_pct"] for h in database.get_history("A", tmp_db)] == [10, 20, 30]


def test_delete_profile_removes_everything(tmp_db):
    database.save_profile(data.DEMO_PROFILE, tmp_db)
    database.mark_completed("Demo Student", "x", None, tmp_db)
    database.delete_profile("Demo Student", tmp_db)
    assert database.list_profiles(tmp_db) == [] and database.get_completed("Demo Student", tmp_db) == set()
