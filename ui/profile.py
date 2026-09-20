"""Profile and goal page: education, skills, interests, target career, preferences."""
from __future__ import annotations

import streamlit as st

from backend import data
from backend.career_engine import extract_skills_from_text

CUSTOM_OPTION = "Define my own role"


def _level_name(level: int) -> str:
    return data.LEVELS[level]


def render_profile_page() -> dict | None:
    """Draw the form. Returns a profile dict when the user clicks Analyze, else None."""
    v = st.session_state.get("form_version", 0)  # bumping this resets every widget
    saved: dict = st.session_state.get("profile") or {}

    st.title("Your profile and goal")
    st.write("Tell us where you are and where you want to go. Everything here can be changed later.")

    # ---- About you --------------------------------------------------------
    st.subheader("About you")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Name", value=saved.get("name", ""), key=f"pf_name_{v}", placeholder="e.g. Asha")
    stage = c2.selectbox(
        "Current stage", data.STAGES,
        index=data.STAGES.index(saved.get("stage", data.STAGES[0])), key=f"pf_stage_{v}",
    )
    experience = c3.number_input(
        "Years of work experience", min_value=0.0, max_value=40.0, step=0.5,
        value=float(saved.get("experience_years", 0.0)), key=f"pf_exp_{v}",
    )
    c4, c5 = st.columns(2)
    education = c4.selectbox(
        "Highest education", data.EDUCATION_LEVELS,
        index=data.EDUCATION_LEVELS.index(saved.get("education", data.EDUCATION_LEVELS[2])), key=f"pf_edu_{v}",
    )
    field = c5.text_input("Field of study", value=saved.get("field", ""), key=f"pf_field_{v}", placeholder="e.g. Computer Science")

    interests = st.multiselect(
        "Areas you are interested in", data.INTEREST_OPTIONS,
        default=[i for i in saved.get("interests", []) if i in data.INTEREST_OPTIONS], key=f"pf_int_{v}",
    )

    # ---- Current skills -----------------------------------------------------
    st.subheader("Your current skills")
    skills_key = f"pf_skills_{v}"
    st.session_state.setdefault(skills_key, [s for s in saved.get("skills", {}) if s in data.SKILLS])

    pasted = st.text_area(
        "Paste your resume or a short bio to detect skills (optional)", key=f"pf_text_{v}", height=90,
        placeholder="e.g. Built a churn model in Python with pandas and scikit-learn, queried MySQL, used Git...",
    )
    if st.button("Detect skills from text", key=f"pf_detect_{v}"):
        detected = extract_skills_from_text(pasted)
        if detected:
            st.session_state[skills_key] = sorted(set(st.session_state[skills_key]) | set(detected))
            st.success(f"Added {len(detected)} skill(s). Review the levels below.")
        else:
            st.warning("No known skills found in that text. Pick them from the list instead.")

    selected = st.multiselect("Skills you already have", list(data.SKILLS), key=skills_key)
    levels: dict[str, int] = {}
    if selected:
        st.caption("Rate yourself honestly. The gap analysis is only as accurate as these ratings.")
        cols = st.columns(3)
        for i, skill in enumerate(selected):
            key = f"lvl_{v}_{skill}"
            st.session_state.setdefault(key, saved.get("skills", {}).get(skill, 1))
            with cols[i % 3]:
                levels[skill] = st.select_slider(skill, options=[1, 2, 3], format_func=_level_name, key=key)

    # ---- Career goal --------------------------------------------------------
    st.subheader("Your target role")
    options = list(data.CAREERS) + [CUSTOM_OPTION]
    saved_custom = saved.get("custom_career")
    default_target = saved.get("target_career", options[0])
    if saved_custom and default_target == saved_custom.get("name"):
        default_target = CUSTOM_OPTION
    choice = st.selectbox(
        "Choose a career", options,
        index=options.index(default_target) if default_target in options else 0, key=f"pf_career_{v}",
    )

    custom_career = None
    if choice == CUSTOM_OPTION:
        role_name = st.text_input(
            "Role name", value=(saved_custom or {}).get("name", ""), key=f"cc_name_{v}", placeholder="e.g. Bioinformatics Analyst"
        )
        req_skills = st.multiselect(
            "Skills this role needs", list(data.SKILLS),
            default=list((saved_custom or {}).get("requirements", {})), key=f"cc_skills_{v}",
        )
        requirements = {}
        cols = st.columns(2)
        for i, skill in enumerate(req_skills):
            prev = (saved_custom or {}).get("requirements", {}).get(skill, {})
            with cols[i % 2]:
                st.markdown(f"**{skill}**")
                level = st.select_slider(
                    "Required level", [1, 2, 3], value=prev.get("required", 2),
                    format_func=_level_name, key=f"cc_lvl_{v}_{skill}",
                )
                importance = st.slider("Importance", 1, 5, prev.get("importance", 4), key=f"cc_imp_{v}_{skill}")
            requirements[skill] = {"required": level, "importance": importance}
        if role_name.strip() and requirements:
            custom_career = {"name": role_name.strip(), "requirements": requirements}
    else:
        info = data.CAREERS[choice]
        st.write(info["description"])
        chips = ", ".join(f"{s} ({_level_name(r)})" for s, (_, r) in info["requirements"].items())
        st.caption(f"Core skills: {chips}")

    # ---- Preferences --------------------------------------------------------
    st.subheader("How you like to learn")
    p1, p2 = st.columns(2)
    weekly_hours = p1.slider(
        "Hours you can study each week", 2, 40, int(saved.get("weekly_hours", 8)), key=f"pf_hours_{v}"
    )
    style = p2.selectbox(
        "Preferred learning style", data.LEARNING_STYLES,
        index=data.LEARNING_STYLES.index(saved.get("learning_style", data.LEARNING_STYLES[0])), key=f"pf_style_{v}",
    )

    # ---- Submit ---------------------------------------------------------------
    if st.button("Analyze career", type="primary", key=f"pf_go_{v}"):
        if not name.strip():
            st.error("Enter your name so your progress can be saved.")
            return None
        if choice == CUSTOM_OPTION and custom_career is None:
            st.error("Name your role and pick at least one skill it needs.")
            return None
        return {
            "name": name.strip(),
            "stage": stage,
            "experience_years": experience,
            "education": education,
            "field": field.strip(),
            "interests": interests,
            "skills": levels,
            "target_career": custom_career["name"] if custom_career else choice,
            "custom_career": custom_career,
            "weekly_hours": weekly_hours,
            "learning_style": style,
        }
    return None
