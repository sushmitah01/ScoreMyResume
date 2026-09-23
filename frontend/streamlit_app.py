import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"

st.title("ScoreMyResume")
st.write("AI-powered ATS resume scorer")

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if st.session_state.access_token is None:
    auth_mode = st.radio("Choose an option", ["Login", "Sign Up"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if auth_mode == "Sign Up":
        full_name = st.text_input("Full Name")

        if st.button("Sign Up"):
            response = requests.post(
                f"{API_BASE_URL}/auth/signup",
                json={"email": email, "password": password, "full_name": full_name},
            )

            if response.status_code == 201:
                st.session_state.access_token = response.json()["access_token"]
                st.success("Account created!")
                st.rerun()
            else:
                st.error(f"Signup failed: {response.json().get('detail', 'Unknown error')}")

    else:
        if st.button("Log In"):
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={"email": email, "password": password},
            )

            if response.status_code == 200:
                st.session_state.access_token = response.json()["access_token"]
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Login failed. Check your email and password.")
else:
    st.success("You are logged in.")

    if st.button("Log Out"):
        st.session_state.access_token = None
        st.rerun()

    st.divider()
    st.subheader("Score Your Resume")

    resume_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    job_description = st.text_area("Paste the job description", height=200)
    required_years = st.number_input("Years of experience required (optional)", min_value=0, value=0)

    if st.button("Score My Resume"):
        if resume_file is None or job_description.strip() == "":
            st.error("Please upload a resume and paste a job description.")
        else:
            with st.spinner("Scoring your resume..."):
                headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
                files = {"resume": (resume_file.name, resume_file.getvalue(), resume_file.type)}
                data = {"job_description": job_description, "required_years": required_years}

                response = requests.post(
                    f"{API_BASE_URL}/resume/score",
                    headers=headers,
                    files=files,
                    data=data,
                )

            if response.status_code == 200:
                result = response.json()

                st.subheader("Results")
                st.metric("Overall Score", f"{result['overall_score']} / 100")

                st.write("**Score Breakdown**")
                for component, score in result["breakdown"].items():
                    st.write(f"{component.capitalize()}: {score}")
                    st.progress(min(score / 100, 1.0))

                st.write("**Matched Keywords:**", ", ".join(result["matched_keywords"]) or "None")
                st.write("**Missing Keywords:**", ", ".join(result["missing_keywords"]) or "None")
                st.write("**Matched Skills:**", ", ".join(result["matched_skills"]) or "None")
                st.write("**Missing Skills:**", ", ".join(result["missing_skills"]) or "None")

                st.write("**AI Feedback:**")
                st.info(result["ai_feedback"])
            else:
                st.error(f"Scoring failed: {response.json().get('detail', 'Unknown error')}")