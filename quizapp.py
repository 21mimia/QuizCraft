import streamlit as st
import json
import os
import re
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ------------------- CUSTOM STYLING -------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }

body, .stApp {
    background: linear-gradient(135deg, #601c87 0%, #8b2cbf 50%, #1e1b4b 100%);
    color: white !important;
}

/* Page Layout */
.block-container {
    padding-top: 3rem !important;
    max-width: 850px !important;
    margin: auto;
}

/* Headings */
.dashboard-heading {
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    color: #fff;
    margin-bottom: 0.5rem;
}
.dashboard-subtitle {
    text-align: center;
    color: #d8b4fe;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

/* =======================
   ✨ UNIFIED INPUT STYLE
   ======================= */
textarea, input, select,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="select"] > div {
    background: rgba(94, 23, 235, 0.25) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 10px !important;
    color: #fff !important;
    box-shadow: 0 0 15px rgba(139,92,246,0.35) !important;
    transition: all 0.3s ease !important;
}

/* Focus glow */
textarea:focus, input:focus, select:focus,
div[data-baseweb="textarea"] textarea:focus,
div[data-baseweb="input"] input:focus,
div[data-baseweb="select"] > div:focus-within {
    background: rgba(157, 23, 235, 0.35) !important;
    border-color: #ec4899 !important;
    box-shadow: 0 0 25px rgba(236,72,153,0.7) !important;
    outline: none !important;
}

/* Dropdown menu background */
div[data-baseweb="popover"] {
    background: rgba(58, 12, 97, 0.95) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 20px rgba(139,92,246,0.45) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}

/* Dropdown options */
div[data-baseweb="option"] {
    background: transparent !important;
    color: white !important;
}
div[data-baseweb="option"]:hover {
    background: linear-gradient(135deg, rgba(168,85,247,0.5), rgba(236,72,153,0.4)) !important;
}

/* Slider */
div[data-baseweb="slider"] > div > div {
    background: linear-gradient(135deg, #ec4899, #8b5cf6) !important;
}
div[data-baseweb="slider"] div[role="slider"] {
    background: #ec4899 !important;
    border: 2px solid white !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #8b5cf6, #ec4899);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.7rem 1.5rem;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 0 10px rgba(236,72,153,0.4);
}
.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 20px rgba(236,72,153,0.6);
}

/* Result Box */
.result-box {
    background: rgba(255,255,255,0.15);
    border-radius: 1rem;
    padding: 1.5rem;
    margin-top: 2rem;
    text-align: center;
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

# ------------------- QUIZ LOGIC -------------------
@st.cache_data
def fetch_questions_raw(text_content, quiz_level, language, num_questions, question_type):
    sample_format = {
        "questions": [
            {
                "type": "mcq",
                "question": "Sample question?",
                "options": {
                    "a": "Option A",
                    "b": "Option B",
                    "c": "Option C",
                    "d": "Option D"
                },
                "correct": "a"
            },
            {
                "type": "true_false",
                "question": "Sample true/false question?",
                "correct": "True"
            },
            {
                "type": "fill_blank",
                "question": "Sample fill-in-the-blank question?",
                "correct": "Answer"
            }
        ]
    }

    prompt = f"""
Text: {text_content}

You are an expert multilingual quiz generator. Based on the above text_content,
create {num_questions} questions with difficulty level '{quiz_level}',
question type '{question_type}', written in '{language}' language.

⚠ Respond with ONLY valid JSON matching the format below.
Do not include any explanation, markdown, or extra text.

{json.dumps(sample_format, indent=2)}
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    content = response.choices[0].message.content.strip()
    content = re.sub(r"^json|$", "", content, flags=re.MULTILINE).strip()
    return content


# ------------------- MAIN APP -------------------
def main():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.markdown("<h1 class='dashboard-heading'>⚡ AI Quiz Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='dashboard-subtitle'>Generate intelligent, multilingual quizzes using AI in seconds!</p>", unsafe_allow_html=True)

    text_content = st.text_area("📄 Paste content for quiz:", height=200)
    quiz_level = st.selectbox("🎯 Choose difficulty:", ["Easy", "Medium", "Hard"]).lower()

    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("🗣 Choose language:", ["English", "Spanish", "French", "Hindi", "Bangla", "German", "Chinese"])
    with col2:
        num_questions = st.slider("🧮 Number of questions:", min_value=1, max_value=30, value=5)

    question_type = st.selectbox("📝 Choose question type:", ["Multiple Choice", "True/False", "Fill-in-the-Blank", "Mixed"])

    if st.button("🚀 Generate Quiz"):
        if not text_content:
            st.warning("⚠ Please paste some content before generating a quiz.")
            return

        raw_output = fetch_questions_raw(text_content, quiz_level, language, num_questions, question_type)

        try:
            questions = json.loads(raw_output).get("questions", [])
        except json.JSONDecodeError:
            st.error("❌ Model did not return valid JSON. Try again.")
            return

        if not questions:
            st.warning("⚠ No questions generated. Please adjust input or try again.")
            return

        st.divider()
        st.subheader("🧩 Your Quiz:")

        selected_options = []
        correct_answers = []

        for i, q in enumerate(questions, start=1):
            st.markdown(f"<div class='quiz-box'><b>{i}. {q['question']}</b></div>", unsafe_allow_html=True)

            if q["type"] == "mcq":
                opts = list(q["options"].values())
                selected = st.radio(label=f"Question {i}", options=opts, key=f"q{i}", label_visibility="collapsed")
            elif q["type"] == "true_false":
                selected = st.radio(label=f"Question {i}", options=["True", "False"], key=f"q{i}", label_visibility="collapsed")
            elif q["type"] == "fill_blank":
                selected = st.text_input(label=f"Question {i}", key=f"q{i}", label_visibility="collapsed")
            else:
                continue

            selected_options.append(selected)
            correct_answers.append(q["correct"])

        if st.button("✅ Submit Answers"):
            st.balloons()
            score = 0
            st.markdown("<div class='result-box'><h3>📊 Results</h3>", unsafe_allow_html=True)
            for i, q in enumerate(questions, start=1):
                if str(selected_options[i-1]).strip().lower() == str(correct_answers[i-1]).strip().lower():
                    score += 1
            st.success(f"🎉 You scored *{score} / {len(questions)}*")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
