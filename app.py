"""Personalized Career & Skill Navigator Agent - Streamlit entry point.

Run with:  streamlit run app.py
"""
import streamlit as st

from backend import data, database
from ui import components, dashboard
from ui import profile as profile_ui

st.set_page_config(page_title="Career & Skill Navigator", page_icon="🧭", layout="wide")
components.inject_css()
database.init_db()

# ---- session defaults --------------------------------------------------------
st.session_state.setdefault("profile", None)
st.session_state.setdefault("form_version", 0)
st.session_state.setdefault("nav", "Profile and goal")
if "_goto" in st.session_state:  # set by buttons, applied before the radio is drawn
    st.session_state["nav"] = st.session_state.pop("_goto")


def open_profile(profile: dict) -> None:
    st.session_state["profile"] = profile
    st.session_state["form_version"] += 1
    st.session_state["_goto"] = "Dashboard"
    st.rerun()


# ---- sidebar -------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Career & Skill Navigator")
    st.radio("Go to", ["Profile and goal", "Dashboard"], key="nav")

    st.divider()
    saved = database.list_profiles()
    if saved:
        choice = st.selectbox("Saved profiles", saved, key="load_choice")
        if st.button("Load profile"):
            loaded = database.load_profile(choice)
            if loaded:
                open_profile(loaded)
    if st.button("Try the demo profile"):
        demo = data.DEMO_PROFILE
        database.save_profile(demo)
        open_profile(demo)

    if st.session_state["profile"]:
        p = st.session_state["profile"]
        st.divider()
        st.caption(f"Signed in as **{p['name']}**")
        st.caption(f"Target: {p['target_career']}")

# ---- main area -----------------------------------------------------------------
if st.session_state["nav"] == "Profile and goal":
    submitted = profile_ui.render_profile_page()
    if submitted:
        database.save_profile(submitted)
        open_profile(submitted)
else:
    active = st.session_state["profile"]
    if not active:
        st.title("No profile yet")
        st.write("Create your profile first, or try the demo profile from the sidebar.")
    else:
        dashboard.render_dashboard(active)
