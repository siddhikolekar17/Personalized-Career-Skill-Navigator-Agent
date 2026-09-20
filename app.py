import streamlit as st

st.set_page_config(
    page_title="Career & Skill Navigator",
    page_icon="🎯"
)

st.title("🎯 Personalized Career & Skill Navigator Agent")
st.write("AI-powered personalized career and skill roadmap navigator")

st.subheader("👤 Student Profile")

name = st.text_input("Your Name")
education = st.text_input("Education")
skills = st.text_area("Current Skills")
career = st.text_input("Target Career")

if st.button("🚀 Analyze My Career"):
    st.success("Profile received!")
    st.write("Target Career:", career)
