"""
Personalized Career & Skill Navigator — Enhanced Edition
=========================================================

Run with:
    pip install streamlit pandas          # plotly is optional (radar chart)
    streamlit run app.py

What's new compared with the Step 6 version
-------------------------------------------
 1. Six careers (added GenAI / Agentic AI Engineer and Full Stack Developer)
 2. Prerequisite-aware roadmap (skills are ordered by dependency, not just a list)
 3. Study-hours slider -> per-phase weeks and an estimated completion date
 4. Live adaptation: checking a skill instantly updates priority, roadmap,
    next actions and career comparison (no need to press Analyze again)
 5. Learning resources, difficulty level and time estimate for every skill
 6. Per-skill notes saved to the database
 7. Progress history (a snapshot on every save) with a trend chart
 8. Returning-student picker that restores career, hours, skills and notes
 9. Career comparison: match % of your skills against every career
10. Project recommendations with "ready to build" / "locked" status
11. Category coverage chart (radar with plotly, bar chart fallback)
12. Achievement badges and a weekly study plan
13. Export report as Markdown, CSV or JSON, plus a database backup button
14. Fixes: user input is HTML-escaped, cards stay readable in dark mode,
    buttons use callbacks (safe session-state updates), DB connections
    always close, HTML blocks no longer risk rendering as code
"""

import html
import io
import json
import math
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go

    PLOTLY_OK = True
except ImportError:  # radar chart falls back to a bar chart
    PLOTLY_OK = False

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
# DATABASE
# ============================================================

DB_FILE = Path("career_navigator.db")


@contextmanager
def db():
    """Open a connection, commit on success, roll back on error, always close."""
    connection = sqlite3.connect(DB_FILE)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    """Create all tables if they do not already exist."""
    with db() as conn:
        # Same schema as the previous version, so existing data keeps working.
        conn.execute(
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progress_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                career TEXT NOT NULL,
                completed_count INTEGER NOT NULL,
                total_count INTEGER NOT NULL,
                percentage INTEGER NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS skill_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                career TEXT NOT NULL,
                skill TEXT NOT NULL,
                note TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_name, career, skill)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS student_settings (
                student_name TEXT PRIMARY KEY,
                last_career TEXT,
                hours_per_week INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_progress(student_name, career, progress_data, notes, hours_per_week):
    """Save skill progress, notes, a history snapshot and study settings."""
    total = len(progress_data)
    done = sum(1 for value in progress_data.values() if value)
    percentage = round(done / total * 100) if total else 0

    with db() as conn:
        conn.executemany(
            """
            INSERT INTO skill_progress
                (student_name, career, skill, completed, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(student_name, career, skill)
            DO UPDATE SET
                completed = excluded.completed,
                updated_at = CURRENT_TIMESTAMP
            """,
            [
                (student_name, career, skill, 1 if completed else 0)
                for skill, completed in progress_data.items()
            ],
        )

        for skill, note in notes.items():
            note = (note or "").strip()
            if note:
                conn.execute(
                    """
                    INSERT INTO skill_notes
                        (student_name, career, skill, note, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(student_name, career, skill)
                    DO UPDATE SET
                        note = excluded.note,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (student_name, career, skill, note),
                )
            else:
                conn.execute(
                    "DELETE FROM skill_notes "
                    "WHERE student_name = ? AND career = ? AND skill = ?",
                    (student_name, career, skill),
                )

        conn.execute(
            """
            INSERT INTO progress_history
                (student_name, career, completed_count, total_count, percentage)
            VALUES (?, ?, ?, ?, ?)
            """,
            (student_name, career, done, total, percentage),
        )

        conn.execute(
            """
            INSERT INTO student_settings
                (student_name, last_career, hours_per_week, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(student_name)
            DO UPDATE SET
                last_career = excluded.last_career,
                hours_per_week = excluded.hours_per_week,
                updated_at = CURRENT_TIMESTAMP
            """,
            (student_name, career, hours_per_week),
        )


def load_progress(student_name, career):
    """Return {skill: completed_bool} for a student and career."""
    with db() as conn:
        rows = conn.execute(
            "SELECT skill, completed FROM skill_progress "
            "WHERE student_name = ? AND career = ?",
            (student_name, career),
        ).fetchall()
    return {skill: bool(completed) for skill, completed in rows}


def load_notes(student_name, career):
    """Return {skill: note_text} for a student and career."""
    with db() as conn:
        rows = conn.execute(
            "SELECT skill, note FROM skill_notes "
            "WHERE student_name = ? AND career = ?",
            (student_name, career),
        ).fetchall()
    return {skill: note for skill, note in rows}


def load_history(student_name, career):
    """Return the saved progress snapshots as a DataFrame."""
    with db() as conn:
        rows = conn.execute(
            "SELECT recorded_at, percentage, completed_count, total_count "
            "FROM progress_history "
            "WHERE student_name = ? AND career = ? "
            "ORDER BY recorded_at, id",
            (student_name, career),
        ).fetchall()
    return pd.DataFrame(
        rows,
        columns=["Saved at", "Progress %", "Completed", "Total"],
    )


def load_settings(student_name):
    """Return the last saved career and study hours for a student."""
    with db() as conn:
        row = conn.execute(
            "SELECT last_career, hours_per_week FROM student_settings "
            "WHERE student_name = ?",
            (student_name,),
        ).fetchone()
    if not row:
        return None
    return {"career": row[0], "hours": row[1]}


def list_students():
    """All student names that have saved progress."""
    with db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT student_name FROM skill_progress "
            "ORDER BY student_name COLLATE NOCASE"
        ).fetchall()
    return [row[0] for row in rows]


def delete_progress(student_name, career):
    """Delete saved progress, notes and history for a student and career."""
    with db() as conn:
        for table in ("skill_progress", "skill_notes", "progress_history"):
            conn.execute(
                f"DELETE FROM {table} WHERE student_name = ? AND career = ?",
                (student_name, career),
            )


initialize_database()

# ============================================================
# CUSTOM CSS  (explicit text colours keep cards readable in dark mode)
# ============================================================

st.markdown(
    """
    <style>
    .hero {
        padding: 28px; border-radius: 18px;
        background: linear-gradient(135deg, #173f5f, #20639b);
        color: white; margin-bottom: 25px;
    }
    .hero h1 { font-size: 38px; margin-bottom: 8px; color: white; }
    .hero p { font-size: 17px; margin-bottom: 0; color: #e6eef7; }

    .card, .skill-gap, .skill-match, .priority, .agent-step,
    .roadmap-box, .action-box, .save-box, .project-card, .badge-card,
    .week-box {
        color: #1f2937;
    }
    .card, .roadmap-box, .project-card {
        padding: 18px; border-radius: 14px; background: white;
        border: 1px solid #e5e7eb; margin-bottom: 12px;
    }
    .skill-gap {
        padding: 12px; border-radius: 10px; background: #fff4f4;
        border-left: 5px solid #e74c3c; margin-bottom: 8px;
    }
    .skill-match {
        padding: 12px; border-radius: 10px; background: #f0fff4;
        border-left: 5px solid #2e8b57; margin-bottom: 8px;
    }
    .priority {
        padding: 15px; border-radius: 12px; background: #fff8e7;
        border-left: 5px solid #f39c12; margin: 10px 0;
    }
    .agent-step, .action-box {
        padding: 15px; border-radius: 12px; background: #f4f7fb;
        border: 1px solid #dce3ec; margin-bottom: 10px;
    }
    .save-box {
        padding: 18px; border-radius: 14px; background: #f0f9ff;
        border: 1px solid #bae6fd; margin-bottom: 15px;
    }
    .badge-card {
        padding: 12px; border-radius: 12px; background: #fdf7e3;
        border: 1px solid #f3e2a9; margin-bottom: 8px;
    }
    .week-box {
        padding: 10px 14px; border-radius: 10px; background: #eef6ff;
        border: 1px solid #cfe2fb; margin-bottom: 8px;
    }
    .small-text { color: #64748b; font-size: 14px; }
    .pill {
        display: inline-block; padding: 2px 10px; margin-right: 6px;
        border-radius: 999px; background: #e8eef6; color: #1f2937;
        font-size: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def html_box(css_class, *parts):
    """Render one HTML block on a single line (avoids markdown code-block quirks)."""
    inner = "".join(parts)
    st.markdown(f'<div class="{css_class}">{inner}</div>', unsafe_allow_html=True)


esc = html.escape

# ============================================================
# CAREER DATA
# ============================================================

CAREER_SKILLS = {
    "AI/ML Engineer": [
        "Python", "NumPy", "Pandas", "Statistics",
        "Machine Learning", "Deep Learning", "SQL", "Git/GitHub",
    ],
    "Data Scientist": [
        "Python", "NumPy", "Pandas", "Statistics",
        "Machine Learning", "SQL", "Data Visualization", "Git/GitHub",
    ],
    "Web Developer": [
        "HTML", "CSS", "JavaScript", "React", "Python", "SQL", "Git/GitHub",
    ],
    "Data Analyst": [
        "Python", "SQL", "Excel", "Statistics", "Pandas",
        "Data Visualization", "Power BI", "Git/GitHub",
    ],
    "GenAI / Agentic AI Engineer": [
        "Python", "REST APIs", "Prompt Engineering", "LLM Integration",
        "Vector Databases", "RAG", "Agent Frameworks", "Docker", "Git/GitHub",
    ],
    "Full Stack Developer": [
        "HTML", "CSS", "JavaScript", "React", "Node.js",
        "SQL", "REST APIs", "Docker", "Git/GitHub",
    ],
}

# ============================================================
# SKILL KNOWLEDGE BASE
# hours = rough effort for a beginner to reach working proficiency
# prereqs = skills that should be learned first
# ============================================================

SKILL_INFO = {
    "Python": {
        "category": "Programming", "level": "Foundation", "hours": 40, "prereqs": [],
        "why": "Python is widely used for automation, data analysis, machine learning and backend development.",
        "activity": "Build small Python programs and gradually move toward project-based development.",
        "resources": [
            ("Official Python Tutorial", "https://docs.python.org/3/tutorial/"),
            ("Kaggle Learn: Python", "https://www.kaggle.com/learn"),
        ],
    },
    "NumPy": {
        "category": "Data & Math", "level": "Foundation", "hours": 15, "prereqs": ["Python"],
        "why": "NumPy provides the numerical computing foundation used heavily in data science and machine learning.",
        "activity": "Practice arrays, vectorization, matrix operations and numerical calculations.",
        "resources": [("NumPy Learn", "https://numpy.org/learn/")],
    },
    "Pandas": {
        "category": "Data & Math", "level": "Core", "hours": 25, "prereqs": ["Python", "NumPy"],
        "why": "Pandas is important for cleaning, transforming and analyzing structured datasets.",
        "activity": "Work with real datasets and practice filtering, grouping, merging and missing-value handling.",
        "resources": [
            ("Pandas Getting Started", "https://pandas.pydata.org/docs/getting_started/index.html"),
            ("Kaggle Learn: Pandas", "https://www.kaggle.com/learn"),
        ],
    },
    "Statistics": {
        "category": "Data & Math", "level": "Foundation", "hours": 35, "prereqs": [],
        "why": "Statistics supports data interpretation, experimentation and machine-learning decisions.",
        "activity": "Study probability, distributions, mean, variance, correlation and hypothesis testing.",
        "resources": [("Khan Academy: Statistics & Probability", "https://www.khanacademy.org/math/statistics-probability")],
    },
    "Machine Learning": {
        "category": "ML & AI", "level": "Core", "hours": 60, "prereqs": ["Python", "Statistics", "Pandas"],
        "why": "Machine learning is a core skill for building predictive intelligent systems.",
        "activity": "Implement regression, classification, clustering and model evaluation.",
        "resources": [("scikit-learn User Guide", "https://scikit-learn.org/stable/user_guide.html")],
    },
    "Deep Learning": {
        "category": "ML & AI", "level": "Advanced", "hours": 70, "prereqs": ["Machine Learning"],
        "why": "Deep learning is useful for advanced AI applications involving images, text and complex patterns.",
        "activity": "Build a small neural-network project using a public dataset.",
        "resources": [("PyTorch Tutorials", "https://pytorch.org/tutorials/")],
    },
    "SQL": {
        "category": "Data & Math", "level": "Foundation", "hours": 25, "prereqs": [],
        "why": "SQL is essential for retrieving, filtering and analyzing data stored in databases.",
        "activity": "Practice SELECT, JOIN, GROUP BY, subqueries and analytical queries.",
        "resources": [("SQLite Tutorial", "https://www.sqlitetutorial.net/")],
    },
    "Git/GitHub": {
        "category": "Tools & Cloud", "level": "Foundation", "hours": 10, "prereqs": [],
        "why": "Git and GitHub demonstrate collaborative software development and version-control skills.",
        "activity": "Create repositories, commit meaningful changes and document projects with README files.",
        "resources": [("GitHub Docs: Get Started", "https://docs.github.com/en/get-started")],
    },
    "HTML": {
        "category": "Web", "level": "Foundation", "hours": 15, "prereqs": [],
        "why": "HTML provides the structure of modern web pages.",
        "activity": "Create a responsive multi-page website using semantic HTML.",
        "resources": [("MDN: HTML", "https://developer.mozilla.org/en-US/docs/Web/HTML")],
    },
    "CSS": {
        "category": "Web", "level": "Foundation", "hours": 25, "prereqs": ["HTML"],
        "why": "CSS controls layout, appearance and responsive design.",
        "activity": "Build responsive layouts using Flexbox, Grid and media queries.",
        "resources": [("MDN: CSS", "https://developer.mozilla.org/en-US/docs/Web/CSS")],
    },
    "JavaScript": {
        "category": "Web", "level": "Core", "hours": 45, "prereqs": ["HTML"],
        "why": "JavaScript provides interactive behavior for web applications.",
        "activity": "Build interactive browser applications using DOM manipulation and APIs.",
        "resources": [("MDN: JavaScript", "https://developer.mozilla.org/en-US/docs/Web/JavaScript")],
    },
    "React": {
        "category": "Web", "level": "Core", "hours": 40, "prereqs": ["JavaScript"],
        "why": "React is widely used for component-based modern frontend development.",
        "activity": "Build a small dashboard with reusable components and state management.",
        "resources": [("React: Learn", "https://react.dev/learn")],
    },
    "Node.js": {
        "category": "Web", "level": "Core", "hours": 30, "prereqs": ["JavaScript"],
        "why": "Node.js lets you build backend services and APIs using JavaScript.",
        "activity": "Build a small REST service with routing, validation and a database connection.",
        "resources": [("Node.js Learn", "https://nodejs.org/en/learn")],
    },
    "REST APIs": {
        "category": "Web", "level": "Core", "hours": 20, "prereqs": ["Python"],
        "why": "REST APIs are how applications, services and AI models talk to each other.",
        "activity": "Consume a public API, then design and document one of your own.",
        "resources": [("MDN: HTTP", "https://developer.mozilla.org/en-US/docs/Web/HTTP")],
    },
    "Data Visualization": {
        "category": "Analytics", "level": "Core", "hours": 20, "prereqs": ["Pandas"],
        "why": "Visualization helps communicate patterns and insights clearly.",
        "activity": "Create dashboards and charts from real-world datasets.",
        "resources": [("Matplotlib Tutorials", "https://matplotlib.org/stable/tutorials/index.html")],
    },
    "Excel": {
        "category": "Analytics", "level": "Foundation", "hours": 20, "prereqs": [],
        "why": "Excel remains useful for business analysis, reporting and data preparation.",
        "activity": "Practice formulas, pivot tables, charts and data cleaning.",
        "resources": [("Microsoft Excel Support", "https://support.microsoft.com/excel")],
    },
    "Power BI": {
        "category": "Analytics", "level": "Core", "hours": 25, "prereqs": ["Data Visualization"],
        "why": "Power BI is useful for interactive business intelligence dashboards.",
        "activity": "Build a dashboard using a real dataset and explain the key insights.",
        "resources": [("Power BI Documentation", "https://learn.microsoft.com/power-bi/")],
    },
    "Prompt Engineering": {
        "category": "ML & AI", "level": "Foundation", "hours": 12, "prereqs": [],
        "why": "Clear, structured prompts are the fastest way to get reliable behavior from language models.",
        "activity": "Write and test prompts with examples, output formats and step-by-step instructions, then compare results.",
        "resources": [("Prompt Engineering Overview", "https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview")],
    },
    "LLM Integration": {
        "category": "ML & AI", "level": "Core", "hours": 30, "prereqs": ["Python", "REST APIs", "Prompt Engineering"],
        "why": "Integrating LLM APIs into applications is the base skill for every AI product and agent.",
        "activity": "Build a small app that calls an LLM API, handles errors, streams output and keeps conversation state.",
        "resources": [("Claude API Docs", "https://docs.claude.com")],
    },
    "Vector Databases": {
        "category": "ML & AI", "level": "Core", "hours": 20, "prereqs": ["Python"],
        "why": "Vector databases store embeddings so applications can search by meaning instead of keywords.",
        "activity": "Embed a set of documents, store them in a vector store and run similarity searches.",
        "resources": [("Chroma Docs", "https://docs.trychroma.com/")],
    },
    "RAG": {
        "category": "ML & AI", "level": "Advanced", "hours": 35, "prereqs": ["LLM Integration", "Vector Databases"],
        "why": "Retrieval-Augmented Generation grounds model answers in your own documents and data.",
        "activity": "Build a document Q&A pipeline: chunk, embed, retrieve, generate and cite sources.",
        "resources": [("LangChain: Build a RAG App", "https://python.langchain.com/docs/tutorials/rag/")],
    },
    "Agent Frameworks": {
        "category": "ML & AI", "level": "Advanced", "hours": 40, "prereqs": ["LLM Integration"],
        "why": "Agent frameworks let models plan, call tools and loop until a task is finished.",
        "activity": "Build an agent with two or three tools, a planning step and basic guardrails.",
        "resources": [("LangGraph Docs", "https://langchain-ai.github.io/langgraph/")],
    },
    "Docker": {
        "category": "Tools & Cloud", "level": "Core", "hours": 20, "prereqs": [],
        "why": "Docker packages your app and its dependencies so it runs the same everywhere.",
        "activity": "Containerize one of your projects and run it with Docker Compose.",
        "resources": [("Docker: Get Started", "https://docs.docker.com/get-started/")],
    },
}

# Order used to break ties when several skills are ready to be learned.
PRIORITY_ORDER = [
    "Python", "Statistics", "SQL", "HTML", "Pandas", "NumPy", "CSS",
    "Excel", "Prompt Engineering", "Git/GitHub", "JavaScript", "REST APIs",
    "Data Visualization", "Machine Learning", "Node.js", "React",
    "Vector Databases", "LLM Integration", "Docker", "Power BI",
    "Deep Learning", "RAG", "Agent Frameworks",
]

# ============================================================
# PROJECT RECOMMENDATIONS
# (title, description, skills used, difficulty)
# ============================================================

PROJECTS = {
    "AI/ML Engineer": [
        ("House Price Prediction System", "A regression pipeline with feature engineering and model comparison.", ["Python", "Pandas", "Machine Learning"], "Beginner"),
        ("Customer Churn Prediction", "A classification model with evaluation metrics and an explanation of key drivers.", ["Pandas", "Statistics", "Machine Learning"], "Intermediate"),
        ("Personalized Recommendation Engine", "Collaborative and content-based recommendations on a public dataset.", ["Python", "NumPy", "Machine Learning", "Git/GitHub"], "Intermediate"),
        ("Traffic Object Detection System", "A neural network that detects vehicles and pedestrians in images.", ["Python", "Deep Learning"], "Advanced"),
    ],
    "Data Scientist": [
        ("Student Performance Prediction", "Predict exam outcomes and study which factors matter most.", ["Python", "Statistics", "Machine Learning"], "Beginner"),
        ("Customer Segmentation System", "Cluster customers and visualize each segment's behavior.", ["Pandas", "Machine Learning", "Data Visualization"], "Intermediate"),
        ("Movie Recommendation System", "Suggest movies from ratings using similarity models.", ["Python", "Pandas", "Machine Learning"], "Intermediate"),
        ("Sales Prediction Dashboard", "Forecast sales from a SQL database and present it in a dashboard.", ["SQL", "Pandas", "Machine Learning", "Data Visualization"], "Advanced"),
    ],
    "Web Developer": [
        ("Portfolio Website", "A responsive multi-section site published on GitHub Pages.", ["HTML", "CSS", "Git/GitHub"], "Beginner"),
        ("Student Management System", "CRUD app with a database for students and courses.", ["HTML", "CSS", "Python", "SQL"], "Intermediate"),
        ("Real-Time Task Management Dashboard", "A drag-and-drop task board built with reusable components.", ["JavaScript", "React", "Git/GitHub"], "Intermediate"),
        ("E-Commerce Web Application", "Catalog, cart and checkout flow backed by a database.", ["HTML", "CSS", "JavaScript", "React", "SQL"], "Advanced"),
    ],
    "Data Analyst": [
        ("Sales Analytics Dashboard", "Monthly sales dashboard built from SQL queries and Excel data.", ["SQL", "Excel", "Power BI"], "Beginner"),
        ("Customer Churn Analysis", "Explore churn patterns and present findings with statistics.", ["Python", "Statistics", "Pandas"], "Intermediate"),
        ("Student Performance Dashboard", "Interactive charts on attendance, grades and trends.", ["Pandas", "Data Visualization"], "Intermediate"),
        ("Business KPI Dashboard", "A KPI dashboard fed by SQL with drill-down views.", ["SQL", "Data Visualization", "Power BI"], "Advanced"),
    ],
    "GenAI / Agentic AI Engineer": [
        ("Prompt Playground", "A small web tool to compare prompts and model outputs side by side.", ["Prompt Engineering", "LLM Integration", "REST APIs"], "Beginner"),
        ("AI Support Ticket Triage Service", "An API that classifies and routes support tickets, shipped in a container.", ["REST APIs", "LLM Integration", "Prompt Engineering", "Docker"], "Intermediate"),
        ("Document Q&A Chatbot", "A RAG chatbot that answers questions from your own PDFs with sources.", ["Python", "LLM Integration", "Vector Databases", "RAG"], "Intermediate"),
        ("Research Assistant Agent", "An agent that plans, searches, reads and writes a cited summary.", ["Agent Frameworks", "RAG", "Git/GitHub"], "Advanced"),
    ],
    "Full Stack Developer": [
        ("Blog Platform with Login", "Posts, comments and user accounts with a REST backend.", ["HTML", "CSS", "Node.js", "SQL", "REST APIs"], "Intermediate"),
        ("Task Manager with API", "React frontend that talks to your own Node.js API.", ["React", "Node.js", "REST APIs", "Git/GitHub"], "Intermediate"),
        ("Real-Time Chat App", "Multi-room chat with live updates.", ["JavaScript", "React", "Node.js"], "Intermediate"),
        ("Dockerized Full Stack Deployment", "Ship a full stack app in containers with a one-command setup.", ["Docker", "Node.js", "Git/GitHub"], "Advanced"),
    ],
}

# ============================================================
# SMALL HELPERS
# ============================================================

NEW_STUDENT = "— New student —"
LEVEL_EMOJI = {"Foundation": "🟢", "Core": "🟡", "Advanced": "🔴"}
DIFFICULTY_EMOJI = {"Beginner": "🟢", "Intermediate": "🟡", "Advanced": "🔴"}
PHASE_TITLES = [
    ("Foundation Building", "Build the core skills required for the target career."),
    ("Applied Learning", "Convert concepts into practical exercises and mini-projects."),
    ("Intermediate Development", "Combine multiple skills to solve realistic problems."),
    ("Advanced Specialisation", "Deepen expertise in the more demanding parts of the career."),
]

ALL_SKILLS = sorted({skill for skills in CAREER_SKILLS.values() for skill in skills})


def progress_key(career, skill):
    return f"progress_{career}_{skill}"


def note_key(career, skill):
    return f"note_{career}_{skill}"


def priority_index(skill):
    if skill in PRIORITY_ORDER:
        return PRIORITY_ORDER.index(skill)
    return len(PRIORITY_ORDER)


def flash(level, message):
    """Queue a message that is shown at the top of the next run."""
    st.session_state["flash"] = (level, message)


def show_flash():
    message = st.session_state.pop("flash", None)
    if message:
        level, text = message
        getattr(st, level)(text)


# ============================================================
# DECISION ENGINE
# ============================================================


def calculate_match(required_skills, known_skills):
    known_lower = {skill.lower() for skill in known_skills}
    matching = [s for s in required_skills if s.lower() in known_lower]
    missing = [s for s in required_skills if s.lower() not in known_lower]
    percentage = round(len(matching) / len(required_skills) * 100) if required_skills else 0
    return matching, missing, percentage


def order_missing_skills(missing):
    """Order skills so prerequisites always come first (ties use PRIORITY_ORDER)."""
    remaining = list(missing)
    ordered = []
    while remaining:
        ready = [
            skill for skill in remaining
            if not any(pre in remaining for pre in SKILL_INFO[skill]["prereqs"])
        ]
        if not ready:  # safety net against accidental cycles
            ready = remaining[:]
        chosen = min(ready, key=priority_index)
        ordered.append(chosen)
        remaining.remove(chosen)
    return ordered


def choose_priority(ordered_missing):
    return ordered_missing[0] if ordered_missing else "Advanced project development"


def build_roadmap(ordered_missing, hours_per_week):
    """Pack ordered skills into ~4-week blocks based on the weekly study time."""
    hours_per_week = max(int(hours_per_week), 1)

    if not ordered_missing:
        return [
            {
                "phase": "Phase 1",
                "title": "Build Portfolio Projects",
                "skills": ["Advanced project development"],
                "hours": 40,
                "weeks": math.ceil(40 / hours_per_week),
                "goal": "Demonstrate practical skills through portfolio projects.",
            },
            {
                "phase": "Phase 2",
                "title": "Career Preparation",
                "skills": ["Interview preparation", "Resume & LinkedIn", "GitHub portfolio"],
                "hours": 20,
                "weeks": math.ceil(20 / hours_per_week),
                "goal": "Prepare for internships and entry-level opportunities.",
            },
        ]

    capacity = hours_per_week * 4
    blocks, current, used = [], [], 0
    for skill in ordered_missing:
        effort = SKILL_INFO[skill]["hours"]
        if current and used + effort > capacity:
            blocks.append(current)
            current, used = [], 0
        current.append(skill)
        used += effort
    if current:
        blocks.append(current)

    phases = []
    for index, block in enumerate(blocks):
        title, goal = PHASE_TITLES[min(index, len(PHASE_TITLES) - 1)]
        hours = sum(SKILL_INFO[s]["hours"] for s in block)
        phases.append(
            {
                "phase": f"Phase {index + 1}",
                "title": title,
                "skills": block,
                "hours": hours,
                "weeks": math.ceil(hours / hours_per_week),
                "goal": goal,
            }
        )

    phases.append(
        {
            "phase": f"Phase {len(phases) + 1}",
            "title": "Portfolio & Career Readiness",
            "skills": ["Portfolio projects", "Resume & LinkedIn", "Interview preparation"],
            "hours": 20,
            "weeks": math.ceil(20 / hours_per_week),
            "goal": "Create portfolio evidence and prepare for real-world opportunities.",
        }
    )
    return phases


def prerequisite_warnings(required, done):
    """Skills marked complete whose prerequisites are not yet marked complete."""
    warnings = []
    for skill in required:
        if skill in done:
            for pre in SKILL_INFO[skill]["prereqs"]:
                if pre in required and pre not in done:
                    warnings.append((skill, pre))
    return warnings


def category_coverage(required, done):
    buckets = {}
    for skill in required:
        category = SKILL_INFO[skill]["category"]
        total, complete = buckets.get(category, (0, 0))
        buckets[category] = (total + 1, complete + (1 if skill in done else 0))
    return {
        category: round(complete / total * 100)
        for category, (total, complete) in buckets.items()
    }


def generate_next_actions(career, ordered_missing, done, hours_per_week):
    actions = []
    if ordered_missing:
        top = ordered_missing[0]
        effort = SKILL_INFO[top]["hours"]
        weeks = math.ceil(effort / max(hours_per_week, 1))
        actions.append(
            f"Focus first on {top} (about {effort} hours, roughly {weeks} week(s) "
            f"at your pace). It is the next skill whose prerequisites are covered for {career}."
        )
        actions.append(
            f"Complete one practical exercise for {top} before moving on: "
            f"{SKILL_INFO[top]['activity']}"
        )
        if len(ordered_missing) > 1:
            actions.append(f"After {top}, your next skill is {ordered_missing[1]}.")
    if done:
        strongest = sorted(done, key=priority_index)[0]
        actions.append(f"Strengthen your existing {strongest} knowledge by applying it in a project.")
    actions.append("Update your GitHub portfolio after each meaningful project milestone.")
    actions.append("Tick skills off as you complete them. The plan adapts instantly and you can save it.")
    return actions


def generate_adaptation_message(progress):
    if progress < 25:
        return ("Your current profile has several skill gaps. The agent prioritizes "
                "foundational skills before advanced topics.")
    if progress < 50:
        return ("You have started building the required foundation. The next step is "
                "to combine skills through practical projects.")
    if progress < 75:
        return ("Your skill coverage is improving. The roadmap now shifts toward "
                "intermediate projects and portfolio development.")
    if progress < 100:
        return ("You have strong coverage of the target skills. Focus on advanced "
                "projects, GitHub evidence and interview preparation.")
    return ("Your required skill list is covered. The next stage is advanced projects, "
            "specialization and career preparation.")


def generate_analysis(name, career, done, hours_per_week):
    required = CAREER_SKILLS[career]
    matching, missing, percentage = calculate_match(required, done)
    ordered = order_missing_skills(missing)
    roadmap = build_roadmap(ordered, hours_per_week)
    remaining_hours = sum(SKILL_INFO[s]["hours"] for s in ordered)
    total_weeks = sum(phase["weeks"] for phase in roadmap)
    eta = date.today() + timedelta(weeks=total_weeks)

    if percentage >= 80:
        summary = (f"{name}'s profile has strong alignment with the {career} career path. "
                   "The main focus should now be practical application, advanced projects "
                   "and portfolio development.")
    elif percentage >= 50:
        summary = (f"{name}'s profile shows moderate alignment with {career}. The agent "
                   "identified several important skills to develop before moving toward "
                   "advanced career preparation.")
    else:
        summary = (f"{name}'s profile is at an early stage for the {career} target. "
                   "The agent therefore prioritizes foundational skills and guided projects.")

    return {
        "name": name,
        "career": career,
        "required": required,
        "done": sorted(done, key=priority_index),
        "matching": matching,
        "missing": ordered,
        "percentage": percentage,
        "priority": choose_priority(ordered),
        "roadmap": roadmap,
        "remaining_hours": remaining_hours,
        "total_weeks": total_weeks,
        "eta": eta,
        "actions": generate_next_actions(career, ordered, done, hours_per_week),
        "adaptation": generate_adaptation_message(percentage),
        "summary": summary,
        "warnings": prerequisite_warnings(required, done),
        "coverage": category_coverage(required, done),
        "hours_per_week": hours_per_week,
    }


def weekly_plan(skill, hours_per_week):
    learn = round(hours_per_week * 0.5, 1)
    practice = round(hours_per_week * 0.4, 1)
    review = round(max(hours_per_week - learn - practice, 0), 1)
    info = SKILL_INFO[skill]
    return [
        ("📖 Learn", learn, f"Study {skill} using {info['resources'][0][0]}."),
        ("🛠️ Practice", practice, info["activity"]),
        ("🔁 Review", review, "Write short notes on what you learned and list open questions."),
    ]


def project_status(project_skills, done):
    missing = [skill for skill in project_skills if skill not in done]
    return (not missing), missing


def get_badges(done_count, total, percentage, has_saved, has_notes):
    badges = []
    if done_count >= 1:
        badges.append(("🥇", "First Step", "You completed your first skill."))
    if percentage >= 25:
        badges.append(("🌱", "Quarter Way", "25% of the required skills are covered."))
    if percentage >= 50:
        badges.append(("🚀", "Halfway There", "Half of the required skills are covered."))
    if percentage >= 75:
        badges.append(("🔥", "Almost There", "75% of the required skills are covered."))
    if total and done_count == total:
        badges.append(("🏆", "Career Ready", "Every required skill is complete."))
    if has_saved:
        badges.append(("💾", "Safe & Saved", "Your progress is stored in the database."))
    if has_notes:
        badges.append(("📝", "Note Taker", "You keep notes on your learning."))
    return badges


def build_report(data, profile, notes, projects_ready):
    lines = [
        f"# Career Navigator Report — {data['name']}",
        "",
        f"- **Target career:** {data['career']}",
        f"- **Report date:** {date.today().isoformat()}",
        f"- **Career match:** {data['percentage']}%",
        f"- **Skills completed:** {len(data['matching'])} / {len(data['required'])}",
        f"- **Study time:** {data['hours_per_week']} hours per week",
        f"- **Estimated completion:** {data['eta'].strftime('%d %b %Y')} "
        f"(about {data['total_weeks']} weeks)",
        "",
        "## Summary",
        data["summary"],
        "",
        "## Completed skills",
    ]
    lines += [f"- {s}" for s in data["matching"]] or ["- None yet"]
    lines += ["", "## Skill gaps (in learning order)"]
    lines += [
        f"- {s} — {SKILL_INFO[s]['level']}, ~{SKILL_INFO[s]['hours']} h"
        for s in data["missing"]
    ] or ["- None"]
    lines += ["", "## Roadmap"]
    for phase in data["roadmap"]:
        lines.append(
            f"- **{phase['phase']} — {phase['title']}** "
            f"({phase['weeks']} wk, {phase['hours']} h): {', '.join(phase['skills'])}"
        )
    lines += ["", "## Projects ready to build"]
    lines += [f"- {title}" for title in projects_ready] or ["- Complete more skills to unlock projects"]
    lines += ["", "## Next actions"]
    lines += [f"{i}. {action}" for i, action in enumerate(data["actions"], start=1)]
    saved_notes = {s: n for s, n in notes.items() if (n or "").strip()}
    if saved_notes:
        lines += ["", "## My notes"]
        for skill, note in saved_notes.items():
            lines += [f"**{skill}**", "", note.strip(), ""]
    return "\n".join(lines)


# ============================================================
# SESSION STATE DEFAULTS
# ============================================================

st.session_state.setdefault("analysis_ready", False)
st.session_state.setdefault("profile", None)
st.session_state.setdefault("name_input", "")
st.session_state.setdefault("career_select", list(CAREER_SKILLS.keys())[0])
st.session_state.setdefault("skills_select", [])
st.session_state.setdefault("hours_live", 6)
st.session_state.setdefault("returning_select", NEW_STUDENT)

# ============================================================
# CALLBACKS  (they run before the script reruns, so session state can be changed safely)
# ============================================================


def pick_returning_student():
    chosen = st.session_state.get("returning_select")
    if not chosen or chosen == NEW_STUDENT:
        return
    st.session_state["name_input"] = chosen
    settings = load_settings(chosen)
    career = st.session_state["career_select"]
    if settings:
        if settings["career"] in CAREER_SKILLS:
            career = settings["career"]
            st.session_state["career_select"] = career
        if settings["hours"]:
            st.session_state["hours_live"] = int(settings["hours"])
    saved = load_progress(chosen, career)
    st.session_state["skills_select"] = [
        skill for skill, done in saved.items() if done and skill in ALL_SKILLS
    ]


def run_analysis():
    name = st.session_state.get("name_input", "").strip()
    career = st.session_state["career_select"]
    chosen_skills = list(st.session_state.get("skills_select", []))

    if not name:
        flash("warning", "Please enter your name first.")
        return
    if not chosen_skills:
        flash("warning", "Please select at least one current skill so the navigator can calculate your skill gap.")
        return

    required = CAREER_SKILLS[career]
    saved = load_progress(name, career)
    saved_notes = load_notes(name, career)
    chosen_lower = {s.lower() for s in chosen_skills}

    for skill in required:
        st.session_state[progress_key(career, skill)] = (
            saved[skill] if skill in saved else skill.lower() in chosen_lower
        )
        st.session_state[note_key(career, skill)] = saved_notes.get(skill, "")

    _, _, initial_pct = calculate_match(required, chosen_skills)
    st.session_state["profile"] = {
        "name": name,
        "career": career,
        "initial_skills": chosen_skills,
        "initial_pct": initial_pct,
        "restored": bool(saved),
    }
    st.session_state["analysis_ready"] = True

    if saved:
        flash("success", "✅ Career analysis completed and previously saved progress was restored!")
    else:
        flash("success", "✅ Career profile analyzed successfully!")


def current_progress_map(profile):
    career = profile["career"]
    return {
        skill: bool(st.session_state.get(progress_key(career, skill), False))
        for skill in CAREER_SKILLS[career]
    }


def save_current():
    profile = st.session_state["profile"]
    career = profile["career"]
    notes = {
        skill: st.session_state.get(note_key(career, skill), "")
        for skill in CAREER_SKILLS[career]
    }
    save_progress(
        profile["name"],
        career,
        current_progress_map(profile),
        notes,
        st.session_state["hours_live"],
    )
    flash("success", "✅ Progress, notes and a history snapshot were saved.")


def delete_saved():
    profile = st.session_state["profile"]
    delete_progress(profile["name"], profile["career"])
    flash("success", "✅ Saved progress, notes and history were deleted from the database. "
                     "Your current on-screen selections are unchanged.")


def reset_to_initial():
    profile = st.session_state["profile"]
    career = profile["career"]
    initial_lower = {s.lower() for s in profile["initial_skills"]}
    for skill in CAREER_SKILLS[career]:
        st.session_state[progress_key(career, skill)] = skill.lower() in initial_lower
    flash("success", "✅ Progress reset to the skills you selected at the start. "
                     "Use Save to store this state.")


# ============================================================
# HEADER
# ============================================================

html_box(
    "hero",
    "<h1>🎯 Personalized Career & Skill Navigator</h1>",
    "<p>An agentic career guidance system that analyzes your skills, identifies gaps, "
    "and builds an adaptive, prerequisite-aware learning roadmap.</p>",
)

# ============================================================
# SIDEBAR
# ============================================================

students = list_students()

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
        6. Tick skills off as you learn
        7. Save progress and notes
        8. Reopen the app and continue
        """
    )

    st.divider()
    st.subheader("⚙️ Study Settings")
    st.slider(
        "Study hours per week",
        min_value=1,
        max_value=40,
        key="hours_live",
        help="Changes the roadmap phases and the estimated completion date instantly.",
    )

    st.divider()
    st.metric("Saved student profiles", len(students))
    if DB_FILE.exists():
        st.download_button(
            "⬇️ Download database backup",
            data=DB_FILE.read_bytes(),
            file_name=f"career_navigator_backup_{date.today().isoformat()}.db",
            mime="application/octet-stream",
            use_container_width=True,
        )

    st.info(
        "💡 This prototype uses a local decision engine and a SQLite database. "
        "No paid AI API is required."
    )

# ============================================================
# STUDENT PROFILE
# ============================================================

show_flash()

st.header("👤 Student Profile")

if students:
    st.selectbox(
        "Returning student (optional)",
        [NEW_STUDENT] + students,
        key="returning_select",
        on_change=pick_returning_student,
        help="Pick a saved student to pre-fill name, career, study hours and completed skills.",
    )

col1, col2 = st.columns(2)
with col1:
    st.text_input("Your Name", placeholder="Enter your name", key="name_input")
with col2:
    st.selectbox("Target Career", list(CAREER_SKILLS.keys()), key="career_select")

st.subheader("🧠 Current Skills")
st.multiselect(
    "Select the skills you currently know",
    ALL_SKILLS,
    key="skills_select",
    help="Select all skills you already have basic or practical knowledge of.",
)
st.caption(
    f"Selected {len(st.session_state['skills_select'])} skill(s). "
    "You can update this later and re-run the analysis."
)

st.button(
    "🚀 Analyze My Career",
    type="primary",
    use_container_width=True,
    on_click=run_analysis,
)

# ============================================================
# RESULTS
# ============================================================

if st.session_state["analysis_ready"] and st.session_state["profile"]:

    profile = st.session_state["profile"]
    career = profile["career"]
    required = CAREER_SKILLS[career]
    hours = st.session_state["hours_live"]

    # Everything below is computed from the live checkbox state.
    progress_map = current_progress_map(profile)
    done_set = {skill for skill, value in progress_map.items() if value}
    data = generate_analysis(profile["name"], career, done_set, hours)
    notes_map = {s: st.session_state.get(note_key(career, s), "") for s in required}

    saved_rows = load_progress(profile["name"], career)
    has_saved = bool(saved_rows)
    has_notes = any((n or "").strip() for n in notes_map.values())

    completed_count = len(data["matching"])
    remaining_count = len(required) - completed_count
    progress = data["percentage"]

    projects_ready = []
    for title, _desc, project_skills, _difficulty in PROJECTS.get(career, []):
        ready, _ = project_status(project_skills, done_set)
        if ready:
            projects_ready.append(title)

    st.divider()
    st.header("📊 Career Analysis")

    tabs = st.tabs(
        [
            "🏠 Overview",
            "🔎 Skill Gaps",
            "🗺️ Roadmap",
            "📈 Progress",
            "🛠️ Projects",
            "⚖️ Compare Careers",
            "📄 Report",
            "🤖 How It Works",
        ]
    )
    (tab_overview, tab_gaps, tab_roadmap, tab_progress,
     tab_projects, tab_compare, tab_report, tab_how) = tabs

    # --------------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------------
    with tab_overview:
        html_box("card", "<h3>Career Profile</h3>", f"<p>{esc(data['summary'])}</p>")

        m1, m2, m3, m4 = st.columns(4)
        delta = progress - profile["initial_pct"]
        m1.metric("Career Match", f"{progress}%", delta=f"{delta:+d}% since analysis" if delta else None)
        m2.metric("Matching Skills", completed_count)
        m3.metric("Skill Gaps", len(data["missing"]))
        m4.metric("Est. Completion", data["eta"].strftime("%d %b %Y"), help=f"About {data['total_weeks']} weeks at {hours} h/week")

        st.subheader("🎯 Recommended Next Priority")
        if data["missing"]:
            info = SKILL_INFO[data["priority"]]
            html_box(
                "priority",
                f"<h3>Focus on: {esc(data['priority'])}</h3>",
                f"<p>{esc(info['why'])}</p>",
                f"<span class='pill'>{LEVEL_EMOJI[info['level']]} {info['level']}</span>",
                f"<span class='pill'>~{info['hours']} hours</span>",
                f"<span class='pill'>{esc(info['category'])}</span>",
            )

            st.subheader("🗓️ This Week's Study Plan")
            for label, plan_hours, description in weekly_plan(data["priority"], hours):
                html_box(
                    "week-box",
                    f"<strong>{label} · {plan_hours} h</strong><br>",
                    f"<span class='small-text'>{esc(description)}</span>",
                )
        else:
            html_box(
                "priority",
                "<h3>Focus on: Advanced project development</h3>",
                "<p>All required skills are covered. Build projects, publish them and prepare for interviews.</p>",
            )

        left, right = st.columns([1, 1])
        with left:
            st.subheader("🧭 Skill Coverage by Category")
            coverage = data["coverage"]
            categories = list(coverage.keys())
            values = list(coverage.values())
            if PLOTLY_OK and len(categories) >= 3:
                fig = go.Figure(
                    go.Scatterpolar(
                        r=values + values[:1],
                        theta=categories + categories[:1],
                        fill="toself",
                        name="Coverage %",
                    )
                )
                fig.update_layout(
                    polar=dict(radialaxis=dict(range=[0, 100], visible=True)),
                    showlegend=False,
                    height=340,
                    margin=dict(l=40, r=40, t=20, b=20),
                )
                st.plotly_chart(fig)
            else:
                st.bar_chart(pd.DataFrame({"Coverage %": values}, index=categories))
        with right:
            st.subheader("🏅 Achievements")
            badges = get_badges(completed_count, len(required), progress, has_saved, has_notes)
            if badges:
                for icon, title, description in badges:
                    html_box(
                        "badge-card",
                        f"<strong>{icon} {esc(title)}</strong><br>",
                        f"<span class='small-text'>{esc(description)}</span>",
                    )
            else:
                st.write("Complete your first skill to earn a badge.")

        st.subheader("🔄 Current Adaptive Status")
        adaptation = generate_adaptation_message(progress)
        if progress >= 80:
            st.success("🚀 " + adaptation)
        elif progress >= 50:
            st.info("📚 " + adaptation)
        else:
            st.warning("🌱 " + adaptation)

        st.subheader("🚀 Recommended Next Actions")
        for index, action in enumerate(data["actions"], start=1):
            html_box("action-box", f"<strong>Step {index}</strong>", f"<p>{esc(action)}</p>")

    # --------------------------------------------------------
    # SKILL GAPS
    # --------------------------------------------------------
    with tab_gaps:
        st.subheader("✅ Matching Skills")
        if data["matching"]:
            cols = st.columns(2)
            for index, skill in enumerate(data["matching"]):
                with cols[index % 2]:
                    html_box(
                        "skill-match",
                        f"<strong>✓ {esc(skill)}</strong><br>",
                        "<span class='small-text'>Marked as completed in your profile</span>",
                    )
        else:
            st.info("No matching skills were detected for the selected career.")

        for skill, prerequisite in data["warnings"]:
            st.warning(
                f"You marked **{skill}** as complete, but its prerequisite "
                f"**{prerequisite}** is not marked yet. Consider reviewing it."
            )

        st.subheader("⚠️ Skill Gaps (in recommended learning order)")
        if data["missing"]:
            for order, skill in enumerate(data["missing"], start=1):
                info = SKILL_INFO[skill]
                pre_missing = [p for p in info["prereqs"] if p in data["missing"]]
                pre_text = (
                    f"<br><span class='small-text'>Learn first: {esc(', '.join(pre_missing))}</span>"
                    if pre_missing else ""
                )
                html_box(
                    "skill-gap",
                    f"<strong>{order}. ❌ {esc(skill)}</strong> ",
                    f"<span class='pill'>{LEVEL_EMOJI[info['level']]} {info['level']}</span>",
                    f"<span class='pill'>~{info['hours']} h</span><br>",
                    f"<span>{esc(info['why'])}</span><br>",
                    f"<span class='small-text'>Recommended activity: {esc(info['activity'])}</span>",
                    pre_text,
                )
                with st.expander(f"📚 Learning resources for {skill}"):
                    for label, url in info["resources"]:
                        st.markdown(f"- [{label}]({url})")
        else:
            st.success("🎉 No major skill gaps detected from the selected skill list.")

    # --------------------------------------------------------
    # ROADMAP
    # --------------------------------------------------------
    with tab_roadmap:
        st.subheader("🗺️ Adaptive Learning Roadmap")
        r1, r2, r3 = st.columns(3)
        r1.metric("Remaining effort", f"{data['remaining_hours']} h")
        r2.metric("Study pace", f"{hours} h / week")
        r3.metric("Estimated finish", data["eta"].strftime("%d %b %Y"), help=f"About {data['total_weeks']} weeks")
        st.caption("Change the study hours in the sidebar to see the plan adjust.")

        for phase in data["roadmap"]:
            html_box(
                "roadmap-box",
                f"<h3>{esc(phase['phase'])} — {esc(phase['title'])}</h3>",
                f"<p><strong>Skills:</strong> {esc(', '.join(phase['skills']))}</p>",
                f"<p><strong>Effort:</strong> {phase['hours']} hours · about {phase['weeks']} week(s)</p>",
                f"<p><strong>Goal:</strong> {esc(phase['goal'])}</p>",
            )

        roadmap_df = pd.DataFrame(
            [
                {
                    "Phase": p["phase"],
                    "Title": p["title"],
                    "Skills": ", ".join(p["skills"]),
                    "Hours": p["hours"],
                    "Weeks": p["weeks"],
                }
                for p in data["roadmap"]
            ]
        )
        st.dataframe(roadmap_df, hide_index=True)

    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------
    with tab_progress:
        st.subheader("📈 Skill Progress Tracking")
        st.caption(
            "Tick a skill when you complete it. Everything in the app updates instantly. "
            "Use Save to keep your progress, notes and history in the database."
        )

        cols = st.columns(2)
        for index, skill in enumerate(required):
            info = SKILL_INFO[skill]
            with cols[index % 2]:
                st.checkbox(
                    skill,
                    key=progress_key(career, skill),
                    help=f"{info['level']} · about {info['hours']} hours",
                )
                with st.expander("📝 Notes"):
                    st.text_area(
                        f"Notes for {skill}",
                        key=note_key(career, skill),
                        label_visibility="collapsed",
                        placeholder=f"What did you learn about {skill}? Links, questions, next steps…",
                        height=80,
                    )

        st.progress(progress / 100, text=f"Learning Progress: {progress}%")
        st.write(f"**{completed_count} / {len(required)} required skills completed**")

        st.subheader("💾 Save Progress")
        html_box(
            "save-box",
            "<strong>Persistent Progress</strong>",
            "<p>Your completed skills, notes and study pace are stored in the SQLite database. "
            "Each save also adds a point to your progress history.</p>",
        )

        b1, b2, b3 = st.columns(3)
        b1.button("💾 Save My Progress", type="primary", use_container_width=True,
                  on_click=save_current, key="btn_save")
        b2.button("↩️ Reset to Initial Skills", use_container_width=True,
                  on_click=reset_to_initial, key="btn_reset")
        b3.button("🗑️ Delete Saved Data", use_container_width=True,
                  on_click=delete_saved, key="btn_delete")

        st.subheader("🕒 Progress History")
        history_df = load_history(profile["name"], career)
        if history_df.empty:
            st.info("No saved snapshots yet. Press Save My Progress to start your history.")
        else:
            st.line_chart(history_df.set_index("Saved at")["Progress %"], height=250)
            st.dataframe(history_df.iloc[::-1], hide_index=True)

        st.subheader("📊 Dashboard")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Career Match", f"{data['percentage']}%")
        d2.metric("Skills Completed", f"{completed_count}/{len(required)}")
        d3.metric("Skills Remaining", remaining_count)
        d4.metric("Roadmap Progress", f"{progress}%")

        st.bar_chart(
            pd.DataFrame({"Skills": [completed_count, remaining_count]},
                         index=["Completed", "Remaining"]),
            height=260,
        )

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("✅ Completed Skills")
            if data["matching"]:
                for skill in data["matching"]:
                    st.success(f"✓ {skill}")
            else:
                st.write("No skills completed yet.")
        with c2:
            st.subheader("⏳ Remaining Skills")
            if data["missing"]:
                for skill in data["missing"]:
                    st.warning(f"• {skill}")
            else:
                st.success("🎉 All required skills completed!")

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------
    with tab_projects:
        st.subheader("🛠️ Recommended Projects")
        st.write(
            "Projects unlock as you complete the skills they need, so learning "
            "turns into portfolio evidence."
        )
        levels = st.multiselect(
            "Show difficulty",
            ["Beginner", "Intermediate", "Advanced"],
            default=["Beginner", "Intermediate", "Advanced"],
            key="difficulty_filter",
        )
        shown = 0
        for title, description, project_skills, difficulty in PROJECTS.get(career, []):
            if difficulty not in levels:
                continue
            shown += 1
            ready, missing_for_project = project_status(project_skills, done_set)
            status = (
                "<span class='pill'>✅ Ready to build</span>"
                if ready
                else f"<span class='pill'>🔒 Needs: {esc(', '.join(missing_for_project))}</span>"
            )
            html_box(
                "project-card",
                f"<strong>{esc(title)}</strong> ",
                f"<span class='pill'>{DIFFICULTY_EMOJI[difficulty]} {difficulty}</span><br>",
                f"<span>{esc(description)}</span><br>",
                f"<span class='small-text'>Skills: {esc(', '.join(project_skills))}</span><br>",
                status,
            )
        if shown == 0:
            st.info("No projects match the selected difficulty.")

    # --------------------------------------------------------
    # COMPARE CAREERS
    # --------------------------------------------------------
    with tab_compare:
        st.subheader("⚖️ How Do Your Skills Fit Other Careers?")
        st.caption(
            "Uses the skills you selected at the start plus everything you have ticked off since."
        )
        known_all = set(profile["initial_skills"]) | done_set
        rows = []
        for other_career, other_required in CAREER_SKILLS.items():
            _, other_missing, other_pct = calculate_match(other_required, known_all)
            effort = sum(SKILL_INFO[s]["hours"] for s in other_missing)
            rows.append(
                {
                    "Career": other_career,
                    "Match %": other_pct,
                    "Skills missing": len(other_missing),
                    "Effort left (h)": effort,
                    "Est. weeks": math.ceil(effort / max(hours, 1)) if effort else 0,
                }
            )
        compare_df = pd.DataFrame(rows).sort_values("Match %", ascending=False)
        best = compare_df.iloc[0]
        st.success(f"Best current fit: **{best['Career']}** ({best['Match %']}% match).")
        st.bar_chart(compare_df.set_index("Career")["Match %"], height=300)
        st.dataframe(compare_df, hide_index=True)

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------
    with tab_report:
        st.subheader("📄 Export Your Report")
        report_md = build_report(data, profile, notes_map, projects_ready)

        status_df = pd.DataFrame(
            [
                {
                    "Skill": skill,
                    "Category": SKILL_INFO[skill]["category"],
                    "Level": SKILL_INFO[skill]["level"],
                    "Est. hours": SKILL_INFO[skill]["hours"],
                    "Prerequisites": ", ".join(SKILL_INFO[skill]["prereqs"]) or "—",
                    "Status": "Completed" if skill in done_set else "Remaining",
                }
                for skill in required
            ]
        )
        report_json = json.dumps(
            {
                "student": data["name"],
                "career": career,
                "generated": datetime.now().isoformat(timespec="seconds"),
                "career_match_percent": data["percentage"],
                "hours_per_week": hours,
                "estimated_completion": data["eta"].isoformat(),
                "completed_skills": data["matching"],
                "remaining_skills_in_order": data["missing"],
                "roadmap": data["roadmap"],
                "projects_ready": projects_ready,
                "notes": {s: n for s, n in notes_map.items() if (n or "").strip()},
            },
            indent=2,
        )
        csv_buffer = io.StringIO()
        status_df.to_csv(csv_buffer, index=False)

        safe_name = "".join(c if c.isalnum() else "_" for c in data["name"]).strip("_") or "student"
        e1, e2, e3 = st.columns(3)
        e1.download_button("⬇️ Markdown report", report_md,
                           file_name=f"{safe_name}_career_report.md",
                           mime="text/markdown", use_container_width=True)
        e2.download_button("⬇️ Skills CSV", csv_buffer.getvalue(),
                           file_name=f"{safe_name}_skills.csv",
                           mime="text/csv", use_container_width=True)
        e3.download_button("⬇️ Full JSON", report_json,
                           file_name=f"{safe_name}_career_data.json",
                           mime="application/json", use_container_width=True)

        with st.expander("Preview report", expanded=True):
            st.markdown(report_md)
        st.dataframe(status_df, hide_index=True)

    # --------------------------------------------------------
    # HOW IT WORKS
    # --------------------------------------------------------
    with tab_how:
        st.subheader("❓ Why These Recommendations?")
        explanation = [
            ("1. Target Career", "Your selected career defines the required skill set."),
            ("2. Current Skill Profile", "The skills you know or have ticked off are compared with the requirements."),
            ("3. Skill Gap Detection", "Required skills missing from your profile become skill gaps."),
            ("4. Prerequisite Ordering", "Skills are ordered so that prerequisites always come first, then by foundational priority."),
            ("5. Roadmap Generation", "Ordered skills are packed into roughly four-week phases using your weekly study time."),
            ("6. Project Unlocking", "Projects become ready when every skill they need is complete."),
            ("7. Live Adaptation", "Ticking or unticking a skill instantly updates the priority, roadmap, next actions and career comparison."),
            ("8. Persistent Storage", "Progress, notes, study pace and history live in a local SQLite database."),
        ]
        for title, text in explanation:
            html_box("card", f"<strong>{esc(title)}</strong><br>", f"<span>{esc(text)}</span>")

        st.subheader("🤖 Agentic AI Decision Pipeline")
        pipeline = [
            ("1️⃣", "Profile Understanding", "Reads the student's target career and current skill profile."),
            ("2️⃣", "Career Skill Mapping", "Maps the selected career to the skills required for it."),
            ("3️⃣", "Skill Gap Detection", "Compares existing skills against required skills."),
            ("4️⃣", "Priority Decision", "Selects the next skill using prerequisites and foundational priority."),
            ("5️⃣", "Roadmap Planning", "Creates progressive learning phases sized to the student's schedule."),
            ("6️⃣", "Project Recommendation", "Suggests projects and unlocks them when the skills are ready."),
            ("7️⃣", "Progress Adaptation", "Updates every recommendation when progress changes."),
            ("8️⃣", "Persistent Memory", "Stores progress, notes and history for later retrieval."),
        ]
        for icon, title, description in pipeline:
            html_box("agent-step", f"<h4>{icon} {esc(title)}</h4>", f"<p>{esc(description)}</p>")

    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------
    st.divider()
    st.success("🟢 Career Navigator is running with local decision engine + SQLite persistence.")
    st.caption("No OpenAI API key, paid API credits or external AI service is required.")
    st.caption(f"Student progress is stored in: {DB_FILE.name}")

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.markdown(
    '<div style="text-align:center;color:#64748b;padding:10px;">'
    "<strong>Personalized Career & Skill Navigator Agent</strong><br>"
    "Agentic AI • Personalized Learning • Skill Gap Analysis • "
    "Adaptive Roadmap • Persistent Progress"
    "</div>",
    unsafe_allow_html=True,
)
