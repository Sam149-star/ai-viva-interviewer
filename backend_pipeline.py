import os
import json
import replicate
import cohere

# ==========================================
# 🔑 SET YOUR API CREDENTIALS HERE
# ==========================================
# Replace these strings with your actual tokens from your dashboards
os.environ["REPLICATE_API_TOKEN"] = "r8_cnRCrL1qLTsd8VXF3yg2ma80sGPBufr0KIYVD"
cohere_client = cohere.Client('cohere_jhqUl3kYIHzDdwZ6gJJIYhP7OtOX1uzCq6pe2IZ83CI9e6')

# ==========================================
# 🎧 THE EAR: AUDIO TRANSCRIPTION
# ==========================================
def transcribe_audio(audio_file):
    try:
        output = replicate.run(
            "openai/whisper:91ee9c0c3a868fa83db554db254997caab043004b",
            input={"audio": audio_file}
        )
        return output["transcription"]
    except Exception as e:
        return f"Whisper Processing Error: {str(e)}"

# ==========================================
# 🧠 THE BRAIN: LIVE VERIFICATION & SCORING
# ==========================================
def evaluate_answer(question, user_transcript):
    prompt = f"""
    You are an expert technical interviewer. Evaluate the candidate's response to the question.
    
    Question asked: "{question}"
    Candidate's spoken answer: "{user_transcript}"
    
    Analyze the correctness, depth, and clarity of their answer.
    You must output your response ONLY as a valid JSON object. Do not include any conversational filler text or markdown formatting blocks.
    
    Use this exact format:
    {{
        "score": <Give an integer score out of 10>,
        "strengths": ["point 1", "point 2"],
        "weaknesses": ["point 1", "point 2"]
    }}
    """
    try:
        response = cohere_client.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=250,
            temperature=0.3
        )
        
        clean_text = response.generations[0].text.strip()
        dictionary_output = json.loads(clean_text)
        return dictionary_output

    except Exception as e:
        return {
            "score": 0,
            "strengths": ["System error occurred during evaluation."],
            "weaknesses": [f"Error details: {str(e)}"]
        }