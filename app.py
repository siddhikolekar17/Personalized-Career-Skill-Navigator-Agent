import streamlit as st
from datetime import datetime

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Personalized Career & Skill Navigator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc;
    }

    .hero {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(135deg, #173f5f, #20639b);
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        font-size: 38px;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 17px;
        margin-bottom: 0;
    }

    .card {
        padding: 20px;
        border-radius: 15px;
        background: white;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }

    .skill-gap {
        padding: 12px;
        border-radius: 10px;
        background: #fff4f4;
        border-left: 5px solid #e74c3c;
        margin-bottom: 8px;
    }

    .skill-match {
        padding: 12px;
        border-radius: 10px;
        background: #f0fff4;
        border-left: 5px solid #2e8b57;
        margin-bottom: 8px;
    }

    .priority {
        padding: 15px;
        border-radius: 12px;
        background: #fff8e7;
        border-left: 5px solid #f39c12;
        margin: 10px 0;
    }

    .agent-step {
        padding: 15px;
        border-radius: 12px;
        background: #f4f7fb;
        border: 1px solid #dce3ec;
        margin-bottom: 10px;
    }

    .small-text {
        color: #64748b;
        font-size: 14px;
    }

    .metric-card {
        text-align: center;
        padding: 18px;
        border-radius: 14px;
        background: white;
        border: 1px solid #e5e7eb;
    }

    .metric-value {
        font-size: 30px;
        font-weight: bold;
    }

    .metric-label {
        color: #64748b;
        font-size: 14px;
    }

    .roadmap-box {
        padding: 18px;
        border-radius: 14px;
        background: white;
        border: 1px solid #e5e7eb;
        margin-bottom: 12px;
    }

    .action-box {
        padding: 15px;
        border-radius: 12px;
        background: #f4f7fb;
        border: 1px solid #dce3ec;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CAREER DATA
# ============================================================

CAREER_SKILLS = {
    "AI/ML Engineer": [
        "Python",
        "NumPy",
        "Pandas",
        "Statistics",
        "Machine Learning",
        "Deep Learning",
        "SQL",
        "Git/GitHub",
    ],

    "Data Scientist": [
        "Python",
        "NumPy",
        "Pandas",
        "Statistics",
        "Machine Learning",
        "SQL",
        "Data Visualization",
        "Git/GitHub",
    ],

    "Web Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Python",
        "SQL",
        "Git/GitHub",
    ],

    "Data Analyst": [
        "Python",
        "SQL",
        "Excel",
        "Statistics",
        "Pandas",
        "Data Visualization",
        "Power BI",
        "Git/GitHub",
    ],
}

# ============================================================
# SKILL RECOMMENDATIONS
# ============================================================

SKILL_RECOMMENDATIONS = {
    "Python": {
        "why": (
            "Python is widely used for automation, data analysis, "
            "machine learning and backend development."
        ),
        "activity": (
            "Build small Python programs and gradually move toward "
            "project-based development."
        ),
    },

    "NumPy": {
        "why": (
            "NumPy provides the numerical computing foundation used "
            "heavily in data science and machine learning."
        ),
        "activity": (
            "Practice arrays, vectorization, matrix operations "
            "and numerical calculations."
        ),
    },

    "Pandas": {
        "why": (
            "Pandas is important for cleaning, transforming and "
            "analyzing structured datasets."
        ),
        "activity": (
            "Work with real datasets and practice filtering, "
            "grouping, merging and missing-value handling."
        ),
    },

    "Statistics": {
        "why": (
            "Statistics supports data interpretation, experimentation "
            "and machine-learning decisions."
        ),
        "activity": (
            "Study probability, distributions, mean, variance, "
            "correlation and hypothesis testing."
        ),
    },

    "Machine Learning": {
        "why": (
            "Machine learning is a core skill for building "
            "predictive intelligent systems."
        ),
        "activity": (
            "Implement regression, classification, clustering "
            "and model evaluation."
        ),
    },

    "Deep Learning": {
        "why": (
            "Deep learning is useful for advanced AI applications "
            "involving images, text and complex patterns."
        ),
        "activity": (
            "Build a small neural-network project using a public dataset."
        ),
    },

    "SQL": {
        "why": (
            "SQL is essential for retrieving, filtering and "
            "analyzing data stored in databases."
        ),
        "activity": (
            "Practice SELECT, JOIN, GROUP BY, subqueries "
            "and analytical queries."
        ),
    },

    "Git/GitHub": {
        "why": (
            "Git and GitHub demonstrate collaborative software "
            "development and version-control skills."
        ),
        "activity": (
            "Create repositories, commit meaningful changes "
            "and document projects with README files."
        ),
    },

    "HTML": {
        "why": (
            "HTML provides the structure of modern web pages."
        ),
        "activity": (
            "Create a responsive multi-page website using semantic HTML."
        ),
    },

    "CSS": {
        "why": (
            "CSS controls layout, appearance and responsive design."
        ),
        "activity": (
            "Build responsive layouts using Flexbox, Grid and media queries."
        ),
    },

    "JavaScript": {
        "why": (
            "JavaScript provides interactive behavior for web applications."
        ),
        "activity": (
            "Build interactive browser applications using DOM "
            "manipulation and APIs."
        ),
    },

    "React": {
        "why": (
            "React is widely used for component-based modern "
            "frontend development."
        ),
        "activity": (
            "Build a small dashboard with reusable components "
            "and state management."
        ),
    },

    "Data Visualization": {
        "why": (
            "Visualization helps communicate patterns and insights clearly."
        ),
        "activity": (
            "Create dashboards and charts from real-world datasets."
        ),
    },

    "Excel": {
        "why": (
            "Excel remains useful for business analysis, "
            "reporting and data preparation."
        ),
        "activity": (
            "Practice formulas, pivot tables, charts and data cleaning."
        ),
    },

    "Power BI": {
        "why": (
            "Power BI is useful for interactive business intelligence dashboards."
        ),
        "activity": (
            "Build a dashboard using a real dataset and explain the key insights."
        ),
    },
}

# ============================================================
# PROJECT RECOMMENDATIONS
# ============================================================

PROJECTS = {
    "AI/ML Engineer": [
        "House Price Prediction System",
        "Customer Churn Prediction",
        "Traffic Object Detection System",
        "Personalized Recommendation Engine",
    ],

    "Data Scientist": [
        "Customer Segmentation System",
        "Sales Prediction Dashboard",
        "Student Performance Prediction",
        "Movie Recommendation System",
    ],

    "Web Developer": [
        "Portfolio Website",
        "Student Management System",
        "E-Commerce Web Application",
        "Real-Time Task Management Dashboard",
    ],

    "Data Analyst": [
        "Sales Analytics Dashboard",
        "Student Performance Dashboard",
        "Customer Churn Analysis",
        "Business KPI Dashboard",
    ],
}

# ============================================================
# SESSION STATE
# ============================================================

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

if "analysis_ready" not in st.session_state:
    st.session_state.analysis_ready = False

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_match(required_skills, current_skills):
    """Calculate matching and missing skills."""

    current_lower = {
        skill.lower()
        for skill in current_skills
    }

    matching = []
    missing = []

    for skill in required_skills:

        if skill.lower() in current_lower:
            matching.append(skill)
        else:
            missing.append(skill)

    if required_skills:
        percentage = round(
            (len(matching) / len(required_skills)) * 100
        )
    else:
        percentage = 0

    return matching, missing, percentage


def choose_priority(missing_skills):
    """Choose the next skill using a transparent priority order."""

    if not missing_skills:
        return "Advanced project development"

    priority_order = [
        "Python",
        "Statistics",
        "SQL",
        "Pandas",
        "NumPy",
        "Machine Learning",
        "Data Visualization",
        "Git/GitHub",
        "Deep Learning",
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Excel",
        "Power BI",
    ]

    for skill in priority_order:

        if skill in missing_skills:
            return skill

    return missing_skills[0]


def generate_roadmap(career, missing_skills):
    """Generate a progressive learning roadmap."""

    if not missing_skills:

        return [
            {
                "phase": "Phase 1",
                "title": "Strengthen Existing Skills",
                "skills": ["Practice advanced concepts"],
                "goal": (
                    "Move from basic understanding toward "
                    "practical proficiency."
                ),
            },
            {
                "phase": "Phase 2",
                "title": "Build Portfolio Projects",
                "skills": ["Project development"],
                "goal": (
                    "Demonstrate practical skills through "
                    "portfolio projects."
                ),
            },
            {
                "phase": "Phase 3",
                "title": "Career Preparation",
                "skills": [
                    "Interview preparation",
                    "Resume",
                    "GitHub portfolio",
                ],
                "goal": (
                    "Prepare for internships and entry-level opportunities."
                ),
            },
        ]

    phases = []

    chunks = [
        missing_skills[:2],
        missing_skills[2:4],
        missing_skills[4:6],
        missing_skills[6:],
    ]

    phase_number = 1

    for chunk in chunks:

        if not chunk:
            continue

        if phase_number == 1:

            title = "Foundation Building"

            goal = (
                "Build the core skills required for the target career."
            )

        elif phase_number == 2:

            title = "Applied Learning"

            goal = (
                "Convert concepts into practical exercises and mini-projects."
            )

        elif phase_number == 3:

            title = "Intermediate Development"

            goal = (
                "Combine multiple skills to solve realistic problems."
            )

        else:

            title = "Portfolio & Career Readiness"

            goal = (
                "Create portfolio evidence and prepare for real-world opportunities."
            )

        phases.append(
            {
                "phase": f"Phase {phase_number}",
                "title": title,
                "skills": chunk,
                "goal": goal,
            }
        )

        phase_number += 1

    return phases


def generate_next_actions(career, missing_skills, matching_skills):
    """Generate personalized next actions."""

    actions = []

    if missing_skills:

        priority = choose_priority(missing_skills)

        actions.append(
            f"Focus first on {priority}, because it is currently "
            f"one of the important missing skills for {career}."
        )

        actions.append(
            f"Complete one practical exercise related to {priority} "
            "before moving to the next major skill."
        )

    if matching_skills:

        actions.append(
            f"Strengthen your existing {matching_skills[0]} knowledge "
            "by applying it in a project."
        )

    actions.append(
        "Update your GitHub portfolio after completing each "
        "meaningful project milestone."
    )

    actions.append(
        "Re-analyze your profile after completing skills "
        "so the roadmap can adapt."
    )

    return actions


def generate_adaptation_message(progress):
    """Generate an adaptive message from learning progress."""

    if progress < 25:

        return (
            "Your current profile has several skill gaps. "
            "The agent prioritizes foundational skills before advanced topics."
        )

    if progress < 50:

        return (
            "You have started building the required foundation. "
            "The next step is to combine skills through practical projects."
        )

    if progress < 75:

        return (
            "Your skill coverage is improving. "
            "The roadmap now shifts toward intermediate projects "
            "and portfolio development."
        )

    if progress < 100:

        return (
            "You have strong coverage of the target skills. "
            "Focus on advanced projects, GitHub evidence "
            "and interview preparation."
        )

    return (
        "Your required skill list is covered. "
        "The next stage is advanced projects, specialization "
        "and career preparation."
    )


def generate_analysis(name, career, current_skills):

    required_skills = CAREER_SKILLS[career]

    matching, missing, percentage = calculate_match(
        required_skills,
        current_skills,
    )

    priority = choose_priority(missing)

    roadmap = generate_roadmap(
        career,
        missing,
    )

    projects = PROJECTS.get(
        career,
        [
            "Build a portfolio project related "
            "to your target career."
        ],
    )

    actions = generate_next_actions(
        career,
        missing,
        matching,
    )

    adaptation = generate_adaptation_message(
        percentage
    )

    if percentage >= 80:

        profile_summary = (
            f"{name}'s profile has strong alignment with the "
            f"{career} career path. The main focus should now be "
            "practical application, advanced projects and "
            "portfolio development."
        )

    elif percentage >= 50:

        profile_summary = (
            f"{name}'s profile shows moderate alignment with "
            f"{career}. The agent identified several important "
            "skills that should be developed before moving toward "
            "advanced career preparation."
        )

    else:

        profile_summary = (
            f"{name}'s profile is at an early stage for the "
            f"{career} target. The agent therefore prioritizes "
            "foundational skills and guided projects."
        )

    return {
        "name": name,
        "career": career,
        "required": required_skills,
        "matching": matching,
        "missing": missing,
        "percentage": percentage,
        "priority": priority,
        "roadmap": roadmap,
        "projects": projects,
        "actions": actions,
        "adaptation": adaptation,
        "summary": profile_summary,
    }


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <h1>🎯 Personalized Career & Skill Navigator</h1>

        <p>
            An agentic career guidance system that analyzes your skills,
            identifies gaps and creates an adaptive learning roadmap.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🎯 Career Navigator")

    st.markdown(
        """
        **How it works**

        1. Enter your profile
        2. Select your target career
        3. Select your current skills
        4. Analyze your skill gaps
        5. Follow the personalized roadmap
        6. Track your progress
        7. Re-analyze as you improve
        """
    )

    st.divider()

    st.info(
        "💡 This prototype uses a local decision engine, "
        "so it does not require an external AI API "
        "or paid API credits."
    )

# ============================================================
# STUDENT PROFILE
# ============================================================

st.header("👤 Student Profile")

col1, col2 = st.columns(2)

with col1:

    name = st.text_input(
        "Your Name",
        placeholder="Enter your name",
    )

with col2:

    career = st.selectbox(
        "Target Career",
        list(CAREER_SKILLS.keys()),
    )

st.subheader("🧠 Current Skills")

all_skills = sorted(
    {
        skill
        for skills in CAREER_SKILLS.values()
        for skill in skills
    }
)

current_skills = st.multiselect(
    "Select the skills you currently know",
    all_skills,
    help=(
        "Select all skills you already have "
        "basic or practical knowledge of."
    ),
)

st.caption(
    f"Selected {len(current_skills)} skill(s). "
    "You can update this later and re-run the analysis."
)

# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "🚀 Analyze My Career",
    type="primary",
    use_container_width=True,
):

    if not name.strip():

        st.warning(
            "Please enter your name first."
        )

    elif not current_skills:

        st.warning(
            "Please select at least one current skill "
            "so the navigator can calculate your skill gap."
        )

    else:

        # Generate fresh analysis
        st.session_state.analysis_data = generate_analysis(
            name=name.strip(),
            career=career,
            current_skills=current_skills,
        )

        st.session_state.analysis_ready = True

        # Reset old progress checkboxes for this career
        for skill in CAREER_SKILLS[career]:

            key = f"progress_{skill}_{career}"

            if key in st.session_state:
                del st.session_state[key]

        st.success(
            "✅ Career profile analyzed successfully!"
        )

# ============================================================
# RESULTS
# ============================================================

if (
    st.session_state.analysis_ready
    and st.session_state.analysis_data
):

    data = st.session_state.analysis_data

    st.divider()

    # ========================================================
    # CAREER ANALYSIS
    # ========================================================

    st.header("📊 Career Analysis")

    st.markdown(
        f"""
        <div class="card">

            <h3>Career Profile</h3>

            <p>{data["summary"]}</p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # METRICS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-value">
                    {data["percentage"]}%
                </div>

                <div class="metric-label">
                    Career Match
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-value">
                    {len(data["matching"])}
                </div>

                <div class="metric-label">
                    Matching Skills
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-value">
                    {len(data["missing"])}
                </div>

                <div class="metric-label">
                    Skill Gaps
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-value">
                    {len(data["required"])}
                </div>

                <div class="metric-label">
                    Required Skills
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # ========================================================
    # MATCHING SKILLS
    # ========================================================

    st.header("✅ Matching Skills")

    if data["matching"]:

        cols = st.columns(2)

        for index, skill in enumerate(
            data["matching"]
        ):

            with cols[index % 2]:

                st.markdown(
                    f"""
                    <div class="skill-match">

                        <strong>✓ {skill}</strong><br>

                        <span class="small-text">
                            Already present in your profile
                        </span>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:

        st.info(
            "No matching skills were detected "
            "for the selected career."
        )

    # ========================================================
    # SKILL GAPS
    # ========================================================

    st.header("⚠️ Skill Gaps")

    if data["missing"]:

        for skill in data["missing"]:

            recommendation = SKILL_RECOMMENDATIONS.get(
                skill,
                {
                    "why": (
                        "This skill is required "
                        "for your selected career."
                    ),
                    "activity": (
                        "Practice the skill through "
                        "a practical project."
                    ),
                },
            )

            st.markdown(
                f"""
                <div class="skill-gap">

                    <strong>❌ {skill}</strong><br>

                    <span>
                        {recommendation["why"]}
                    </span><br>

                    <span class="small-text">
                        Recommended activity:
                        {recommendation["activity"]}
                    </span>

                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.success(
            "🎉 No major skill gaps detected "
            "from the selected skill list."
        )

    # ========================================================
    # PRIORITY
    # ========================================================

    st.header("🎯 Recommended Next Priority")

    st.markdown(
        f"""
        <div class="priority">

            <h3>
                Focus on: {data["priority"]}
            </h3>

            <p>
                The decision engine selected this as the next
                priority based on your current skill profile
                and target career.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # ROADMAP
    # ========================================================

    st.header("🗺️ Adaptive Learning Roadmap")

    for phase in data["roadmap"]:

        skills_text = ", ".join(
            phase["skills"]
        )

        st.markdown(
            f"""
            <div class="roadmap-box">

                <h3>
                    {phase["phase"]} — {phase["title"]}
                </h3>

                <p>
                    <strong>Skills:</strong>
                    {skills_text}
                </p>

                <p>
                    <strong>Goal:</strong>
                    {phase["goal"]}
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # ========================================================
    # PERSONALIZED RECOMMENDATIONS
    # ========================================================

    st.header(
        "💡 Personalized Skill Recommendations"
    )

    for skill in data["missing"]:

        recommendation = SKILL_RECOMMENDATIONS.get(
            skill,
            {
                "why": "Important for the target career.",
                "activity": (
                    "Practice through a practical project."
                ),
            },
        )

        with st.expander(
            f"📚 {skill}"
        ):

            st.write(
                f"**Why this matters:** "
                f"{recommendation['why']}"
            )

            st.write(
                f"**Recommended activity:** "
                f"{recommendation['activity']}"
            )

    # ========================================================
    # PROJECT RECOMMENDATIONS
    # ========================================================

    st.header("🛠️ Recommended Projects")

    st.write(
        "Projects are selected according to your target "
        "career so that learning can be converted into "
        "portfolio evidence."
    )

    for index, project in enumerate(
        data["projects"],
        start=1,
    ):

        st.markdown(
            f"""
            <div class="card">

                <strong>
                    {index}. {project}
                </strong>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # ========================================================
    # ADAPTIVE STRATEGY
    # ========================================================

    st.header("🔄 Adaptive Strategy")

    st.info(
        data["adaptation"]
    )

    # ========================================================
    # PROGRESS TRACKING
    # ========================================================

    st.header("📈 Skill Progress Tracking")

    st.caption(
        "Your initially selected skills are marked as completed. "
        "Use the checkboxes to update your learning progress."
    )

    progress_skills = data["required"]

    completed_count = 0

    for skill in progress_skills:

        # Initially selected skills are completed.
        default_value = (
            skill in data["matching"]
        )

        key = (
            f"progress_{skill}_{data['career']}"
        )

        # Initialize only once.
        if key not in st.session_state:

            st.session_state[key] = (
                default_value
            )

        completed = st.checkbox(
            skill,
            key=key,
        )

        if completed:
            completed_count += 1

    # Calculate progress.
    progress = (
        round(
            (
                completed_count
                / len(progress_skills)
            ) * 100
        )
        if progress_skills
        else 0
    )

    st.progress(
        progress / 100,
        text=(
            f"Learning Progress: "
            f"{progress}%"
        ),
    )

    st.write(
        f"**{completed_count} / "
        f"{len(progress_skills)} "
        f"required skills completed**"
    )

    # ========================================================
    # ADAPTIVE PROGRESS MESSAGE
    # ========================================================

    current_adaptation = generate_adaptation_message(
        progress
    )

    if progress >= 80:

        st.success(
            "🚀 " + current_adaptation
        )

    elif progress >= 50:

        st.info(
            "📚 " + current_adaptation
        )

    else:

        st.warning(
            "🌱 " + current_adaptation
        )

    # ========================================================
    # RESET PROGRESS
    # ========================================================

    if st.button(
        "🔄 Reset Skill Progress",
        use_container_width=True,
    ):

        for skill in data["required"]:

            key = (
                f"progress_{skill}_{data['career']}"
            )

            if key in st.session_state:

                del st.session_state[key]

        st.rerun()

    # ========================================================
    # NEXT ACTIONS
    # ========================================================

    st.header("🚀 Recommended Next Actions")

    for index, action in enumerate(
        data["actions"],
        start=1,
    ):

        st.markdown(
            f"""
            <div class="action-box">

                <strong>
                    Step {index}
                </strong>

                <p>
                    {action}
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # ========================================================
    # EXPLAINABILITY
    # ========================================================

    st.header(
        "❓ Why These Recommendations?"
    )

    st.markdown(
        """
        <div class="card">

            <p>
                The navigator follows a transparent decision process:
            </p>

            <p>
                <strong>1. Target Career</strong><br>
                Your selected career is used to determine the
                required skill set.
            </p>

            <p>
                <strong>2. Current Skill Profile</strong><br>
                The skills you selected are compared against
                the target requirements.
            </p>

            <p>
                <strong>3. Skill Gap Detection</strong><br>
                Skills present in the target career but missing
                from your profile become skill gaps.
            </p>

            <p>
                <strong>4. Priority Selection</strong><br>
                The engine prioritizes foundational or
                high-dependency skills first.
            </p>

            <p>
                <strong>5. Roadmap Generation</strong><br>
                Missing skills are organized into
                progressive learning phases.
            </p>

            <p>
                <strong>6. Project Recommendation</strong><br>
                Projects are selected according to the target
                career so that learning produces practical
                portfolio evidence.
            </p>

            <p>
                <strong>7. Progress Adaptation</strong><br>
                When your completed skills change, the
                progress calculation and adaptive guidance
                change accordingly.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # AGENTIC AI DECISION PIPELINE
    # ========================================================

    st.header(
        "🤖 Agentic AI Decision Pipeline"
    )

    pipeline = [

        (
            "1️⃣",
            "Profile Understanding",
            "Reads the student's target career "
            "and current skill profile.",
        ),

        (
            "2️⃣",
            "Career Skill Mapping",
            "Maps the selected career to the "
            "skills required for that career.",
        ),

        (
            "3️⃣",
            "Skill Gap Detection",
            "Compares existing skills against "
            "required skills.",
        ),

        (
            "4️⃣",
            "Priority Decision",
            "Selects the next skill based on "
            "the detected gap.",
        ),

        (
            "5️⃣",
            "Roadmap Planning",
            "Creates progressive learning phases.",
        ),

        (
            "6️⃣",
            "Project Recommendation",
            "Suggests projects aligned with "
            "the target career.",
        ),

        (
            "7️⃣",
            "Progress Adaptation",
            "Updates recommendations when the "
            "student's progress changes.",
        ),
    ]

    for (
        icon,
        title,
        description,
    ) in pipeline:

        st.markdown(
            f"""
            <div class="agent-step">

                <h4>
                    {icon} {title}
                </h4>

                <p>
                    {description}
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # ========================================================
    # SYSTEM STATUS
    # ========================================================

    st.divider()

    st.success(
        "🟢 Career Navigator is running "
        "in local zero-cost mode."
    )

    st.caption(
        "No OpenAI API key, paid API credits "
        "or external AI service is required."
    )

    st.caption(
        "Analysis generated locally on "
        f"{datetime.now().strftime('%d %b %Y, %H:%M')}"
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        color:#64748b;
        padding:10px;
    ">

        <strong>
            Personalized Career & Skill Navigator Agent
        </strong>

        <br>

        Agentic AI • Personalized Learning •
        Skill Gap Analysis • Adaptive Roadmap

    </div>
    """,
    unsafe_allow_html=True,
)
