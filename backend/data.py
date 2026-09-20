"""Knowledge base for the Career & Skill Navigator.

Contains:
  * SKILLS      - skill library (category, prerequisites, search aliases)
  * RESOURCES   - learning resources generated for every skill and level
  * CAREERS     - target roles with weighted skill requirements
  * MARKET_PRESETS - example "changing requirement" updates for demos

The content is curated by hand for the prototype. Course names and providers
should be re-checked before real use because catalogues change over time.
"""
from __future__ import annotations

import re
from collections import Counter
from urllib.parse import quote_plus

# --------------------------------------------------------------------------
# Constants shared by backend and UI
# --------------------------------------------------------------------------
LEVELS = {0: "None", 1: "Beginner", 2: "Intermediate", 3: "Advanced"}

INTEREST_OPTIONS = [
    "Data & Analytics",
    "Machine Learning & AI",
    "Web Development",
    "Cloud & DevOps",
    "Cybersecurity",
]

STAGES = ["Student", "Recent graduate", "Working professional", "Career switcher"]
EDUCATION_LEVELS = [
    "High school",
    "Diploma",
    "Bachelor's (in progress)",
    "Bachelor's",
    "Master's",
    "PhD",
    "Self-taught / bootcamp",
]
LEARNING_STYLES = ["Mixed (balanced)", "Structured courses", "Hands-on projects", "Certifications"]


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# --------------------------------------------------------------------------
# Skill library
#   l1 / l2 : (title, provider, hours)   - a course for each level
#   project : (title, hours)             - level-2 portfolio project
#   l3      : (title, hours, type)       - level-3 project or certification
# Every level also gets one generic practice activity (see _build below).
# --------------------------------------------------------------------------
_RAW_SKILLS: dict[str, dict] = {
    # ---- Programming ----
    "Python": dict(
        category="Programming", prereqs=[], aliases=["py", "python3"],
        l1=("Python for Everybody", "Coursera (University of Michigan)", 30),
        l2=("Intermediate Python: OOP, modules and testing", "Real Python", 20),
        project=("Command-line expense tracker with file storage and unit tests", 12),
        l3=("Build and publish a Python package with tests and CI", 15, "project"),
    ),
    "Data Structures & Algorithms": dict(
        category="Programming", prereqs=["Python"],
        aliases=["data structures", "algorithms", "dsa", "leetcode"],
        l1=("NeetCode roadmap: core data structures", "NeetCode", 25),
        l2=("Algorithms Specialization", "Coursera (Stanford)", 40),
        project=("Autocomplete engine built on a trie with benchmarks", 10),
        l3=("Mock-interview project: solve 75 curated problems and document patterns", 40, "project"),
    ),
    "JavaScript": dict(
        category="Web Development", prereqs=[], aliases=["js", "typescript", "ecmascript"],
        l1=("JavaScript Algorithms and Data Structures", "freeCodeCamp", 40),
        l2=("The Modern JavaScript Tutorial", "javascript.info", 30),
        project=("Interactive quiz app using the DOM and the fetch API", 12),
        l3=("Real-time chat app with WebSockets", 20, "project"),
    ),
    "Git & GitHub": dict(
        category="Programming", prereqs=[], aliases=["git", "github", "gitlab", "version control"],
        l1=("Pro Git, chapters 1 to 3", "git-scm.com", 6),
        l2=("Collaboration courses", "GitHub Skills", 8),
        project=("Contribute a pull request to an open-source repository", 8),
        l3=("Set up branch protection, code review and release tagging", 6, "project"),
    ),
    # ---- Data & Analytics ----
    "SQL": dict(
        category="Data & Analytics", prereqs=[],
        aliases=["mysql", "postgresql", "postgres", "sqlite", "t-sql"],
        l1=("Intro to SQL", "Kaggle Learn", 5),
        l2=("Advanced SQL", "Kaggle Learn", 10),
        project=("Design a normalised database and write analytical queries for an e-commerce dataset", 12),
        l3=("Query optimisation with indexes and EXPLAIN on a 1M-row dataset", 12, "project"),
    ),
    "Statistics": dict(
        category="Data & Analytics", prereqs=[],
        aliases=["probability", "hypothesis testing", "regression analysis"],
        l1=("Statistics and Probability", "Khan Academy", 25),
        l2=("Statistics with Python Specialization", "Coursera (University of Michigan)", 40),
        project=("A/B test analysis with hypothesis testing on a public dataset", 10),
        l3=("Bayesian and regression modelling case study", 20, "project"),
    ),
    "Excel": dict(
        category="Data & Analytics", prereqs=[], aliases=["spreadsheets", "google sheets", "pivot tables"],
        l1=("Excel Skills for Business: Essentials", "Coursera (Macquarie University)", 20),
        l2=("Excel Skills for Business: Intermediate", "Coursera (Macquarie University)", 25),
        project=("Sales dashboard with PivotTables, lookups and slicers", 8),
        l3=("Microsoft Office Specialist: Excel exam", 20, "certification"),
    ),
    "Data Wrangling": dict(
        category="Data & Analytics", prereqs=["Python"],
        aliases=["pandas", "numpy", "data cleaning", "data wrangling", "etl"],
        l1=("Pandas", "Kaggle Learn", 4),
        l2=("Data Analysis with Python", "freeCodeCamp", 20),
        project=("Clean and analyse a messy public dataset", 12),
        l3=("Reproducible ETL pipeline with pandas and tests", 15, "project"),
    ),
    "Data Visualization": dict(
        category="Data & Analytics", prereqs=["Python"],
        aliases=["matplotlib", "seaborn", "plotly", "data visualisation", "charts"],
        l1=("Data Visualization", "Kaggle Learn", 4),
        l2=("Data Visualization with Python", "freeCodeCamp", 20),
        project=("Interactive dashboard on a public dataset", 12),
        l3=("Data-story project: publish a five-chart narrative", 12, "project"),
    ),
    "BI Tools": dict(
        category="Data & Analytics", prereqs=["SQL"],
        aliases=["power bi", "powerbi", "tableau", "looker", "business intelligence"],
        l1=("Get started with Power BI", "Microsoft Learn", 8),
        l2=("Tableau Public training videos", "Tableau", 12),
        project=("Executive KPI dashboard published to Tableau Public", 12),
        l3=("PL-300: Microsoft Power BI Data Analyst exam", 30, "certification"),
    ),
    # ---- Machine Learning & AI ----
    "Math for ML": dict(
        category="Machine Learning & AI", prereqs=[],
        aliases=["linear algebra", "calculus", "math for machine learning"],
        l1=("Essence of Linear Algebra", "3Blue1Brown", 5),
        l2=("Mathematics for Machine Learning Specialization", "Coursera (Imperial College London)", 50),
        project=("Implement linear regression, PCA and gradient descent from scratch with NumPy", 10),
        l3=("Derive and implement backpropagation from scratch", 15, "project"),
    ),
    "Machine Learning": dict(
        category="Machine Learning & AI", prereqs=["Python", "Statistics"],
        aliases=["scikit-learn", "sklearn", "ml", "predictive modelling", "xgboost"],
        l1=("Machine Learning Specialization", "Coursera (DeepLearning.AI, Stanford)", 50),
        l2=("Intermediate Machine Learning", "Kaggle Learn", 10),
        project=("End-to-end tabular ML project with a Kaggle dataset", 20),
        l3=("Kaggle competition with feature engineering and ensembling", 30, "project"),
    ),
    "Deep Learning": dict(
        category="Machine Learning & AI", prereqs=["Machine Learning", "Math for ML"],
        aliases=["pytorch", "tensorflow", "keras", "neural networks", "cnn", "computer vision"],
        l1=("Intro to Deep Learning", "Kaggle Learn", 4),
        l2=("Deep Learning Specialization", "Coursera (DeepLearning.AI)", 60),
        project=("Image classifier with transfer learning in PyTorch", 15),
        l3=("Fine-tune a research-paper model and document the results", 30, "project"),
    ),
    "Generative AI & LLMs": dict(
        category="Machine Learning & AI", prereqs=["Python", "Machine Learning"],
        aliases=["llm", "llms", "generative ai", "langchain", "rag", "prompt engineering", "openai", "nlp"],
        l1=("Generative AI for Everyone", "Coursera (DeepLearning.AI)", 6),
        l2=("LLM Course", "Hugging Face", 25),
        project=("Retrieval-augmented chatbot over your own documents", 15),
        l3=("Deploy an LLM app with evaluation, guardrails and monitoring", 25, "project"),
    ),
    "MLOps": dict(
        category="Machine Learning & AI", prereqs=["Python", "Docker", "Git & GitHub"],
        aliases=["mlflow", "kubeflow", "model deployment", "ml pipelines"],
        l1=("Made With ML", "Anyscale", 25),
        l2=("MLOps Zoomcamp", "DataTalksClub", 50),
        project=("Track experiments with MLflow and serve a model with FastAPI", 15),
        l3=("Deploy a model with CI/CD and monitoring on a cloud platform", 25, "project"),
    ),
    # ---- Web Development ----
    "HTML & CSS": dict(
        category="Web Development", prereqs=[], aliases=["html", "html5", "css", "css3", "tailwind", "bootstrap"],
        l1=("Responsive Web Design", "freeCodeCamp", 30),
        l2=("Learn CSS", "web.dev", 15),
        project=("Responsive portfolio website deployed on GitHub Pages", 12),
        l3=("Accessible multi-page site built on a design system, with a WCAG audit", 15, "project"),
    ),
    "React": dict(
        category="Web Development", prereqs=["JavaScript", "HTML & CSS"],
        aliases=["reactjs", "react.js", "next.js", "nextjs", "redux"],
        l1=("Learn React", "react.dev", 12),
        l2=("Full Stack Open, parts 1 and 2", "University of Helsinki", 40),
        project=("Task manager single-page app with routing and state management", 20),
        l3=("Production-grade React app with tests and performance tuning", 25, "project"),
    ),
    "Node.js & REST APIs": dict(
        category="Web Development", prereqs=["JavaScript"],
        aliases=["node.js", "nodejs", "node", "express", "rest api", "rest apis", "flask", "fastapi", "django"],
        l1=("Introduction to Node.js", "nodejs.org", 8),
        l2=("Back End Development and APIs", "freeCodeCamp", 30),
        project=("REST API with JWT authentication and PostgreSQL", 20),
        l3=("Scalable API with caching, rate limiting and OpenAPI docs", 20, "project"),
    ),
    # ---- Cloud & DevOps ----
    "Linux": dict(
        category="Cloud & DevOps", prereqs=[], aliases=["bash", "ubuntu", "shell scripting", "command line"],
        l1=("Linux Journey", "linuxjourney.com", 15),
        l2=("Introduction to Linux (LFS101)", "Linux Foundation on edX", 40),
        project=("Automate backups and log rotation with Bash scripts and cron", 8),
        l3=("Linux Foundation Certified IT Associate exam", 30, "certification"),
    ),
    "Docker": dict(
        category="Cloud & DevOps", prereqs=["Linux"], aliases=["containers", "containerisation", "docker compose"],
        l1=("Get started with Docker", "Docker Docs", 6),
        l2=("Docker Compose and multi-stage builds", "Docker Docs", 8),
        project=("Containerise a full-stack app with Docker Compose", 10),
        l3=("Slim, secure production images with vulnerability scanning", 10, "project"),
    ),
    "Cloud Computing": dict(
        category="Cloud & DevOps", prereqs=["Linux"],
        aliases=["aws", "azure", "gcp", "google cloud", "cloud"],
        l1=("AWS Cloud Practitioner Essentials", "AWS Skill Builder", 6),
        l2=("Ultimate AWS Certified Solutions Architect Associate", "Udemy (Stephane Maarek)", 27),
        project=("Deploy a three-tier web app on AWS with VPC, EC2, RDS and S3", 15),
        l3=("AWS Certified Solutions Architect Associate exam", 30, "certification"),
    ),
    "CI/CD": dict(
        category="Cloud & DevOps", prereqs=["Git & GitHub"],
        aliases=["cicd", "ci/cd", "jenkins", "github actions", "continuous integration"],
        l1=("GitHub Actions quickstart", "GitHub Docs", 4),
        l2=("Automate your workflow with GitHub Actions", "GitHub Skills", 8),
        project=("Pipeline that tests, builds an image and deploys on every push", 10),
        l3=("Blue/green or canary deployment pipeline with rollback", 15, "project"),
    ),
    "Kubernetes": dict(
        category="Cloud & DevOps", prereqs=["Docker"], aliases=["k8s", "helm", "kubectl"],
        l1=("Kubernetes Basics tutorial", "kubernetes.io", 6),
        l2=("Introduction to Kubernetes (LFS158x)", "Linux Foundation on edX", 30),
        project=("Deploy a multi-service app on a local Kubernetes cluster", 15),
        l3=("Certified Kubernetes Administrator (CKA) exam", 60, "certification"),
    ),
    "Infrastructure as Code": dict(
        category="Cloud & DevOps", prereqs=["Cloud Computing", "Git & GitHub"],
        aliases=["terraform", "iac", "ansible", "cloudformation"],
        l1=("Get started with Terraform tutorials", "HashiCorp Developer", 6),
        l2=("Terraform Associate study guide", "HashiCorp Developer", 15),
        project=("Provision a VPC, EC2 and RDS stack with Terraform modules", 12),
        l3=("HashiCorp Certified: Terraform Associate exam", 20, "certification"),
    ),
    # ---- Cybersecurity ----
    "Networking": dict(
        category="Cybersecurity", prereqs=[], aliases=["tcp/ip", "tcp ip", "wireshark", "computer networks", "dns"],
        l1=("Networking Basics", "Cisco Networking Academy", 20),
        l2=("The Bits and Bytes of Computer Networking", "Coursera (Google)", 25),
        project=("Home lab: segment a network and analyse traffic in Wireshark", 10),
        l3=("CompTIA Network+ exam", 40, "certification"),
    ),
    "Security Fundamentals": dict(
        category="Cybersecurity", prereqs=["Networking"],
        aliases=["cybersecurity", "cyber security", "information security", "infosec", "security+"],
        l1=("Pre Security learning path", "TryHackMe", 15),
        l2=("CompTIA Security+ video course", "Professor Messer", 30),
        project=("Threat-model a small web app with STRIDE and write a report", 10),
        l3=("CompTIA Security+ exam", 40, "certification"),
    ),
    "Ethical Hacking": dict(
        category="Cybersecurity", prereqs=["Networking", "Linux", "Security Fundamentals"],
        aliases=["pentesting", "penetration testing", "metasploit", "ctf", "burp suite", "red team"],
        l1=("Bandit wargame", "OverTheWire", 10),
        l2=("Jr Penetration Tester path", "TryHackMe", 40),
        project=("Write up 10 capture-the-flag machines from TryHackMe or Hack The Box", 25),
        l3=("eJPT junior penetration tester exam", 40, "certification"),
    ),
    "Incident Response": dict(
        category="Cybersecurity", prereqs=["Security Fundamentals", "Networking"],
        aliases=["siem", "splunk", "soc", "forensics", "blue team", "threat detection"],
        l1=("SOC Level 1 learning path", "TryHackMe", 30),
        l2=("Computer Security Incident Handling Guide (SP 800-61)", "NIST", 8),
        project=("Build a SIEM lab with Wazuh and investigate simulated attack logs", 20),
        l3=("Blue Team Level 1 (BTL1) exam", 40, "certification"),
    ),
    # ---- Professional skills ----
    "Communication": dict(
        category="Professional Skills", prereqs=[],
        aliases=["public speaking", "presentation", "presentations", "technical writing", "teamwork", "stakeholder"],
        l1=("Improving Communication Skills", "Coursera (University of Pennsylvania)", 15),
        l2=("Technical Writing One", "Google Developers", 6),
        project=("Record a 10-minute technical talk about one of your projects", 6),
        l3=("Publish a three-article technical blog series and present at a meetup", 20, "project"),
    ),
}


def _build() -> tuple[dict, dict, dict]:
    skills: dict[str, dict] = {}
    resources: dict[str, dict] = {}
    by_skill: dict[str, list] = {}
    for name, raw in _RAW_SKILLS.items():
        sid = slug(name)
        skills[name] = {
            "category": raw["category"],
            "prereqs": list(raw["prereqs"]),
            "aliases": [name.lower(), *raw.get("aliases", [])],
        }
        l3_title, l3_hours, l3_type = raw["l3"]
        specs = [
            (1, "course", raw["l1"][0], raw["l1"][1], raw["l1"][2]),
            (1, "activity", f"Practice set: 15 beginner exercises in {name}", "Self-practice", 4),
            (2, "course", raw["l2"][0], raw["l2"][1], raw["l2"][2]),
            (2, "project", raw["project"][0], "Portfolio project", raw["project"][1]),
            (3, l3_type, l3_title, "Certification exam" if l3_type == "certification" else "Portfolio project", l3_hours),
            (3, "activity", f"Teach-back: write a post or give a short talk on advanced {name}", "Self-practice", 4),
        ]
        per_level = Counter(level for level, *_ in specs)
        by_skill[name] = []
        for level, rtype, title, provider, hours in specs:
            rid = f"{sid}-l{level}-{rtype}"
            link = None
            if rtype in ("course", "certification"):
                link = "https://www.google.com/search?q=" + quote_plus(f"{title} {provider}")
            res = {
                "id": rid, "skill": name, "level": level, "type": rtype,
                "title": title, "provider": provider, "hours": hours, "link": link,
                # Finishing every resource of a level adds exactly one full level.
                "gain": round(1 / per_level[level], 3),
            }
            resources[rid] = res
            by_skill[name].append(res)
    return skills, resources, by_skill


SKILLS, RESOURCES, RESOURCES_BY_SKILL = _build()

# --------------------------------------------------------------------------
# Careers: skill -> (importance 1-5, required level 1-3)
# --------------------------------------------------------------------------
CAREERS: dict[str, dict] = {
    "Data Analyst": {
        "description": "Turns raw business data into clear answers using SQL, spreadsheets and dashboards.",
        "interests": ["Data & Analytics"],
        "requirements": {
            "SQL": (5, 2), "Excel": (4, 2), "Data Visualization": (5, 2), "BI Tools": (4, 2),
            "Statistics": (4, 2), "Data Wrangling": (4, 2), "Python": (3, 2), "Communication": (4, 2),
        },
        "capstone": ("Business analytics case study: raw data to SQL to dashboard to recommendations deck", 30),
        "certifications": ["Google Data Analytics Professional Certificate", "Microsoft PL-300: Power BI Data Analyst"],
    },
    "Data Scientist": {
        "description": "Builds statistical and machine-learning models that predict outcomes and guide decisions.",
        "interests": ["Data & Analytics", "Machine Learning & AI"],
        "requirements": {
            "Python": (5, 3), "Statistics": (5, 3), "Machine Learning": (5, 3), "Data Wrangling": (4, 3),
            "SQL": (4, 2), "Data Visualization": (4, 2), "Math for ML": (3, 2), "Git & GitHub": (3, 2),
            "Communication": (4, 2), "Deep Learning": (2, 1),
        },
        "capstone": ("End-to-end data science project: problem framing, modelling, evaluation and a written report", 40),
        "certifications": ["IBM Data Science Professional Certificate", "Google Advanced Data Analytics Certificate"],
    },
    "Machine Learning Engineer": {
        "description": "Takes models from notebooks to reliable, monitored production systems.",
        "interests": ["Machine Learning & AI"],
        "requirements": {
            "Python": (5, 3), "Machine Learning": (5, 3), "Deep Learning": (4, 2), "Math for ML": (4, 2),
            "MLOps": (4, 2), "Docker": (3, 2), "Git & GitHub": (3, 2), "SQL": (3, 2),
            "Generative AI & LLMs": (3, 2), "Data Structures & Algorithms": (3, 2), "Cloud Computing": (3, 2),
        },
        "capstone": ("Production ML service: trained model, API, container, CI/CD and monitoring dashboard", 45),
        "certifications": ["Google Cloud Professional Machine Learning Engineer", "AWS Certified Machine Learning Engineer Associate"],
    },
    "Full-Stack Web Developer": {
        "description": "Designs and ships complete web applications, from the interface to the database.",
        "interests": ["Web Development"],
        "requirements": {
            "HTML & CSS": (5, 3), "JavaScript": (5, 3), "React": (5, 2), "Node.js & REST APIs": (5, 2),
            "SQL": (4, 2), "Git & GitHub": (4, 2), "Data Structures & Algorithms": (3, 2),
            "Communication": (3, 2), "Docker": (2, 1), "CI/CD": (2, 1),
        },
        "capstone": ("Deployed full-stack product with authentication, database, tests and a live URL", 45),
        "certifications": ["Meta Front-End Developer Professional Certificate", "Meta Back-End Developer Professional Certificate"],
    },
    "Cloud & DevOps Engineer": {
        "description": "Automates infrastructure and delivery so software ships quickly and stays reliable.",
        "interests": ["Cloud & DevOps"],
        "requirements": {
            "Linux": (5, 3), "Cloud Computing": (5, 3), "Docker": (5, 3), "CI/CD": (5, 2),
            "Kubernetes": (4, 2), "Infrastructure as Code": (4, 2), "Networking": (4, 2),
            "Git & GitHub": (4, 2), "Python": (3, 2), "Communication": (3, 2),
        },
        "capstone": ("Infrastructure-as-code platform: Terraform, Kubernetes, CI/CD and monitoring for a sample app", 45),
        "certifications": ["AWS Certified Solutions Architect Associate", "Certified Kubernetes Administrator (CKA)", "HashiCorp Terraform Associate"],
    },
    "Cybersecurity Analyst": {
        "description": "Detects, investigates and prevents attacks against systems and data.",
        "interests": ["Cybersecurity"],
        "requirements": {
            "Security Fundamentals": (5, 3), "Networking": (5, 2), "Linux": (4, 2), "Incident Response": (5, 2),
            "Ethical Hacking": (3, 2), "Python": (3, 2), "Communication": (3, 2), "Cloud Computing": (2, 1),
        },
        "capstone": ("Security operations lab: monitor, detect and write an incident report for a simulated attack", 35),
        "certifications": ["CompTIA Security+", "Google Cybersecurity Certificate", "Blue Team Level 1 (BTL1)"],
    },
}

# Example requirement changes used to demonstrate adaptability.
MARKET_PRESETS = [
    {"career": "Data Analyst", "skill": "Generative AI & LLMs", "importance": 3, "required": 1,
     "note": "Simulated update: employers now ask for AI-assistant tooling in analytics work."},
    {"career": "Data Scientist", "skill": "Generative AI & LLMs", "importance": 4, "required": 2,
     "note": "Simulated update: LLM application experience is now expected."},
    {"career": "Machine Learning Engineer", "skill": "MLOps", "importance": 5, "required": 3,
     "note": "Simulated update: production deployment skill is now the main hiring filter."},
    {"career": "Full-Stack Web Developer", "skill": "Generative AI & LLMs", "importance": 3, "required": 1,
     "note": "Simulated update: most products now integrate LLM APIs."},
    {"career": "Cloud & DevOps Engineer", "skill": "Kubernetes", "importance": 5, "required": 3,
     "note": "Simulated update: Kubernetes depth is now expected."},
    {"career": "Cybersecurity Analyst", "skill": "Cloud Computing", "importance": 4, "required": 2,
     "note": "Simulated update: cloud security is now a core requirement."},
]

DEMO_PROFILE = {
    "name": "Demo Student",
    "education": "Bachelor's (in progress)",
    "field": "Computer Science",
    "stage": "Student",
    "experience_years": 0.5,
    "interests": ["Data & Analytics", "Machine Learning & AI"],
    "skills": {"Python": 2, "SQL": 1, "Statistics": 1, "Git & GitHub": 1, "Excel": 2, "Communication": 2},
    "target_career": "Data Scientist",
    "custom_career": None,
    "weekly_hours": 10,
    "learning_style": "Hands-on projects",
}
