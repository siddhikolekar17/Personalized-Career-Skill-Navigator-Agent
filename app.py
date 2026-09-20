import streamlit as st

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Career & Skill Navigator",
    page_icon="🎯",
    layout="wide"
)

# ---------------------------------------------------------
# CAREER SKILL DATABASE
# ---------------------------------------------------------

CAREER_SKILLS = {
    "AI/ML Engineer": [
        "Python",
        "NumPy",
        "Pandas",
        "Statistics",
        "Machine Learning",
        "Deep Learning",
        "SQL",
        "Git/GitHub"
    ],

    "Data Scientist": [
        "Python",
        "NumPy",
        "Pandas",
        "Statistics",
        "Machine Learning",
        "SQL",
        "Data Visualization",
        "Git/GitHub"
    ],

    "Web Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Python",
        "SQL",
        "Git/GitHub"
    ],

    "Data Analyst": [
        "Python",
        "SQL",
        "Excel",
        "Statistics",
        "Pandas",
        "Data Visualization",
        "Power BI",
        "Git/GitHub"
    ]
}

# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------

st.title("🎯 Personalized Career & Skill Navigator Agent")

st.write(
    "AI-powered personalized career and skill roadmap navigator"
)

st.divider()

# ---------------------------------------------------------
# STUDENT PROFILE
# ---------------------------------------------------------

st.header("👤 Student Profile")

name = st.text_input(
    "Your Name",
    placeholder="Enter your name"
)

education = st.text_input(
    "Education",
    placeholder="Example: B.Tech Computer Science - 2nd Year"
)

skills_input = st.text_area(
    "Current Skills",
    placeholder="Example: Python, SQL, HTML"
)

career = st.selectbox(
    "Target Career",
    list(CAREER_SKILLS.keys())
)

# ---------------------------------------------------------
# ANALYZE BUTTON
# ---------------------------------------------------------

if st.button("🚀 Analyze My Career", use_container_width=True):

    if not name:
        st.warning("Please enter your name.")

    elif not skills_input:
        st.warning("Please enter your current skills.")

    else:

        # -------------------------------------------------
        # CONVERT USER SKILLS
        # -------------------------------------------------

        user_skills = [
            skill.strip().lower()
            for skill in skills_input.split(",")
            if skill.strip()
        ]

        # Required skills for selected career
        required_skills = CAREER_SKILLS[career]

        # -------------------------------------------------
        # SKILL GAP ANALYSIS
        # -------------------------------------------------

        matched_skills = []
        missing_skills = []

        for skill in required_skills:

            if skill.lower() in user_skills:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        # -------------------------------------------------
        # CAREER MATCH
        # -------------------------------------------------

        total_required = len(required_skills)

        match_percentage = (
            len(matched_skills) / total_required
        ) * 100

        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------

        st.divider()

        st.header("📊 Career Analysis")

        st.success(
            f"Hello {name}! Your target career is **{career}**."
        )

        st.metric(
            "Career Skill Match",
            f"{match_percentage:.0f}%"
        )

        # -------------------------------------------------
        # MATCHING SKILLS
        # -------------------------------------------------

        st.subheader("✅ Your Matching Skills")

        if matched_skills:

            for skill in matched_skills:
                st.write(f"✅ {skill}")

        else:
            st.write("No matching skills found yet.")

        # -------------------------------------------------
        # SKILL GAPS
        # -------------------------------------------------

        st.subheader("❌ Your Skill Gaps")

        if missing_skills:

            for skill in missing_skills:
                st.write(f"❌ {skill}")

        else:

            st.success(
                "Excellent! You have all the required skills."
            )

        # -------------------------------------------------
        # REQUIRED SKILLS
        # -------------------------------------------------

        st.subheader("🎯 Skills Required for Your Career")

        for skill in required_skills:
            st.write(f"• {skill}")

        # -------------------------------------------------
        # PROGRESS TRACKING
        # -------------------------------------------------

        st.divider()

        st.header("📈 Skill Progress Tracking")

        st.write(
            "Mark the skills you have completed to update your "
            "personalized career progress."
        )

        completed_skills = []

        # Create checkbox for every required skill
        for skill in required_skills:

            # Already matching skills are automatically completed
            default_value = skill in matched_skills

            completed = st.checkbox(
                skill,
                value=default_value,
                key=f"progress_{skill}"
            )

            if completed:
                completed_skills.append(skill)

        # -------------------------------------------------
        # CALCULATE OVERALL PROGRESS
        # -------------------------------------------------

        completed_count = len(completed_skills)

        total_skills = len(required_skills)

        progress_percentage = (
            completed_count / total_skills
        ) * 100

        st.subheader("🎯 Overall Career Progress")

        st.progress(
            progress_percentage / 100
        )

        st.metric(
            "Overall Progress",
            f"{progress_percentage:.0f}%"
        )

        st.write(
            f"**{completed_count} / {total_skills} skills completed**"
        )

        # -------------------------------------------------
        # CURRENT STATUS
        # -------------------------------------------------

        st.subheader("📋 Skill Status")

        for skill in required_skills:

            if skill in completed_skills:

                st.write(f"✅ **{skill}** — Completed")

            else:

                st.write(f"⬜ **{skill}** — Not Completed")

        # -------------------------------------------------
# ADAPTIVE ROADMAP
# -------------------------------------------------

st.subheader("🗺️ Adaptive Learning Roadmap")

# Skills that are still incomplete
remaining_skills = [
    skill
    for skill in required_skills
    if skill not in completed_skills
]

if remaining_skills:

    # The first incomplete skill becomes the next priority
    next_skill = remaining_skills[0]

    st.info(
        f"🤖 **Agent Recommendation:** "
        f"Your next priority should be **{next_skill}**."
    )

    st.write(
        "The roadmap automatically adapts based on your "
        "completed skills."
    )

    st.divider()

    # Show adaptive roadmap
    for index, skill in enumerate(
        remaining_skills,
        start=1
    ):

        if index == 1:

            st.write(
                f"🔥 **NEXT:** {skill}"
            )

        else:

            st.write(
                f"➡️ **Step {index}:** {skill}"
            )

else:

    st.success(
    f"🎯 Because you completed previous skills, "
    f"the agent has updated your roadmap. "
    f"Your next recommended skill is **{next_skill}**."
)

    st.write(
        "Your next step is to build advanced projects "
        "and prepare for industry roles."
    )
        # -------------------------------------------------
        # RECOMMENDED NEXT ACTIONS
        # -------------------------------------------------

        st.subheader("💡 Recommended Next Actions")

        if remaining_skills:

            next_skill = remaining_skills[0]

            st.write(
                f"🎯 **Priority:** Start with **{next_skill}**"
            )

            st.write(
                "📚 Learn the recommended skill."
            )

            st.write(
                "💻 Build a practical project."
            )

            st.write(
                "📂 Add the project to GitHub."
            )

            st.write(
                "🧪 Practice with real-world problems."
            )

            st.write(
                "📈 Update your progress after completing the skill."
            )

        else:

            st.write(
                "💻 Build advanced real-world projects."
            )

            st.write(
                "📂 Strengthen your GitHub portfolio."
            )

            st.write(
                "🏆 Consider relevant certifications."
            )

        # -------------------------------------------------
        # EXPLANATION
        # -------------------------------------------------

        st.subheader("💡 Why these recommendations?")

        if remaining_skills:

            next_skill = remaining_skills[0]

            st.write(
                f"Your roadmap adapts to your completed skills. "
                f"Since **{next_skill}** is still incomplete, "
                f"it is currently prioritized as your next learning goal."
            )

        else:

            st.write(
                f"You have completed the required skills for "
                f"**{career}**. The system therefore recommends "
                f"advanced projects and career preparation."
            )
