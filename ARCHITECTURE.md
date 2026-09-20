# Project Architecture

The Personalized Career & Skill Navigator Agent is organized into separate layers for application logic, user interface, data persistence, and testing.

## Application Flow

1. The Streamlit application starts from `app.py`.
2. The profile interface collects the user's education, skills, interests, experience, and career goal.
3. The career engine analyzes the user's current skills against the selected target role.
4. The roadmap module generates a personalized learning path based on identified skill gaps.
5. The recommendations module provides relevant learning resources and activities.
6. The dashboard displays the results and progress to the user.
7. The database module stores user and progress information.

## Main Components

- `app.py` — Streamlit application entry point.
- `backend/career_engine.py` — career and skill-gap analysis.
- `backend/roadmap.py` — personalized roadmap generation.
- `backend/recommendations.py` — learning and career recommendations.
- `backend/database.py` — persistent data storage.
- `ui/profile.py` — user profile and career-goal input.
- `ui/dashboard.py` — personalized results and progress display.
- `tests/` — automated tests for core functionality.

## Design Approach

The separation of backend logic and UI components makes the application easier to test, maintain, and extend as additional career-planning features are introduced.