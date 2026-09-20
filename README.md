# Personalized Career & Skill Navigator Agent

An adaptive career-guidance app. It builds a structured profile, compares the user's skills with a target role, ranks the skill gaps, generates a phased learning roadmap and **re-plans every time the user makes progress or the role's requirements change**. Every recommendation comes with a plain-language explanation.

Built for the DSSA 24-Hour Hackathon (Problem 02).

## How each core requirement is met

| Requirement | Where it lives |
|---|---|
| Structured profile (education, skills, interests, experience, goals) | `ui/profile.py`, saved by `backend/database.py` |
| Select or define a target career | 6 built-in roles plus "Define my own role" (`career_engine.resolve_career`) |
| Skills required for the career | `backend/data.py` (weighted requirements, prerequisites auto-added) |
| Compare current vs target, find and prioritise gaps | `career_engine.compute_skill_gaps` |
| Personalised roadmap | `roadmap.generate_roadmap` (3 phases, week-by-week schedule from weekly hours) |
| Courses, projects, certifications, activities | `recommendations.select_resources` (learning style aware) |
| Track completed activities and update the roadmap | "Mark complete" writes to SQLite; roadmap is rebuilt from the new state |
| Adapt to progress and changing requirements | Progress raises skill levels; "Change the role's requirements" and fast-track mode re-plan instantly |
| Explanations | `explain_gap`, `explain_resource`, and the "How your plan has adapted" panel |

## How the scoring works

* Skills are rated 0 to 3 (None, Beginner, Intermediate, Advanced).
* **Effective level** = self-rated level + gains from completed activities. Finishing every activity of one level adds exactly one level.
* **Gap** = required level - effective level. Status is *Missing*, *Underdeveloped* or *Met*.
* **Priority score** = importance (1-5) x gap x (1 + 0.25 x number of skills it unlocks), plus a 15% boost when it matches the user's interests.
* **Prerequisites** (for example Statistics for Machine Learning) are added automatically as foundation gaps and scheduled first.
* **Career match** = importance-weighted share of the role's requirements already covered.
* **Career fit** (for the "best-fit careers" cards) = 75% skill match + 25% interest overlap.
* **Adaptive notes** compare completed hours with hours planned since the profile was created and suggest fast-track mode when the user falls behind.

## Run it

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

Click **Try the demo profile** in the sidebar for an instant walkthrough.

## Test it

Run the automated tests with:

```bash
pytest -q
```

The tests cover the knowledge base, gap engine, roadmap ordering and scheduling, adaptivity, SQLite round trips and an end-to-end UI flow using Streamlit `AppTest`.

## Project structure

```text
app.py                     Streamlit entry point and navigation

backend/
  data.py                  Skills, resources, careers, market presets
  career_engine.py         Requirements, gaps, priorities, match, explanations
  recommendations.py       Resource selection and explanations
  roadmap.py               Phased schedule, adaptive notes, Markdown export
  analysis.py              Facade: one call runs the whole pipeline
  database.py              SQLite persistence

ui/
  components.py            CSS and reusable widgets
  profile.py               Profile and goal form
  dashboard.py             Overview, gaps, roadmap, recommendations,
                           adaptive engine, progress

tests/                     pytest test suite
```

## Suggested demo flow (3 minutes)

1. Sidebar: **Try the demo profile**. Show the hero section and career-match strip.
2. **Skill gaps**: open the top gap and read its explanation.
3. **Roadmap**: mark two steps complete and watch the match, hours and roadmap change.
4. **Adaptive engine**: apply the example requirement change and show priorities re-ranking.
5. **Progress**: show the match-over-time chart and download the roadmap.

## Notes and limits

* The knowledge base is hand-curated for the prototype. Course names and providers should be re-checked before real use.
* Example "market updates" are simulated to demonstrate adaptability; they are not live job-market data.
* Possible extension: plug an LLM behind `explain_*` for richer coaching, or replace `data.py` with a live skills API.

## Installation and Setup

### Prerequisites

Make sure the following are installed:

- Python 3.10 or later
- Git
- A web browser

### Clone the Repository

```bash
git clone https://github.com/siddhikolekar17/Personalized-Career-Skill-Navigator-Agent.git
cd Personalized-Career-Skill-Navigator-Agent
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Project

```bash
streamlit run app.py
```

The application will open in your browser.

### Run Tests

```bash
pytest -q
```

## Live Demo

**Streamlit Application:**

https://personalized-career-skill-navigator-agent-epsjyrwxpdkxb2xyzaoh.streamlit.app/

## Source Code

**GitHub Repository:**

https://github.com/siddhikolekar17/Personalized-Career-Skill-Navigator-Agent