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
    placeholder="Example: Python, SQL, HTML, CSS"
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

        # Convert user's skills into a clean list
        user_skills = [
            skill.strip().lower()
            for skill in skills_input.split(",")
            if skill.strip()
        ]

        # Get required skills for selected career
        required_skills = CAREER_SKILLS[career]

        # Convert required skills to lowercase for comparison
        required_lower = [
            skill.lower()
            for skill in required_skills
        ]

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

        # Calculate skill match percentage
        total_required = len(required_skills)

        if total_required > 0:
            match_percentage = (
                len(matched_skills) / total_required
            ) * 100
        else:
            match_percentage = 0

        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------

        st.divider()

        st.header("📊 Career Analysis")

        st.success(
            f"Hello {name}! Your target career is **{career}**."
        )

        # Match percentage
        st.metric(
            "Career Skill Match",
            f"{match_percentage:.0f}%"
        )

        # -------------------------------------------------
        # STRONG SKILLS
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
        # PERSONALIZED ROADMAP
        # -------------------------------------------------

        st.subheader("🗺️ Personalized Learning Roadmap")

        if missing_skills:

            for index, skill in enumerate(
                missing_skills,
                start=1
            ):

                st.write(
                    f"**Step {index}:** Learn and practice **{skill}**"
                )

        else:

            st.success(
                "You are ready to move toward advanced projects "
                "and industry preparation."
            )

        # -------------------------------------------------
        # RECOMMENDATIONS
        # -------------------------------------------------

        st.subheader("💡 Recommended Next Actions")

        if missing_skills:

            st.write("📚 Learn the missing skills.")
            st.write("💻 Build projects using those skills.")
            st.write("📂 Add completed projects to GitHub.")
            st.write("🧪 Practice through practical assessments.")
            st.write("📈 Update your profile as you improve.")

        else:

            st.write("💻 Build advanced real-world projects.")
            st.write("📂 Strengthen your GitHub portfolio.")
            st.write("🏆 Consider relevant certifications.")
            st.write("🎯 Prepare for industry roles.")

        # -------------------------------------------------
        # EXPLANATION
        # -------------------------------------------------

        st.subheader("💡 Why these recommendations?")

        st.write(
            f"The roadmap is based on the skills required for "
            f"**{career}** and the skills you entered in your "
            f"current profile. Missing skills are prioritized "
            f"as learning areas."
        )
