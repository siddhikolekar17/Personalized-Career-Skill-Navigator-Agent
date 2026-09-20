"""Dashboard: overview, skill gaps, roadmap, recommendations, adaptive engine, progress."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from backend import data, database
from backend.analysis import complete_activity, run_analysis, undo_activity
from backend.career_engine import describe_level
from backend.recommendations import TYPE_LABEL, group_by_type, recommend_next_actions
from backend.roadmap import roadmap_to_markdown
from ui import components as ui

GREEN, AMBER, ROUTE, INK = "#0E5A45", "#F5B700", "#2F6DB5", "#1D2B33"


def render_dashboard(profile: dict, db_path: str | None = None) -> None:
    fast_track = st.session_state.get("fast_track", False)
    result = run_analysis(profile, db_path, fast_track=fast_track)
    career, gaps, roadmap = result["career"], result["gaps"], result["roadmap"]

    ui.hero(profile["name"], career["name"], result["match"], result["readiness"],
            roadmap["total_weeks"], roadmap["weekly_hours"])
    met = sum(1 for g in gaps if g["status"] == "Met")
    ui.metric_strip([
        ("Career match", f"{result['match']:.0f}%", "weighted by skill importance"),
        ("Skills on target", f"{met} of {len(gaps)}", "including prerequisites"),
        ("Hours remaining", f"{roadmap['total_hours']}", f"{roadmap['pending_count']} steps left"),
        ("Roadmap progress", f"{roadmap['progress_pct']:.0f}%", f"{roadmap['completed_hours']} hours done"),
    ])

    tabs = st.tabs(["Overview", "Skill gaps", "Roadmap", "Recommendations", "Adaptive engine", "Progress"])
    with tabs[0]:
        _overview(profile, result)
    with tabs[1]:
        _skill_gaps(gaps)
    with tabs[2]:
        _roadmap(profile, result, db_path, fast_track)
    with tabs[3]:
        _recommendations(profile, result)
    with tabs[4]:
        _adaptive(result, db_path)
    with tabs[5]:
        _progress(profile, result, db_path)


# ------------------------------------------------------------------ charts
def _radar(gaps: list[dict]) -> go.Figure:
    core = sorted((g for g in gaps if g["source"] != "prerequisite"), key=lambda g: -g["importance"])[:10]
    labels = [g["skill"] for g in core]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[g["required"] for g in core] + [core[0]["required"]], theta=labels + [labels[0]],
        name="Required", line=dict(color=AMBER, width=3), fill="toself", fillcolor="rgba(245,183,0,0.15)"))
    fig.add_trace(go.Scatterpolar(
        r=[g["current"] for g in core] + [core[0]["current"]], theta=labels + [labels[0]],
        name="You today", line=dict(color=GREEN, width=3), fill="toself", fillcolor="rgba(14,90,69,0.25)"))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 3], tickvals=[1, 2, 3], ticktext=["Beg", "Int", "Adv"])),
        margin=dict(l=80, r=100, t=20, b=20), height=400, legend=dict(orientation="h", y=-0.08),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color=INK))
    return fig


def _gap_bars(gaps: list[dict]) -> go.Figure:
    rows = list(reversed(gaps))  # highest priority ends up on top
    fig = go.Figure()
    fig.add_trace(go.Bar(y=[g["skill"] for g in rows], x=[g["required"] for g in rows], orientation="h",
                         name="Required", marker_color=AMBER))
    fig.add_trace(go.Bar(y=[g["skill"] for g in rows], x=[g["current"] for g in rows], orientation="h",
                         name="You today", marker_color=GREEN))
    fig.update_layout(
        barmode="group", height=max(320, 34 * len(rows) + 90), margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(range=[0, 3.3], tickvals=[0, 1, 2, 3], ticktext=["None", "Beginner", "Intermediate", "Advanced"]),
        legend=dict(orientation="h", y=1.04), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK))
    return fig


# --------------------------------------------------------------------- tabs
def _overview(profile: dict, result: dict) -> None:
    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("Where you stand")
        core = [g for g in result["gaps"] if g["source"] != "prerequisite"]
        if len(core) >= 3:
            st.plotly_chart(_radar(result["gaps"]), key="chart_radar")
        else:
            st.plotly_chart(_gap_bars(result["gaps"]), key="chart_bars_overview")
        st.caption("Amber is what the role requires. Green is where you are today, including completed steps.")
    with right:
        st.subheader("Best-fit careers")
        target = result["career"]["name"]
        for c in result["career_ranking"][:3]:
            ui.career_card(c, c["name"] == target)
        if target not in [c["name"] for c in result["career_ranking"][:3]]:
            st.caption(f"Your target, {target}, is outside the top three by current fit. That is fine: fit changes as you learn.")
        st.subheader("Do this next")
        nxt = recommend_next_actions(result["roadmap"], 3)
        if not nxt:
            st.success("No steps left. You have closed every gap and finished the capstone.")
        for item in nxt:
            with st.container(border=True):
                st.markdown(ui.stop_html(item, TYPE_LABEL[item["type"]]), unsafe_allow_html=True)
                st.caption(item["why"])


def _skill_gaps(gaps: list[dict]) -> None:
    st.subheader("Current level against what the role requires")
    st.plotly_chart(_gap_bars(gaps), key="chart_bars_gaps")
    unmet = [g for g in gaps if g["status"] != "Met"]
    st.subheader(f"Gaps to close ({len(unmet)})")
    if not unmet:
        st.success("Every required skill is at the target level.")
    for g in unmet:
        title = f"#{g['rank']}  {g['skill']}  |  {g['status']}  |  {g['priority']} priority"
        with st.expander(title):
            st.markdown(
                f"{ui.badge(g['status'])} &nbsp; Needs **{data.LEVELS[g['required']]}**, you are at "
                f"**{describe_level(g['current'])}**. Priority score {g['score']}.",
                unsafe_allow_html=True,
            )
            st.write(g["reason"])
    met = [g for g in gaps if g["status"] == "Met"]
    if met:
        with st.expander(f"Skills you already meet ({len(met)})"):
            for g in met:
                st.write(f"**{g['skill']}**: {g['reason']}")


def _roadmap(profile: dict, result: dict, db_path: str | None, fast_track: bool) -> None:
    roadmap = result["roadmap"]
    st.subheader("Your personalised roadmap")
    st.write(
        f"{roadmap['pending_count']} steps, {roadmap['total_hours']} hours, about {roadmap['total_weeks']} weeks "
        f"at {roadmap['weekly_hours']} hours a week."
        + (" Fast-track mode is on, so optional practice steps for lower-priority skills are hidden." if fast_track else "")
    )
    if not roadmap["phases"]:
        st.success("Roadmap complete. Update your target role or add a requirement to keep growing.")
    for phase in roadmap["phases"]:
        ui.plate(phase["name"], phase["description"])
        for item in phase["items"]:
            with st.container(border=True):
                a, b = st.columns([5, 1.3])
                with a:
                    st.markdown(ui.stop_html(item, TYPE_LABEL[item["type"]]), unsafe_allow_html=True)
                    st.caption(f"Why: {item['why']}")
                with b:
                    if st.button("Mark complete", key=f"done_{item['id']}"):
                        complete_activity(profile, item["id"], db_path, fast_track)
                        st.rerun()
    if roadmap["completed_items"]:
        with st.expander(f"Completed steps ({len(roadmap['completed_items'])})"):
            for item in roadmap["completed_items"]:
                a, b = st.columns([5, 1.3])
                a.write(f"{item['title']} ({item['skill']}, {item['hours']} h)")
                if b.button("Undo", key=f"undo_{item['id']}"):
                    undo_activity(profile, item["id"], db_path, fast_track)
                    st.rerun()


def _recommendations(profile: dict, result: dict) -> None:
    roadmap, career = result["roadmap"], result["career"]
    st.subheader("Start here")
    nxt = recommend_next_actions(roadmap, 3)
    if not nxt:
        st.info("Nothing pending. Consider the certifications below.")
    for item in nxt:
        with st.container(border=True):
            st.markdown(ui.stop_html(item, TYPE_LABEL[item["type"]]), unsafe_allow_html=True)
            st.write(item["why"])

    st.subheader("Everything on your roadmap, by type")
    grouped = group_by_type(roadmap)
    cols = st.columns(4)
    for col, (rtype, items) in zip(cols, grouped.items()):
        with col:
            hours = sum(i["hours"] for i in items)
            st.markdown(f"**{TYPE_LABEL[rtype]}s** ({len(items)}, {hours} h)")
            for i in items[:8]:
                st.caption(f"{i['title']} ({i['skill']})")
            if len(items) > 8:
                st.caption(f"and {len(items) - 8} more")

    if career.get("certifications"):
        st.subheader("Certifications employers ask for")
        for cert in career["certifications"]:
            st.write(f"- {cert}")
        st.caption("Check each provider for current exam details before you commit.")


def _adaptive(result: dict, db_path: str | None) -> None:
    career = result["career"]["name"]
    st.subheader("How your plan has adapted")
    for n in result["notes"]:
        ui.note(n["kind"], n["text"])

    st.toggle("Fast-track mode: hide optional practice steps for lower-priority skills", key="fast_track")

    st.subheader("Change the role's requirements")
    st.write(
        "Job requirements shift over time. Add or raise a requirement and the gaps, priorities and "
        "roadmap are recalculated straight away."
    )
    presets = [p for p in data.MARKET_PRESETS if p["career"] == career]
    for p in presets:
        label = f"Apply example: {p['skill']} at {data.LEVELS[p['required']]} level"
        if st.button(label, key=f"preset_{p['skill']}"):
            database.add_market_update(career, p["skill"], p["importance"], p["required"], p["note"], db_path)
            st.rerun()

    c1, c2, c3 = st.columns(3)
    skill = c1.selectbox("Skill", list(data.SKILLS), key="mu_skill")
    importance = c2.slider("Importance", 1, 5, 4, key="mu_imp")
    required = c3.select_slider("Required level", [1, 2, 3], value=2, format_func=lambda x: data.LEVELS[x], key="mu_req")
    note = st.text_input("Reason (optional)", key="mu_note")
    if st.button("Apply requirement change", key="mu_apply"):
        database.add_market_update(career, skill, importance, required, note, db_path)
        st.rerun()

    if result["market_updates"]:
        st.markdown("**Active changes**")
        for u in result["market_updates"]:
            st.write(f"- {u['skill']}: {data.LEVELS[u['required']]}, importance {u['importance']}/5. {u['note']}")
        if st.button("Remove all changes for this role", key="mu_clear"):
            database.clear_market_updates(career, db_path)
            st.rerun()


def _progress(profile: dict, result: dict, db_path: str | None) -> None:
    roadmap = result["roadmap"]
    st.subheader("Career match over time")
    history = result["history"]
    if len(history) < 2:
        st.info("Complete a roadmap step and your match score will start plotting here.")
    else:
        values = [h["match_pct"] for h in history]
        lo, hi = max(0, min(values) - 10), min(100, max(values) + 10)
        fig = go.Figure(go.Scatter(
            x=list(range(len(history))), y=values, mode="lines+markers",
            line=dict(color=GREEN, width=3), marker=dict(color=AMBER, size=9, line=dict(color="white", width=2))))
        fig.update_layout(
            height=280, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(range=[lo, hi], title="Match %"),
            xaxis=dict(title="Change", dtick=1), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=INK))
        st.plotly_chart(fig, key="chart_history")

    st.subheader("Skill progress")
    st.caption("How much of each required level you have reached.")
    for g in sorted(result["gaps"], key=lambda g: (g["status"] == "Met", g["rank"] or 99)):
        pct = 100 * min(g["current"] / g["required"], 1)
        ui.skill_meter(g["skill"], pct, f"{pct:.0f}%")

    st.subheader("Save, export or reset")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Save profile", key="save_profile"):
            database.save_profile(profile, db_path)
            st.success("Profile saved. Load it later from the sidebar.")
    with c2:
        md = roadmap_to_markdown(profile, result["career"]["name"], result["match"], roadmap)
        st.download_button("Download roadmap", md, file_name="career_roadmap.md", mime="text/markdown")
    with c3:
        confirm = st.checkbox("Yes, reset my progress", key="confirm_reset")
        if st.button("Reset progress", key="reset_progress", disabled=not confirm):
            database.reset_progress(profile["name"], db_path)
            st.rerun()
