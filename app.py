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
# SKILL RECOMMENDATIONS
# ---------------------------------------------------------

SKILL_RECOMMENDATIONS = {

    "Python": {
        "learn": "Python programming fundamentals",
        "practice": "Python coding exercises and problem solving",
        "project": "Python Automation Project"
    },

    "NumPy": {
        "learn": "Beginner NumPy course",
        "practice": "Array manipulation exercises",
        "project": "Student Marks Analysis"
    },

    "Pandas": {
        "learn": "Beginner Pandas and DataFrame course",
        "practice": "CSV data cleaning and analysis",
        "project": "Student Performance Dashboard"
    },

    "Statistics": {
        "learn": "Basic Statistics for Data Science",
        "practice": "Mean, median, probability and correlation exercises",
        "project": "Student Performance Statistical Analysis"
    },

    "Machine Learning": {
        "learn": "Machine Learning fundamentals course",
        "practice": "Classification and regression exercises",
        "project": "Student Performance Prediction"
    },

    "Deep Learning": {
        "learn": "Deep Learning fundamentals course",
        "practice": "Neural network practice exercises",
        "project": "Image Classification Project"
    },

    "SQL": {
        "learn": "SQL fundamentals course",
        "practice": "SQL queries and database exercises",
        "project": "Student Database Management System"
    },

    "Git/GitHub": {
        "learn": "Git and GitHub beginner course",
        "practice": "Create repositories and practice commits",
        "project": "Build and publish a portfolio project"
    },

    "HTML": {
        "learn": "HTML fundamentals",
        "practice": "Build structured web pages",
        "project": "Personal Portfolio Website"
    },

    "CSS": {
        "learn": "CSS fundamentals",
        "practice": "Responsive styling exercises",
        "project": "Responsive Portfolio Website"
    },

    "JavaScript": {
        "learn": "JavaScript fundamentals",
        "practice": "DOM and JavaScript exercises",
        "project": "Interactive Web Application"
    },

    "React": {
        "learn": "React fundamentals",
        "practice": "Components, props and state exercises",
        "project": "React Dashboard"
    },

    "Data Visualization": {
        "learn": "Data Visualization fundamentals",
        "practice": "Create charts from datasets",
        "project": "Interactive Data Dashboard"
    },

    "Excel": {
        "learn": "Excel for Data Analysis",
        "practice": "Formulas, pivot tables and charts",
        "project": "Student Performance Excel Dashboard"
    },

    "Power BI": {
        "learn": "Power BI fundamentals",
        "practice": "Build interactive dashboards",
        "project": "Business Analytics Dashboard"
    }
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

if st.button(
    "🚀 Analyze My Career",
    use_container_width=True
):

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

        # -------------------------------------------------
        # REQUIRED SKILLS
        # -------------------------------------------------

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
        # CAREER ANALYSIS
        # -------------------------------------------------

        st.divider()

        st.header("📊 Career Analysis")

        st.success(
            f"Hello {name}! "
            f"Your target career is **{career}**."
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

                st.write(
                    f"✅ {skill}"
                )

        else:

            st.write(
                "No matching skills found yet."
            )

        # -------------------------------------------------
        # SKILL GAPS
        # -------------------------------------------------

        st.subheader("❌ Your Skill Gaps")

        if missing_skills:

            for skill in missing_skills:

                st.write(
                    f"❌ {skill}"
                )

        else:

            st.success(
                "Excellent! You have all the required skills."
            )

        # -------------------------------------------------
        # REQUIRED SKILLS
        # -------------------------------------------------

        st.subheader(
            "🎯 Skills Required for Your Career"
        )

        for skill in required_skills:

            st.write(
                f"• {skill}"
            )

        # -------------------------------------------------
        # PROGRESS TRACKING
        # -------------------------------------------------

        st.divider()

        st.header(
            "📈 Skill Progress Tracking"
        )

        st.write(
            "Mark the skills you have completed "
            "to update your career progress."
        )

        completed_skills = []

        # -------------------------------------------------
        # SKILL CHECKBOXES
        # -------------------------------------------------

        for skill in required_skills:

            # Existing skills are automatically completed
            default_value = (
                skill in matched_skills
            )

            completed = st.checkbox(
                skill,
                value=default_value,
                key=f"progress_{career}_{skill}"
            )

            if completed:

                completed_skills.append(skill)

        # -------------------------------------------------
        # OVERALL PROGRESS
        # -------------------------------------------------

        completed_count = len(
            completed_skills
        )

        total_skills = len(
            required_skills
        )

        progress_percentage = (
            completed_count / total_skills
        ) * 100

        st.subheader(
            "🎯 Overall Career Progress"
        )

        st.progress(
            progress_percentage / 100
        )

        st.metric(
            "Overall Progress",
            f"{progress_percentage:.0f}%"
        )

        st.write(
            f"**{completed_count} / "
            f"{total_skills} skills completed**"
        )

        # -------------------------------------------------
        # SKILL STATUS
        # -------------------------------------------------

        st.subheader(
            "📋 Skill Status"
        )

        for skill in required_skills:

            if skill in completed_skills:

                st.write(
                    f"✅ **{skill}** — Completed"
                )

            else:

                st.write(
                    f"⬜ **{skill}** — Not Completed"
                )

        # -------------------------------------------------
        # ADAPTIVE ROADMAP
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "🗺️ Adaptive Learning Roadmap"
        )

        # Find incomplete skills
        remaining_skills = [
            skill
            for skill in required_skills
            if skill not in completed_skills
        ]

        # -------------------------------------------------
        # ADAPTIVE RECOMMENDATION
        # -------------------------------------------------

        if remaining_skills:

            # First incomplete skill is the next priority
            next_skill = remaining_skills[0]

            st.info(
                f"🤖 **Agent Recommendation:** "
                f"Your next priority should be "
                f"**{next_skill}**."
            )

            st.write(
                "The roadmap automatically adapts "
                "based on your completed skills."
            )

            st.write(
                "### 📚 Updated Roadmap"
            )

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
                "🎉 You have completed all required skills!"
            )

            st.write(
                "Your next step is to build advanced "
                "projects and prepare for industry roles."
            )

        # -------------------------------------------------
        # STEP 3
        # PERSONALIZED SKILL RECOMMENDATIONS
        # -------------------------------------------------

        st.divider()

        st.header(
            "📚 Personalized Skill Recommendations"
        )

        if remaining_skills:

            st.write(
                "Based on your current skill gaps, "
                "here are personalized learning "
                "recommendations:"
            )

            # Show recommendations only for missing skills
            for skill in remaining_skills:

                if skill in SKILL_RECOMMENDATIONS:

                    recommendation = (
                        SKILL_RECOMMENDATIONS[skill]
                    )

                    st.subheader(
                        f"📚 {skill}"
                    )

                    st.write(
                        f"**Learn →** "
                        f"{recommendation['learn']}"
                    )

                    st.write(
                        f"**Practice →** "
                        f"{recommendation['practice']}"
                    )

                    st.write(
                        f"**Project →** "
                        f"{recommendation['project']}"
                    )

                    st.divider()

                else:

                    st.write(
                        f"📚 **{skill}**"
                    )

                    st.write(
                        "Learn the fundamentals, "
                        "practice with exercises, "
                        "and build a small project."
                    )

        else:

            st.success(
                "🎉 You have completed all required skills. "
                "Start building advanced projects!"
            )

        # -------------------------------------------------
        # RECOMMENDED NEXT ACTIONS
        # -------------------------------------------------

        st.header(
            "💡 Recommended Next Actions"
        )

        if remaining_skills:

            next_skill = remaining_skills[0]

            st.write(
                f"🎯 **Priority:** Start with "
                f"**{next_skill}**"
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
                "📈 Update your progress after "
                "completing the skill."
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

        st.subheader(
            "💡 Why these recommendations?"
        )

        if remaining_skills:

            next_skill = remaining_skills[0]

            st.write(
                f"Your roadmap adapts to your completed "
                f"skills. Since **{next_skill}** is still "
                f"incomplete, it is currently prioritized "
                f"as your next learning goal."
            )

        else:

            st.write(
                f"You have completed the required skills "
                f"for **{career}**. The system therefore "
                f"recommends advanced projects and "
                f"career preparation."
            )
