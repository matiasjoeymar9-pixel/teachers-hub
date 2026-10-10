import streamlit as st
from docx import Document
import io
import json
import base64
import google.generativeai as genai
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Guro Hub - One-Stop Educator Assistant",
    page_icon="🏫",
    layout="wide"
)

# --- GEMINI API CONFIGURATION ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# --- HELPER: CLEAN TEXT SAFELY ---
def clean_text_output(text):
    if not text:
        return ""
    cleaned = text.replace('```python', '').replace('```', '')
    return cleaned.strip()

# --- HELPER: CONVERT TEXT TO DOCX ---
def create_docx(text_content):
    doc = Document()
    doc.add_heading('Guro Hub - Generated Output', 0)
    for line in text_content.split('\n'):
        clean_line = clean_text_output(line)
        if clean_line.startswith('# '):
            doc.add_heading(clean_line.replace('# ', ''), level=1)
        elif clean_line.startswith('## '):
            doc.add_heading(clean_line.replace('## ', ''), level=2)
        elif clean_line.startswith('### '):
            doc.add_heading(clean_line.replace('### ', ''), level=3)
        else:
            if clean_line:
                doc.add_paragraph(clean_line)
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- GEMINI AI GENERATION FUNCTION ---
def generate_ai_response(prompt_text):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Ginamit ang pinakabagong suportadong Gemini model identifier
        model = genai.GenerativeModel('gemini-3.8-flash')
        response = model.generate_content(prompt_text)
        if response and response.text:
            return clean_text_output(response.text)
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"
    return "⚠️ Error: Walang naging tugon mula sa AI."

# --- MAIN APP INTERFACE ---
st.title("🏫 Guro Hub")
st.write("Ang iyong All-in-One AI Assistant para sa DepEd/CHED Lesson Plans at Quizzes.")

# Sidebar Navigation
st.sidebar.markdown("## 📌 Navigation")
service = st.sidebar.radio("Pumili ng Service:", ["📝 Lesson Plan Generator", "❓ Quiz Generator", "🧹 Class List Cleaner"])

st.sidebar.success("AI Power Activated (Gemini-Powered)!")

if service == "📝 Lesson Plan Generator":
    st.header("📝 DepEd/CHED Lesson Plan Generator (AI)")
    subject = st.text_input("Subject (e.g., Science, Math):", "Math")
    
    grade_levels = [
        "Kindergarten",
        "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6",
        "Grade 7", "Grade 8", "Grade 9", "Grade 10",
        "Grade 11", "Grade 12",
        "College / Tertiary"
    ]
    grade_level = st.selectbox("Grade Level:", grade_levels)
    
    language = st.selectbox("Wika / Language:", ["English", "Filipino"])
    topic = st.text_input("Topic / Aralin:", "Addition")

    if st.button("Generate AI Lesson Plan"):
        if not GEMINI_API_KEY:
            st.error("⚠️ Walang nakitang GEMINI_API_KEY sa Streamlit secrets.")
        else:
            with st.spinner("Pinoproseso ng AI ang detalyadong Lesson Plan..."):
                prompt = (
                    f"Gumawa ng napakalinaw, propesyonal, at kumpletong 4-As Lesson Plan para sa Subject na {subject}, "
                    f"Grade Level {grade_level}, sa wikang {language} tungkol sa paksang '{topic}'. "
                    f"Tiyaking tama at buo ang lahat ng mathematical symbols at pormula. "
                    f"Dapat ay may kasamang kumpletong Answer Key para sa Evaluation at kumpletong step-by-step solutions para sa Assignment."
                )
                result = generate_ai_response(prompt)
                st.markdown("## 📜 Resulta ng AI:")
                st.markdown(result)
                
                # Download Button for DOCX
                docx_file = create_docx(result)
                st.download_button(
                    label="📥 Download as DOCX",
                    data=docx_file,
                    file_name=f"Lesson_Plan_{subject}_{topic}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

elif service == "❓ Quiz Generator":
    st.header("❓ Quiz Generator (AI)")
    quiz_topic = st.text_input("Paksa ng Quiz:", "Pandiwa")
    num_items = st.slider("Bilang ng Items:", 5, 20, 10)
    
    if st.button("Generate AI Quiz"):
        if not GEMINI_API_KEY:
            st.error("⚠️ Walang nakitang GEMINI_API_KEY sa Streamlit secrets.")
        else:
            with st.spinner("Gumagawa ang AI ng Quiz at Answer Key..."):
                prompt = (
                    f"Gumawa ng {num_items}-item na pagsusulit o quiz tungkol sa '{quiz_topic}'. "
                    f"Tiyaking buo at tama ang mga pormula at tanong. "
                    f"Isama ang kumpletong Answer Key para sa lahat ng mga tanong at mga Assignment items."
                )
                result = generate_ai_response(prompt)
                st.markdown("## 📜 Resulta ng Quiz:")
                st.markdown(result)
                
                # Download Button for Quiz DOCX
                docx_file = create_docx(result)
                st.download_button(
                    label="📥 Download Quiz as DOCX",
                    data=docx_file,
                    file_name=f"Quiz_{quiz_topic}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

elif service == "🧹 Class List Cleaner":
    st.header("🧹 Class List Cleaner")
    st.write("I-upload ang iyong listahan ng mga mag-aaral para ayusin.")
    uploaded_file = st.file_uploader("Mag-upload ng CSV o Text file", type=["csv", "txt"])
    if uploaded_file:
        st.success("Na-upload na ang file! Handa nang linisin.")
