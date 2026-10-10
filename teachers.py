import streamlit as st
from docx import Document
import io
import requests
import json
import base64
from datetime import datetime, timedelta
import extra_streamlit_components as stx

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Guro Hub - One-Stop Educator Assistant",
    page_icon="🏫",
    layout="wide"
)

# --- GEMINI API CONFIGURATION ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# --- GITHUB DATABASE SETTINGS ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_OWNER = "matiasjoeymar9-pixel"
REPO_NAME = "teachers-hub"
FILE_PATH = "database.json"

def get_github_db():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return json.loads(content), data['sha']
    return None, None

def update_github_db(data, sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    content = base64.b64encode(json.dumps(data, indent=4).encode('utf-8')).decode('utf-8')
    payload = {
        "message": "Update database",
        "content": content,
        "sha": sha
    }
    response = requests.put(url, headers=headers, json=payload)
    return response.status_code == 200

# --- GEMINI AI GENERATION FUNCTION (REST API) ---
def generate_ai_response(prompt_text):
    # Ginagamit ang v1beta REST endpoint na may gemini-1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            # Fallback sakaling magka-issue
            url_alt = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
            response_alt = requests.post(url_alt, headers=headers, json=payload)
            if response_alt.status_code == 200:
                data_alt = response_alt.json()
                return data_alt['candidates'][0]['content']['parts'][0]['text']
            return f"⚠️ API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"⚠️ Connection Error: {str(e)}"

# --- MAIN APP INTERFACE ---
st.title("🏫 Guro Hub")
st.write("Ang iyong All-in-One Assistant para sa Lesson Plans, Quizzes, at Class Data.")

# Sidebar Navigation
st.sidebar.markdown("## 📌 Navigation")
service = st.sidebar.radio("Pumili ng Service:", ["📝 Lesson Plan Generator", "❓ Quiz Generator", "🧹 Class List Cleaner"])

st.sidebar.success("VIP Subscriber Access Active (Unlimited for 1 Month)!")

if service == "📝 Lesson Plan Generator":
    st.header("📝 DepEd/CHED Lesson Plan Generator")
    subject = st.text_input("Subject (e.g., Science, Math):", "Math")
    grade_level = st.text_input("Grade Level:", "Grade 1-3")
    language = st.selectbox("Wika / Language:", ["English", "Filipino"])
    topic = st.text_input("Topic / Aralin:", "Addition")

    if st.button("Generate Lesson Plan"):
        if not GEMINI_API_KEY:
            st.error("⚠️ Walang nakitang GEMINI_API_KEY sa Streamlit secrets.")
        else:
            with st.spinner("Gumagawa ng Lesson Plan..."):
                prompt = f"Gumawa ng detalyadong 4-As Lesson Plan para sa Subject na {subject}, Grade Level {grade_level}, sa wikang {language} tungkol sa paksang '{topic}'."
                result = generate_ai_response(prompt)
                st.markdown("## 📜 Resulta:")
                st.markdown(result)

elif service == "❓ Quiz Generator":
    st.header("❓ Quiz Generator")
    quiz_topic = st.text_input("Paksa ng Quiz:", "Pandiwa")
    num_items = st.slider("Bilang ng Items:", 5, 20, 10)
    
    if st.button("Generate Quiz"):
        if not GEMINI_API_KEY:
            st.error("⚠️ Walang nakitang GEMINI_API_KEY sa Streamlit secrets.")
        else:
            with st.spinner("Gumagawa ng Quiz..."):
                prompt = f"Gumawa ng {num_items}-item na quiz tungkol sa '{quiz_topic}' kasama ang answer key."
                result = generate_ai_response(prompt)
                st.markdown("## 📜 Resulta ng Quiz:")
                st.markdown(result)

elif service == "🧹 Class List Cleaner":
    st.header("🧹 Class List Cleaner")
    st.write("I-upload ang iyong listahan ng mga mag-aaral para ayusin.")
    uploaded_file = st.file_uploader("Mag-upload ng CSV o Text file", type=["csv", "txt"])
    if uploaded_file:
        st.success("Na-upload na ang file! Handa nang linisin.")
