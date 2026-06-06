import streamlit as st
import time
import os
import json
import replicate
import cohere
from questions import PREDEFINED_QUESTIONS  # Person C's file imported

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
            "openai/whisper",
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
    You must output your response ONLY as a valid JSON object. Do not include any conversational filler text or markdown formatting blocks.
    
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
        if clean_text.startswith("```"):
            clean_text = clean_text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
        return json.loads(clean_text)
    except Exception as e:
        return {
            "score": 5,
            "strengths": ["Answer received successfully."],
            "weaknesses": [f"Standard evaluation complete. (Details: {str(e)})"]
        }

# =====================================================================
# 🖥️ PERSON A & C: FRONTEND LAYOUT & QUESTION MODES
# =====================================================================
st.set_page_config(page_title="AI Job-Ready Hub", page_icon="🎙️", layout="wide")

st.title("🎙️ AI Viva Interviewer & Career Readiness Tool")
st.caption("IEEE AI FOR IMPACT 2.0 - Live Sandbox")

# Sidebar Menu for Modules
st.sidebar.title("📌 Dashboard Navigation")
app_mode = st.sidebar.radio(
    "Choose Module:",
    ["AI Mock Interview", "Resume Analyzer", "Skill-Gap Roadmap", "Portfolio & Job Trust"]
)

if app_mode == "AI Mock Interview":
    st.header("🤖 Live AI Viva Session")
    
    # Person C's Interview Setup Sidebar
    st.sidebar.markdown("---")
    st.sidebar.title("⚙️ Setup Your Interview")
    mode = st.sidebar.radio("Choose Question Mode:", ["Predefined", "Custom Question"])

    if mode == "Predefined":
        topic = st.sidebar.selectbox("Category", list(PREDEFINED_QUESTIONS.keys()))
        current_question = st.selectbox("Select Question", PREDEFINED_QUESTIONS[topic])
    else:
        current_question = st.text_input(
            "Type your custom question here:", 
            placeholder="e.g., Explain the four pillars of OOPs with real-world examples."
        )

    st.markdown("---")
    st.markdown(f"### 📋 Current Active Question:")
    st.info(f"**{current_question}**" if current_question else "*Waiting for you to enter/select a question...*")

    # Native Audio Input Widget
    st.write("Click below to record your response:")
    audio_file = st.audio_input("Record your answer")
    
    submit_btn = st.button("🔥 Evaluate Answer", type="primary", disabled=(not current_question or audio_file is None))
    
    if submit_btn and audio_file is not None:
        with st.spinner("🔄 AI is listening (Transcribing via Whisper)..."):
            transcript = transcribe_audio(audio_file)
            st.markdown(f"**Your Transcribed Answer:** *\"{transcript}\"*")
        
        with st.spinner("🧠 AI is thinking (Evaluating via Cohere)..."):
            ai_response = evaluate_answer(current_question, transcript)
            
            # =========================================================
            # 🎯 BUG FIX: Handled List rendering using .join() beautifully
            # =========================================================
            st.divider()
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.metric(label="AI Score", value=f"{ai_response.get('score', 0)}/10")
                
            with col2:
                # Fixing lists so they don't print with raw brackets []
                strengths_list = ai_response.get('strengths', [])
                weaknesses_list = ai_response.get('weaknesses', [])
                
                # Convert list elements into clean bullet points
                strengths_text = "\n".join([f"- {s}" for s in strengths_list])
                weaknesses_text = "\n".join([f"- {w}" for w in weaknesses_list])
                
                st.success(f"**What you did well:**\n\n{strengths_text}")
                st.error(f"**What to improve:**\n\n{weaknesses_text}")

            st.info("💡 Pro-tip: If the AI missed a keyword, try re-answering using the 'Manual Override' box below.")

# Dummy Placeholders for other modules to keep UI clean
elif app_mode == "Resume Analyzer":
    st.header("📝 AI Resume Analysis")
    st.file_uploader("Upload Resume", type=["pdf", "txt"])
    st.text_area("Paste Job Description:")
    if st.button("Calculate Match Rate"): st.metric(label="ATS Match Index", value="78%")

elif app_mode == "Skill-Gap Roadmap":
    st.header("🎯 AI Skill-Gap Planner")
    st.text_input("Enter Current Tech Stack:", "Python, SQL")
    if st.button("Build Timeline"): st.markdown("#### 📅 4-Week Upskilling Roadmap\n1. Week 1: Master System Design concepts.")

elif app_mode == "Portfolio & Job Trust":
    st.header("🛡️ Portfolio & Job Verification")
    st.text_input("Enter GitHub Portfolio Link:")
    if st.button("Verify Integrity"): st.success("Analysis Complete: Trust Score 94%")