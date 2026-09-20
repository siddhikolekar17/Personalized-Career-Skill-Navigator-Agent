import html
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd
import streamlit as st

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
# DATABASE CONFIGURATION — STEP 6
# ============================================================

DB_FILE = Path("career_navigator.db")


def get_db_connection():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)


def initialize_database():
    """Create the progress table if it does not already exist."""

    # closing() always closes the connection; "with connection" commits
    # on success and rolls back if something fails.
    with closing(get_db_connection()) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS skill_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    career TEXT NOT NULL,
                    skill TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(student_name, career, skill)
                )
                """
            )


def save_progress(student_name, career, progress_data):
    """Save the student's current skill progress."""

    with closing(get_db_connection()) as connection:
        with connection:
            connection.executemany(
                """
                INSERT INTO skill_progress
                (
                    student_name,
                    career,
                    skill,
                    completed,
                    updated_at
                )
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)

                ON CONFLICT(student_name, career, skill)
                DO UPDATE SET
                    completed = excluded.completed,
                    updated_at = CURRENT_TIMESTAMP
                """,
                [
                    (
                        student_name,
                        career,
                        skill,
                        1 if completed else 0,
                    )
                    for skill, completed in progress_data.items()
                ],
            )


def load_progress(student_name, career):
    """Load saved skill progress for a student and career."""

    with closing(get_db_connection()) as connection:
        rows = connection.execute(
            """
            SELECT skill, completed
            FROM skill_progress
            WHERE student_name = ?
            AND career = ?
            """,
            (
                student_name,
                career,
            ),
        ).fetchall()

    return {
        skill: bool(completed)
        for skill, completed in rows
    }


def get_last_saved(student_name, career):
    """Return the most recent save time (UTC) or None."""

    with closing(get_db_connection()) as connection:
        row = connection.execute(
            """
            SELECT MAX(updated_at)
            FROM skill_progress
            WHERE student_name = ?
            AND career = ?
            """,
            (
                student_name,
                career,
            ),
        ).fetchone()

    return row[0] if row else None


def delete_progress(student_name, career):
    """Delete saved progress for a student and career."""

    with closing(get_db_connection()) as connection:
        with connection:
            connection.execute(
                """
                DELETE FROM skill_progress
                WHERE student_name = ?
                AND career = ?
                """,
                (
                    student_name,
                    career,
                ),
            )


# Initialize database when app starts.
initialize_database()

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
        color: white;
    }

    .hero p {
        font-size: 17px;
        margin-bottom: 0;
        color: white;
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

    .dashboard-card {
        padding: 20px;
        border-radius: 15px;
        background: white;
        border: 1px solid #e5e7eb;
        text-align: center;
        margin-bottom: 15px;
    }

    .dashboard-number {
        font-size: 32px;
        font-weight: bold;
    }

    .dashboard-label {
        color: #64748b;
        font-size: 14px;
    }

    .dashboard-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .save-box {
        padding: 18px;
        border-radius: 14px;
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        margin-bottom: 15px;
    }

    /* Keep text dark on the light cards, even when Streamlit uses a dark theme. */
    .card, .skill-gap, .skill-match, .priority, .agent-step,
    .metric-card, .roadmap-box, .action-box, .dashboard-card, .save-box {
        color: #1f2937;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


def render_html(markup):
    """
    Render an HTML snippet safely.

    Streamlit treats lines indented by 4+ spaces after a blank line as a
    markdown code block, which can break nested HTML. Collapsing the
    indentation and blank lines avoids that.
    """

    compact = " ".join(
        line.strip()
        for line in markup.splitlines()
        if line.strip()
    )

    st.markdown(
        compact,
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

if "saved_progress_loaded" not in st.session_state:
    st.session_state.saved_progress_loaded = False

if "initial_skills" not in st.session_state:
    st.session_state.initial_skills = []

if "flash" not in st.session_state:
    st.session_state.flash = []

# ============================================================
# HELPER FUNCTIONS
# ============================================================

# Skills are learned in this order (foundations first).
PRIORITY_ORDER = [
    "Python",
    "Statistics",
    "SQL",
    "NumPy",
    "Pandas",
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


def progress_key(skill, career):
    """Session-state key used for a skill's progress checkbox."""
    return f"progress_{skill}_{career}"


def sort_by_priority(skills):
    """Sort skills so foundational ones come first."""

    def position(skill):
        if skill in PRIORITY_ORDER:
            return PRIORITY_ORDER.index(skill)
        return len(PRIORITY_ORDER)

    return sorted(skills, key=position)


def calculate_match(required_skills, current_skills):

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

    if not missing_skills:
        return "Advanced project development"

    return sort_by_priority(missing_skills)[0]


def generate_roadmap(career, missing_skills):

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


def generate_next_actions(
    career,
    missing_skills,
    matching_skills,
):

    actions = []

    if missing_skills:

        priority = choose_priority(
            missing_skills
        )

        actions.append(
            f"Focus first on {priority}, because it is "
            f"currently one of the important missing skills "
            f"for {career}."
        )

        actions.append(
            f"Complete one practical exercise related to "
            f"{priority} before moving to the next major skill."
        )

    if matching_skills:

        actions.append(
            f"Strengthen your existing "
            f"{matching_skills[0]} knowledge by applying "
            "it in a project."
        )

    actions.append(
        "Update your GitHub portfolio after completing "
        "each meaningful project milestone."
    )

    actions.append(
        "Tick skills off in the progress tracker as you complete "
        "them. The roadmap adapts automatically."
    )

    return actions


def generate_adaptation_message(progress):

    if progress < 25:

        return (
            "Your current profile has several skill gaps. "
            "The agent prioritizes foundational skills "
            "before advanced topics."
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


def generate_analysis(
    name,
    career,
    current_skills,
):

    required_skills = CAREER_SKILLS[career]

    matching, missing, percentage = calculate_match(
        required_skills,
        current_skills,
    )

    # Learn foundational skills first.
    missing = sort_by_priority(missing)

    priority = choose_priority(
        missing
    )

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

    # The summary is placed inside HTML, so escape the typed name.
    safe_name = html.escape(name)

    if percentage >= 80:

        profile_summary = (
            f"{safe_name}'s profile has strong alignment with "
            f"the {career} career path. The main focus should "
            "now be practical application, advanced projects "
            "and portfolio development."
        )

    elif percentage >= 50:

        profile_summary = (
            f"{safe_name}'s profile shows moderate alignment with "
            f"{career}. The agent identified several important "
            "skills that should be developed before moving "
            "toward advanced career preparation."
        )

    else:

        profile_summary = (
            f"{safe_name}'s profile is at an early stage for the "
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
# BUTTON CALLBACKS
# (callbacks run before the page reruns, so session state can be
# changed safely and the messages are not lost)
# ============================================================


def restore_initial_skills(career):
    """Set every progress checkbox back to the skills chosen at the start."""

    initial_lower = {
        skill.lower()
        for skill in st.session_state.initial_skills
    }

    for skill in CAREER_SKILLS[career]:

        st.session_state[progress_key(skill, career)] = (
            skill.lower() in initial_lower
        )


def on_save_progress():

    base = st.session_state.analysis_data

    progress_to_save = {
        skill: bool(
            st.session_state.get(
                progress_key(skill, base["career"]),
                False,
            )
        )
        for skill in CAREER_SKILLS[base["career"]]
    }

    save_progress(
        student_name=base["name"],
        career=base["career"],
        progress_data=progress_to_save,
    )

    st.session_state.flash = [
        ("success", "✅ Progress saved successfully!"),
        (
            "info",
            "You can now close and reopen the app. "
            "Your saved skill progress will be restored "
            "when you analyze the same student profile.",
        ),
    ]


def on_delete_saved_progress():

    base = st.session_state.analysis_data

    delete_progress(
        student_name=base["name"],
        career=base["career"],
    )

    restore_initial_skills(base["career"])

    st.session_state.flash = [
        (
            "success",
            "✅ Saved progress deleted. Your checkboxes were "
            "reset to the skills you selected at the start.",
        ),
    ]


def on_reset_current_progress():

    base = st.session_state.analysis_data

    restore_initial_skills(base["career"])

    st.session_state.flash = [
        (
            "success",
            "✅ Progress reset to your starting skills. "
            "Your saved database progress was not changed.",
        ),
    ]


def show_flash():
    """Show and clear any queued messages."""

    messages = st.session_state.flash
    st.session_state.flash = []

    for level, text in messages:
        getattr(st, level)(text)


# ============================================================
# HEADER
# ============================================================

render_html(
    """
    <div class="hero">

        <h1>🎯 Personalized Career & Skill Navigator</h1>

        <p>
            An agentic career guidance system that analyzes your skills,
            identifies gaps and creates an adaptive learning roadmap.
        </p>

    </div>
    """
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
        7. Save your progress
        8. Reopen the app and continue
        """
    )

    st.divider()

    st.info(
        "💡 This prototype uses a local decision engine "
        "and SQLite database. No paid AI API is required."
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

        # Baseline analysis from the skills selected above.
        st.session_state.analysis_data = generate_analysis(
            name=name.strip(),
            career=career,
            current_skills=current_skills,
        )

        st.session_state.initial_skills = list(current_skills)

        st.session_state.analysis_ready = True

        # Load previously saved database progress.
        saved_progress = load_progress(
            name.strip(),
            career,
        )

        for skill in CAREER_SKILLS[career]:

            key = progress_key(skill, career)

            if skill in saved_progress:

                st.session_state[key] = (
                    saved_progress[skill]
                )

            else:

                # New student:
                # selected current skills start as completed.
                st.session_state[key] = (
                    skill in current_skills
                )

        st.session_state.saved_progress_loaded = True

        if saved_progress:

            st.success(
                "✅ Career analysis completed and "
                "previously saved progress was restored!"
            )

        else:

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

    # Analysis created when the Analyze button was pressed.
    base_data = st.session_state.analysis_data

    # Live analysis: rebuilt from the current progress checkboxes so that
    # matching skills, gaps, priority, roadmap and next actions adapt
    # as soon as a skill is ticked or unticked.
    live_completed = [
        skill
        for skill in base_data["required"]
        if st.session_state.get(
            progress_key(skill, base_data["career"]),
            False,
        )
    ]

    data = generate_analysis(
        name=base_data["name"],
        career=base_data["career"],
        current_skills=live_completed,
    )

    st.divider()

    # ========================================================
    # CAREER ANALYSIS
    # ========================================================

    st.header("📊 Career Analysis")

    render_html(
        f"""
        <div class="card">

            <h3>Career Profile</h3>

            <p>{data["summary"]}</p>

        </div>
        """
    )

    # ========================================================
    # METRICS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        render_html(
            f"""
            <div class="metric-card">

                <div class="metric-value">
                    {data["percentage"]}%
                </div>

                <div class="metric-label">
                    Career Match
                </div>

            </div>
            """
        )

    with col2:

        render_html(
            f"""
            <div class="metric-card">

                <div class="metric-value">
                    {len(data["matching"])}
                </div>

                <div class="metric-label">
                    Matching Skills
                </div>

            </div>
            """
        )

    with col3:

        render_html(
            f"""
            <div class="metric-card">

                <div class="metric-value">
                    {len(data["missing"])}
                </div>

                <div class="metric-label">
                    Skill Gaps
                </div>

            </div>
            """
        )

    with col4:

        render_html(
            f"""
            <div class="metric-card">

                <div class="metric-value">
                    {len(data["required"])}
                </div>

                <div class="metric-label">
                    Required Skills
                </div>

            </div>
            """
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

                render_html(
                    f"""
                    <div class="skill-match">

                        <strong>✓ {skill}</strong><br>

                        <span class="small-text">
                            Already present in your profile
                        </span>

                    </div>
                    """
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

            render_html(
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
                """
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

    render_html(
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
        """
    )

    # ========================================================
    # ROADMAP
    # ========================================================

    st.header("🗺️ Adaptive Learning Roadmap")

    for phase in data["roadmap"]:

        skills_text = ", ".join(
            phase["skills"]
        )

        render_html(
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
            """
        )

    # ========================================================
    # PERSONALIZED RECOMMENDATIONS
    # ========================================================

    st.header(
        "💡 Personalized Skill Recommendations"
    )

    if not data["missing"]:

        st.success(
            "🎉 You have covered every required skill."
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

        render_html(
            f"""
            <div class="card">

                <strong>
                    {index}. {project}
                </strong>

            </div>
            """
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
        "Saved database progress is restored automatically "
        "when available. Everything on this page updates "
        "as you tick skills."
    )

    progress_skills = data["required"]

    completed_count = 0

    for skill in progress_skills:

        key = progress_key(skill, data["career"])

        if key not in st.session_state:

            st.session_state[key] = (
                skill in st.session_state.initial_skills
            )

        completed = st.checkbox(
            skill,
            key=key,
        )

        if completed:

            completed_count += 1

    # ========================================================
    # CALCULATE PROGRESS
    # ========================================================

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
    # STEP 6 — SAVE PROGRESS
    # ========================================================

    st.header("💾 Step 6 — Save Progress")

    render_html(
        """
        <div class="save-box">

            <strong>Persistent Progress</strong>

            <p>
                Your completed skills can now be stored in
                the SQLite database. Close and reopen the app,
                then analyze the same student profile to
                restore the saved progress.
            </p>

        </div>
        """
    )

    progress_to_save = {}

    for skill in progress_skills:

        key = progress_key(skill, data["career"])

        progress_to_save[skill] = (
            st.session_state.get(
                key,
                False,
            )
        )

    save_col1, save_col2 = st.columns(2)

    with save_col1:

        st.button(
            "💾 Save My Progress",
            type="primary",
            use_container_width=True,
            on_click=on_save_progress,
        )

    with save_col2:

        st.button(
            "🗑️ Delete Saved Progress",
            use_container_width=True,
            on_click=on_delete_saved_progress,
        )

    # Messages from the save / delete / reset buttons.
    show_flash()

    # Show whether the screen matches what is stored in the database.
    saved_now = load_progress(
        data["name"],
        data["career"],
    )

    if not saved_now:

        st.caption(
            "Nothing is saved yet for this student and career."
        )

    else:

        saved_view = {
            skill: saved_now.get(skill, False)
            for skill in progress_skills
        }

        if saved_view != progress_to_save:

            st.warning(
                "⚠️ You have unsaved changes. "
                "Press Save My Progress to keep them."
            )

        else:

            st.caption(
                "Last saved: "
                f"{get_last_saved(data['name'], data['career'])} (UTC)"
            )

    # ========================================================
    # ADAPTIVE PROGRESS MESSAGE
    # ========================================================

    current_adaptation = (
        generate_adaptation_message(
            progress
        )
    )

    st.header("🔄 Current Adaptive Status")

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
    # STEP 5 — DASHBOARD
    # ========================================================

    st.header("📊 Step 5 — Dashboard")

    dashboard_col1, dashboard_col2 = st.columns(2)

    with dashboard_col1:

        render_html(
            f"""
            <div class="dashboard-card">

                <div class="dashboard-title">
                    Career Match
                </div>

                <div class="dashboard-number">
                    {base_data["percentage"]}%
                </div>

                <div class="dashboard-label">
                    Initial profile match
                </div>

            </div>
            """
        )

    with dashboard_col2:

        render_html(
            f"""
            <div class="dashboard-card">

                <div class="dashboard-title">
                    Skills Completed
                </div>

                <div class="dashboard-number">
                    {completed_count}/{len(progress_skills)}
                </div>

                <div class="dashboard-label">
                    Current progress
                </div>

            </div>
            """
        )

    dashboard_col3, dashboard_col4 = st.columns(2)

    with dashboard_col3:

        remaining_count = (
            len(progress_skills)
            - completed_count
        )

        render_html(
            f"""
            <div class="dashboard-card">

                <div class="dashboard-title">
                    Skills Remaining
                </div>

                <div class="dashboard-number">
                    {remaining_count}
                </div>

                <div class="dashboard-label">
                    Skills still to complete
                </div>

            </div>
            """
        )

    with dashboard_col4:

        render_html(
            f"""
            <div class="dashboard-card">

                <div class="dashboard-title">
                    Roadmap Progress
                </div>

                <div class="dashboard-number">
                    {progress}%
                </div>

                <div class="dashboard-label">
                    Current learning progress
                </div>

            </div>
            """
        )

    # ========================================================
    # DASHBOARD CHART
    # ========================================================

    st.subheader("📈 Skill Completion Overview")

    chart_data = pd.DataFrame(
        {"Skills": [completed_count, remaining_count]},
        index=["Completed", "Remaining"],
    )

    st.bar_chart(
        chart_data,
        height=300,
    )

    st.subheader("🗺️ Roadmap Completion")

    st.progress(
        progress / 100,
        text=(
            f"Roadmap Progress: "
            f"{progress}%"
        ),
    )

    # ========================================================
    # COMPLETED / REMAINING SKILLS
    # ========================================================

    dashboard_skill_col1, dashboard_skill_col2 = st.columns(2)

    with dashboard_skill_col1:

        st.subheader("✅ Completed Skills")

        completed_skills = []

        for skill in progress_skills:

            key = progress_key(skill, data["career"])

            if st.session_state.get(
                key,
                False,
            ):

                completed_skills.append(
                    skill
                )

        if completed_skills:

            for skill in completed_skills:

                st.success(
                    f"✓ {skill}"
                )

        else:

            st.write(
                "No skills completed yet."
            )

    with dashboard_skill_col2:

        st.subheader("⏳ Remaining Skills")

        remaining_skills = []

        for skill in progress_skills:

            key = progress_key(skill, data["career"])

            if not st.session_state.get(
                key,
                False,
            ):

                remaining_skills.append(
                    skill
                )

        if remaining_skills:

            for skill in remaining_skills:

                st.warning(
                    f"• {skill}"
                )

        else:

            st.success(
                "🎉 All required skills completed!"
            )

    # ========================================================
    # RESET PROGRESS
    # ========================================================

    st.divider()

    st.button(
        "🔄 Reset Current Progress",
        use_container_width=True,
        on_click=on_reset_current_progress,
    )

    # ========================================================
    # NEXT ACTIONS
    # ========================================================

    st.header("🚀 Recommended Next Actions")

    for index, action in enumerate(
        data["actions"],
        start=1,
    ):

        render_html(
            f"""
            <div class="action-box">

                <strong>
                    Step {index}
                </strong>

                <p>
                    {action}
                </p>

            </div>
            """
        )

    # ========================================================
    # EXPLAINABILITY
    # ========================================================

    st.header(
        "❓ Why These Recommendations?"
    )

    render_html(
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
                progressive learning phases, foundations first.
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
                progress calculation, priority, roadmap and
                adaptive guidance change accordingly.
            </p>

            <p>
                <strong>8. Persistent Storage</strong><br>
                Skill progress is stored in a SQLite database
                so the student's progress can be restored
                when the same profile is opened again.
            </p>

        </div>
        """
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

        (
            "8️⃣",
            "Persistent Memory",
            "Stores completed skills in the "
            "SQLite database for later retrieval.",
        ),
    ]

    for (
        icon,
        title,
        description,
    ) in pipeline:

        render_html(
            f"""
            <div class="agent-step">

                <h4>
                    {icon} {title}
                </h4>

                <p>
                    {description}
                </p>

            </div>
            """
        )

    # ========================================================
    # SYSTEM STATUS
    # ========================================================

    st.divider()

    st.success(
        "🟢 Career Navigator is running "
        "with local decision engine + SQLite persistence."
    )

    st.caption(
        "No OpenAI API key, paid API credits "
        "or external AI service is required."
    )

    st.caption(
        "Student progress is stored in: "
        "career_navigator.db"
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

render_html(
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
        Skill Gap Analysis • Adaptive Roadmap •
        Persistent Progress

    </div>
    """
)
