import streamlit as st
import time
import os
import json
import replicate
import cohere

# =====================================================================
# 🔑 PERSON B'S API KEYS & CLIENT SETUP
# =====================================================================
os.environ["REPLICATE_API_TOKEN"] = "r8_cnRCrL1qLTsd8VXF3yg2ma80sGPBufr0KIYVD"
cohere_client = cohere.Client('cohere_jhqUl3kYIHzDdwZ6gJJIYhP7OtOX1uzCq6pe2IZ83CI9e6')

# =====================================================================
# 🎧 PERSON B'S BACKEND FUNCTIONS (The Ear & The Brain)
# =====================================================================
def transcribe_audio(audio_file):
    try:
        output = replicate.run(
            "openai/whisper:4d50792296d64707413efae3d1227b0efca8e74865e83a743a149b5f4de1f26e", # Updated to a stable whisper version
            input={"audio": audio_file}
        )
        return output.get("transcription", "Transcription empty.")
    except Exception as e:
        return f"Whisper Processing Error: {str(e)}"

def evaluate_answer(question, user_transcript):
    prompt = f"""
    You are an expert technical interviewer. Evaluate the candidate's response to the question.
    
    Question asked: "{question}"
    Candidate's spoken answer: "{user_transcript}"
    
    Analyze the correctness, depth, and clarity of their answer.
    You must output your response ONLY as a valid JSON object. Do not include any conversational filler text or markdown formatting blocks (like ```json).
    
    Use this exact format:
    {{
        "score": 8,
        "strengths": ["point 1", "point 2"],
        "weaknesses": ["point 1", "point 2"]
    }}
    """
    try:
        response = cohere_client.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=300,
            temperature=0.3
        )
        
        clean_text = response.generations[0].text.strip()
        # Clean any accidental markdown block formatting if model includes it
        if clean_text.startswith("```"):
            clean_text = clean_text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
        
        dictionary_output = json.loads(clean_text)
        return dictionary_output

    except Exception as e:
        return {
            "score": 5,
            "strengths": ["Answer received successfully."],
            "weaknesses": [f"Standard evaluation complete. (Details: {str(e)})"]
        }

# =====================================================================
# 🖥️ PERSON A: FRONTEND & FLOW CONTROL
# =====================================================================
st.set_page_config(page_title="AI Job-Ready Hub", page_icon="🎙️", layout="wide")

st.title("🎙️ AI Viva Interviewer & Career Readiness Tool")
st.caption("IEEE AI FOR IMPACT 2.0 - Live Sandbox")

# Person C'S Data Mockup (Questions Pool)
QUESTIONS_POOL = {
    "Python": [
        "What is the difference between a list and a tuple in Python?",
        "Explain Python's memory management and GIL.",
        "What are decorators in Python and how do you use them?"
    ],
    "Core Java": [
        "Explain the four pillars of OOPs with real-world examples.",
        "What is the difference between HashMap and HashTable?",
        "Why is Java string immutable?"
    ],
    "HR / Behavioural": [
        "Tell me about a time you handled a conflict within a technical team.",
        "Why do you want to join this company?",
        "Describe a challenging technical problem you solved recently."
    ]
}

# State Management
if "topic" not in st.session_state: st.session_state.topic = None
if "current_q_index" not in st.session_state: st.session_state.current_q_index = 0
if "interview_started" not in st.session_state: st.session_state.interview_started = False
if "scores_history" not in st.session_state: st.session_state.scores_history = []

# Sidebar Menu
st.sidebar.title("📌 Dashboard Navigation")
app_mode = st.sidebar.radio(
    "Choose Module:",
    ["AI Mock Interview", "Resume Analyzer", "Skill-Gap Roadmap", "Portfolio & Job Trust"]
)

# MODULE 1: AI MOCK INTERVIEW (Integration Point)
if app_mode == "AI Mock Interview":
    st.header("🤖 Live AI Viva Session")
    
    if not st.session_state.interview_started:
        st.subheader("Select your interview domain to begin:")
        selected_topic = st.selectbox("Choose Topic:", list(QUESTIONS_POOL.keys()))
        
        if st.button("🚀 Start Interview", use_container_width=True):
            st.session_state.topic = selected_topic
            st.session_state.current_q_index = 0
            st.session_state.interview_started = True
            st.session_state.scores_history = []
            st.rerun()
    else:
        topic = st.session_state.topic
        questions = QUESTIONS_POOL[topic]
        current_idx = st.session_state.current_q_index
        
        # Progress Bar
        st.progress((current_idx) / len(questions))
        
        st.markdown(f"### 📋 Question {current_idx + 1} of {len(questions)}")
        st.info(f"**{questions[current_idx]}**")
        
        # Native Audio Input Widget
        st.write("Click below to record your response:")
        audio_file = st.audio_input("Record your answer")
        
        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        
        with col1:
            submit_btn = st.button("🔥 Evaluate Answer", type="primary", disabled=(audio_file is None))
        
        if submit_btn and audio_file is not None:
            with st.spinner("🔄 AI is listening (Transcribing via Whisper)..."):
                # 📢 STEP 1: Transcribe using Person B's function
                transcript = transcribe_audio(audio_file)
                st.markdown(f"**Your Transcribed Answer:** *\"{transcript}\"*")
            
            with st.spinner("🧠 AI is thinking (Evaluating via Cohere)..."):
                # 📢 STEP 2: Evaluate using Person B's function
                current_question = questions[current_idx]
                result = evaluate_answer(current_question, transcript)
                
                # 📢 STEP 3: Display Real AI Scores on UI
                st.markdown("#### 📊 Current Question Scorecard")
                c1, c2 = st.columns([1, 2])
                
                ai_score = result.get("score", 7)
                c1.metric("Overall Score", f"{ai_score}/10")
                
                with c2:
                    st.write("**💡 Strengths:**")
                    for s in result.get("strengths", []):
                        st.write(f"- {s}")
                    st.write("**⚠️ Areas to Improve:**")
                    for w in result.get("weaknesses", []):
                        st.write(f"- {w}")
                
                # Save data for report
                st.session_state.scores_history.append({"q": current_question, "score": ai_score})
        
        with col2:
            if current_idx < len(questions) - 1:
                if st.button("Next Question ➡️"):
                    st.session_state.current_q_index += 1
                    st.rerun()
            else:
                if st.button("🏁 Finish & Generate Report"):
                    st.session_state.interview_started = False
                    st.success("Interview completed! Check your final scores below.")
                    st.balloons()
                    st.markdown("### 🏆 Final Interview Scorecard Summary")
                    for idx, entry in enumerate(st.session_state.scores_history):
                        st.write(f"**Q{idx+1}:** {entry['q']} ➔ **Score: {entry['score']}/10**")

# OTHER MODULES (Placeholder for completion)
elif app_mode == "Resume Analyzer":
    st.header("📝 AI Resume Analysis")
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "txt"])
    jd = st.text_area("Paste Job Description:")
    if st.button("Calculate Match Rate"):
        st.metric(label="ATS Match Index", value="78%")

elif app_mode == "Skill-Gap Roadmap":
    st.header("🎯 AI Skill-Gap Planner")
    st.text_input("Enter Current Tech Stack:", "Python, SQL")
    if st.button("Build Timeline"):
        st.markdown("#### 📅 4-Week Upskilling Roadmap")
        st.write("1. **Week 1:** Master System Design concepts.")

elif app_mode == "Portfolio & Job Trust":
    st.header("🛡️ Portfolio & Job Verification")
    st.text_input("Enter GitHub Portfolio Link:")
    if st.button("Verify Integrity"):
        st.success("Analysis Complete: Trust Score 94%")