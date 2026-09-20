"""End-to-end UI smoke test using Streamlit's AppTest (no browser needed)."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("CAREER_DB_PATH", str(tmp_path / "ui.db"))
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception
    return at


def _button(at, label):
    return next(b for b in at.button if b.label == label)


def test_full_user_flow(app):
    # Profile page renders, then the demo profile opens the dashboard.
    assert any("Your profile and goal" in t.value for t in app.title)
    _button(app, "Try the demo profile").click().run()
    assert not app.exception
    assert app.session_state["nav"] == "Dashboard"
    assert len(app.tabs) == 6

    # Mark the first roadmap step complete: roadmap and score update, no errors.
    done_buttons = [b for b in app.button if b.label == "Mark complete"]
    assert done_buttons
    done_buttons[0].click().run()
    assert not app.exception
    assert any(b.label == "Undo" for b in app.button)

    # Apply a market requirement change from the adaptive tab.
    preset = next(b for b in app.button if b.label.startswith("Apply example"))
    preset.click().run()
    assert not app.exception


def test_analyze_from_form_and_custom_role(app):
    app.text_input[0].set_value("Riya").run()
    app.multiselect[1].set_value(["Python", "SQL"]).run()   # skills you already have
    app.selectbox[2].set_value("Define my own role").run()  # target career
    assert not app.exception
    _button(app, "Analyze career").click().run()
    assert app.error  # custom role needs a name and skills
    app.selectbox[2].set_value("Data Analyst").run()
    _button(app, "Analyze career").click().run()
    assert not app.exception
    assert app.session_state["profile"]["name"] == "Riya"
    assert app.session_state["nav"] == "Dashboard"
