import os
import streamlit as st

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Career & Skill Navigator",
    page_icon="🎯",
    layout="wide"
)

# =========================================================
# CAREER SKILL DATABASE
# =========================================================

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

# =========================================================
# SKILL RECOMMENDATIONS
# =========================================================

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

# =========================================================
# SESSION STATE
# =========================================================

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

# =========================================================
# HELPER: GET API KEY
# =========================================================

def get_openai_api_key():
    """Get OpenAI API key securely from Streamlit Secrets."""

    try:
        api_key = st.secrets.get("OPENAI_API_KEY")

        if api_key:
            return api_key

    except Exception:
        pass

    return os.getenv("OPENAI_API_KEY")


# =========================================================
# FALLBACK AI RESPONSE
# =========================================================

def create_fallback_response(
    name,
    target_career,
    remaining_skills,
    progress_percentage
):
    """Built-in fallback if the AI API is unavailable."""

    if remaining_skills:

        priority = remaining_skills[0]

        roadmap_lines = []

        projects = []

        for index, skill in enumerate(
            remaining_skills,
            start=1
        ):

            recommendation = SKILL_RECOMMENDATIONS.get(
                skill,
                {
                    "learn": f"Learn {skill} fundamentals",
                    "practice": f"Practice {skill} with exercises",
                    "project": f"Build a project using {skill}"
                }
            )

            roadmap_lines.append(
                f"{index}. **{skill}** — "
                f"Learn: {recommendation['learn']} | "
                f"Practice: {recommendation['practice']} | "
                f"Project: {recommendation['project']}"
            )

            if len(projects) < 3:
                projects.append(
                    recommendation["project"]
                )

        return {
            "analysis": (
                f"{name}, you currently have "
                f"{progress_percentage:.0f}% of the skills "
                f"mapped for the {target_career} career path. "
                f"Your next learning priority is "
                f"**{priority}** because it is the first "
                f"remaining skill in the recommended learning sequence."
            ),

            "priority": priority,

            "roadmap": "\n\n".join(
                roadmap_lines
            ),

            "projects": projects,

            "adaptation": (
                "The roadmap adapts whenever your progress "
                "changes. Completed skills are removed from "
                "the active learning path and the next "
                "remaining skill becomes the priority."
            ),

            "career_advice": (
                "Complete the priority skill, practice it "
                "with a small project, publish the project "
                "to GitHub, and then update your progress."
            )
        }

    return {
        "analysis": (
            f"Congratulations {name}! You have completed "
            f"the currently mapped skills for "
            f"{target_career}."
        ),

        "priority": "Advanced Projects",

        "roadmap": (
            "1. Build an advanced end-to-end project\n\n"
            "2. Strengthen your GitHub portfolio\n\n"
            "3. Practice real-world problems\n\n"
            "4. Prepare for technical interviews"
        ),

        "projects": [
            "End-to-end portfolio project",
            "Real-world AI application",
            "Open-source contribution"
        ],

        "adaptation": (
            "Because the currently required skills are "
            "completed, the roadmap shifts from basic "
            "skill acquisition toward advanced projects, "
            "portfolio development and career preparation."
        ),

        "career_advice": (
            "Focus on projects that demonstrate practical "
            "problem solving and publish your work on GitHub."
        )
    }


# =========================================================
# AI CAREER PERSONALIZATION AGENT
# =========================================================

def generate_ai_personalization(
    name,
    education,
    current_skills,
    target_career,
    matched_skills,
    missing_skills,
    completed_skills,
    remaining_skills,
    progress_percentage
):
    """Generate personalized career guidance using OpenAI."""

    fallback = create_fallback_response(
        name,
        target_career,
        remaining_skills,
        progress_percentage
    )

    api_key = get_openai_api_key()

    if not api_key:

        fallback["analysis"] += (
            "\n\nAI API key was not detected. "
            "The built-in recommendation engine is being used."
        )

        return fallback

    try:

        from openai import OpenAI

        client = OpenAI(
            api_key=api_key
        )

        prompt = f"""
You are an AI Career and Skill Navigator Agent.

Create a personalized career roadmap for a student.

STUDENT PROFILE
Name: {name}
Education: {education}
Current Skills: {current_skills}

TARGET CAREER
{target_career}

MATCHING SKILLS
{", ".join(matched_skills) if matched_skills else "None"}

MISSING SKILLS
{", ".join(missing_skills) if missing_skills else "None"}

COMPLETED SKILLS
{", ".join(completed_skills) if completed_skills else "None"}

REMAINING SKILLS
{", ".join(remaining_skills) if remaining_skills else "None"}

CURRENT PROGRESS
{progress_percentage:.0f}%

TASK

Analyze the student's current position and create a practical
career plan.

Return these sections:

CAREER ANALYSIS
Explain the student's current position.

NEXT PRIORITY
Identify the most useful remaining skill.

PERSONALIZED ROADMAP
Give a logical learning sequence.

PROJECT RECOMMENDATIONS
Suggest practical student-level projects.

ADAPTIVE STRATEGY
Explain how the roadmap should change when the student
completes skills.

CAREER ADVICE
Give practical next actions.

Keep the answer concise and suitable for a student dashboard.

Do not invent statistics, certificates, companies, job offers,
or guaranteed career outcomes.
"""

        response = client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )

        ai_text = response.output_text

        if not ai_text:
            return fallback

        return {
            "analysis": ai_text,

            "priority": (
                remaining_skills[0]
                if remaining_skills
                else "Advanced Projects"
            ),

            "roadmap": "",

            "projects": [],

            "adaptation": (
                "The AI agent generated this guidance using "
                "the student's profile, target career, "
                "skill gaps and progress."
            ),

            "career_advice": (
                "Continue updating your skill progress so "
                "the agent can adapt future recommendations."
            )
        }

    except Exception as e:

        fallback["analysis"] += (
            "\n\n⚠️ The AI service could not be reached, "
            "so the built-in career recommendation engine "
            "is being used."
        )

        # Store only a safe diagnostic message.
        fallback["error"] = str(e)[:300]

        return fallback


# =========================================================
# PAGE TITLE
# =========================================================

st.title(
    "🎯 Personalized Career & Skill Navigator Agent"
)

st.write(
    "AI-powered personalized career and skill roadmap navigator"
)

st.divider()


# =========================================================
# STUDENT PROFILE
# =========================================================

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


# =========================================================
# ANALYZE CAREER BUTTON
# =========================================================

if st.button(
    "🚀 Analyze My Career",
    use_container_width=True
):

    if not name:

        st.warning(
            "Please enter your name."
        )

    elif not skills_input:

        st.warning(
            "Please enter your current skills."
        )

    else:

        user_skills = [
            skill.strip().lower()
            for skill in skills_input.split(",")
            if skill.strip()
        ]

        required_skills = CAREER_SKILLS[career]

        matched_skills = []

        missing_skills = []

        for skill in required_skills:

            if skill.lower() in user_skills:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        total_required = len(required_skills)

        match_percentage = (
            len(matched_skills)
            / total_required
        ) * 100

        # Reset progress when starting a new analysis.
        for skill in required_skills:
            key = f"progress_{career}_{skill}"

            if key in st.session_state:
                del st.session_state[key]

        # Save analysis in session state.
        st.session_state.analysis_data = {
            "name": name,
            "education": education,
            "skills_input": skills_input,
            "career": career,
            "required_skills": required_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_percentage": match_percentage
        }

        # Clear previous AI result.
        st.session_state.ai_result = None

        st.rerun()


# =========================================================
# DISPLAY ANALYSIS
# =========================================================

data = st.session_state.analysis_data

if data is not None:

    name = data["name"]
    education = data["education"]
    skills_input = data["skills_input"]
    career = data["career"]

    required_skills = data["required_skills"]
    matched_skills = data["matched_skills"]
    missing_skills = data["missing_skills"]
    match_percentage = data["match_percentage"]


    # =====================================================
    # CAREER ANALYSIS
    # =====================================================

    st.divider()

    st.header("📊 Career Analysis")

    st.success(
        f"Hello {name}! Your target career is **{career}**."
    )

    st.metric(
        "Career Skill Match",
        f"{match_percentage:.0f}%"
    )


    # =====================================================
    # MATCHING SKILLS
    # =====================================================

    st.subheader(
        "✅ Your Matching Skills"
    )

    if matched_skills:

        for skill in matched_skills:

            st.write(
                f"✅ {skill}"
            )

    else:

        st.write(
            "No matching skills found yet."
        )


    # =====================================================
    # SKILL GAPS
    # =====================================================

    st.subheader(
        "❌ Your Skill Gaps"
    )

    if missing_skills:

        for skill in missing_skills:

            st.write(
                f"❌ {skill}"
            )

    else:

        st.success(
            "Excellent! You have all the required skills."
        )


    # =====================================================
    # REQUIRED SKILLS
    # =====================================================

    st.subheader(
        "🎯 Skills Required for Your Career"
    )

    for skill in required_skills:

        st.write(
            f"• {skill}"
        )


    # =====================================================
    # PROGRESS TRACKING
    # =====================================================

    st.divider()

    st.header(
        "📈 Skill Progress Tracking"
    )

    st.write(
        "Mark the skills you have completed "
        "to update your career progress."
    )

    completed_skills = []

    for skill in required_skills:

        default_value = (
            skill in matched_skills
        )

        completed = st.checkbox(
            skill,
            value=default_value,
            key=f"progress_{career}_{skill}"
        )

        if completed:

            completed_skills.append(
                skill
            )


    # =====================================================
    # OVERALL PROGRESS
    # =====================================================

    completed_count = len(
        completed_skills
    )

    total_skills = len(
        required_skills
    )

    progress_percentage = (
        completed_count
        / total_skills
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


    # =====================================================
    # SKILL STATUS
    # =====================================================

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


    # =====================================================
    # REMAINING SKILLS
    # =====================================================

    remaining_skills = [
        skill
        for skill in required_skills
        if skill not in completed_skills
    ]


    # =====================================================
    # ADAPTIVE ROADMAP
    # =====================================================

    st.divider()

    st.subheader(
        "🗺️ Adaptive Learning Roadmap"
    )

    if remaining_skills:

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

        st.subheader(
            "📚 Updated Roadmap"
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


    # =====================================================
    # PERSONALIZED RECOMMENDATIONS
    # =====================================================

    st.divider()

    st.header(
        "📚 Personalized Skill Recommendations"
    )

    if remaining_skills:

        st.write(
            "Based on your current skill gaps, "
            "here are personalized learning recommendations:"
        )

        for skill in remaining_skills:

            recommendation = SKILL_RECOMMENDATIONS.get(
                skill,
                {
                    "learn": f"Learn {skill} fundamentals",
                    "practice": f"Practice {skill} with exercises",
                    "project": f"Build a project using {skill}"
                }
            )

            st.subheader(
                f"📚 {skill}"
            )

            st.write(
                f"**Learn →** {recommendation['learn']}"
            )

            st.write(
                f"**Practice →** {recommendation['practice']}"
            )

            st.write(
                f"**Project →** {recommendation['project']}"
            )

            st.divider()

    else:

        st.success(
            "🎉 You have completed all required skills. "
            "Start building advanced projects!"
        )


    # =====================================================
    # AI CAREER PERSONALIZATION AGENT
    # =====================================================

    st.divider()

    st.header(
        "🤖 AI Career Personalization Agent"
    )

    st.write(
        "The AI agent analyzes your profile, "
        "career goal, skill gaps and progress "
        "to generate a personalized roadmap."
    )


    # =====================================================
    # AI GENERATION BUTTON
    # =====================================================

    if st.button(
        "✨ Generate My AI Career Roadmap",
        use_container_width=True
    ):

        with st.spinner(
            "🤖 AI Agent is analyzing your career profile..."
        ):

            st.session_state.ai_result = (
                generate_ai_personalization(
                    name=name,
                    education=education,
                    current_skills=skills_input,
                    target_career=career,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    completed_skills=completed_skills,
                    remaining_skills=remaining_skills,
                    progress_percentage=progress_percentage
                )
            )

        st.rerun()


    # =====================================================
    # DISPLAY AI RESULT
    # =====================================================

    ai_result = st.session_state.ai_result

    if ai_result is not None:

        st.success(
            "🤖 AI Career Analysis Generated"
        )

        # -------------------------------------------------
        # AI ANALYSIS
        # -------------------------------------------------

        st.subheader(
            "🧠 Personalized Career Analysis"
        )

        st.write(
            ai_result["analysis"]
        )


        # -------------------------------------------------
        # AI PRIORITY
        # -------------------------------------------------

        st.subheader(
            "🎯 AI Recommended Next Priority"
        )

        st.info(
            f"Focus next on: "
            f"**{ai_result['priority']}**"
        )


        # -------------------------------------------------
        # AI ROADMAP
        # -------------------------------------------------

        if ai_result.get("roadmap"):

            st.subheader(
                "🗺️ AI Personalized Roadmap"
            )

            st.write(
                ai_result["roadmap"]
            )


        # -------------------------------------------------
        # AI PROJECTS
        # -------------------------------------------------

        if ai_result.get("projects"):

            st.subheader(
                "💻 AI Recommended Projects"
            )

            for project in ai_result["projects"]:

                st.write(
                    f"🚀 {project}"
                )


        # -------------------------------------------------
        # AI ADAPTIVE STRATEGY
        # -------------------------------------------------

        st.subheader(
            "🔄 Adaptive AI Strategy"
        )

        st.write(
            ai_result["adaptation"]
        )


        # -------------------------------------------------
        # CAREER ADVICE
        # -------------------------------------------------

        if ai_result.get("career_advice"):

            st.subheader(
                "💡 AI Career Advice"
            )

            st.write(
                ai_result["career_advice"]
            )


        # -------------------------------------------------
        # AGENT PIPELINE
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "🔗 Agentic AI Decision Pipeline"
        )

        pipeline = [
            "👤 Student Profile",
            "🎯 Career Goal",
            "📊 Skill Gap Analysis",
            "📈 Progress Tracking",
            "🤖 AI Career Agent",
            "🗺️ Personalized Roadmap",
            "📚 Recommendations",
            "🔄 Adaptive Roadmap"
        ]

        for index, step in enumerate(
            pipeline
        ):

            st.write(
                step
            )

            if index < len(pipeline) - 1:

                st.write("↓")


        # -------------------------------------------------
        # SAFE AI ERROR INFORMATION
        # -------------------------------------------------

        if ai_result.get("error"):

            with st.expander(
                "Technical information"
            ):

                st.code(
                    ai_result["error"]
                )


    # =====================================================
    # RECOMMENDED NEXT ACTIONS
    # =====================================================

    st.divider()

    st.header(
        "💡 Recommended Next Actions"
    )

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


    # =====================================================
    # WHY THESE RECOMMENDATIONS
    # =====================================================

    st.subheader(
        "💡 Why these recommendations?"
    )

    if remaining_skills:

        next_skill = remaining_skills[0]

        st.write(
            f"Your roadmap adapts to your completed skills. "
            f"Since **{next_skill}** is still incomplete, "
            f"it is currently prioritized as your next "
            f"learning goal."
        )

    else:

        st.write(
            f"You have completed the required skills "
            f"for **{career}**. The system therefore "
            f"recommends advanced projects and "
            f"career preparation."
        )

else:

    # =====================================================
    # INITIAL SCREEN
    # =====================================================

    st.info(
        "👆 Enter your profile details above and click "
        "**🚀 Analyze My Career** to begin."
    )
