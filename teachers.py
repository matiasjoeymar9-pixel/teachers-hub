import streamlit as st
from docx import Document
import io
import requests
import json
import base64
from datetime import datetime, timedelta
import extra_streamlit_components as stx
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Guro Hub - One-Stop Educator Assistant",
    page_icon="🏫",
    layout="wide"
)

# --- GEMINI API CONFIGURATION ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# --- GEMINI AI GENERATION FUNCTION ---
def generate_ai_response(prompt_text):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-3.8-flash')
        response = model.generate_content(prompt_text)
        if response and response.text:
            return response.text
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"
    return "⚠️ Error: Walang naging tugon mula sa AI."

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
