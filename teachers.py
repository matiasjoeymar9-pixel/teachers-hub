import streamlit as st
import google.generativeai as genai
from docx import Document
import io

# Page Configuration
st.set_page_config(page_title="Guro Hub - One-Stop Educator Assistant", page_icon="🏫", layout="centered")

# Helper Function para sa Word Document (.docx)
def create_docx(text_content, title="Guro Hub Generated File"):
    doc = Document()
    doc.add_heading(title, level=1)
    for line in text_content.split('\n'):
        doc.add_paragraph(line)
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# Kuhanin ang API Key mula sa Streamlit Secrets o sa Sidebar
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Initialize Session State para sa Free Tries Counter
if "tries_used" not in st.session_state:
    st.session_state.tries_used = 0

FREE_LIMIT = 5
tries_left = FREE_LIMIT - st.session_state.tries_used

# Header
st.title("🏫 Guro Hub")
st.caption("Ang iyong All-in-One Assistant para sa Lesson Plans, Quizzes, at Class Data.")

# Sidebar Navigation
st.sidebar.header("📌 Navigation")
selected_service = st.sidebar.radio(
    "Pumili ng Service:",
    [
        "📝 Lesson Plan Generator",
        "❓ Quiz Generator",
        "🧹 Class List Cleaner"
    ]
)

# Counter Tracker sa Sidebar
st.sidebar.markdown("---")
if tries_left > 0:
    st.sidebar.success(f"🎁 Free Trial: **{tries_left}** / {FREE_LIMIT} tries left")
else:
    st.sidebar.error("❌ Naubos na ang Libreng Subok!")
    st.sidebar.warning("💳 Mag-subscribe ng ₱99/month via GCash para sa Unlimited Access.")

# Fallback API Key input
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")

# --- MAIN LOGIC PER SERVICE ---
if tries_left <= 0:
    st.error("🔒 Nagamit mo na ang iyong 5 libreng subok.")
    st.info("I-send ang ₱99 subscription via GCash para ma-activate ang Pro Access.")
else:
    # -------------------------------------------------------------
    # TAB 1: Lesson Plan Generator
    # -------------------------------------------------------------
    if selected_service == "📝 Lesson Plan Generator":
        st.subheader("📝 DepEd/CHED Lesson Plan Generator")
        
        col1, col2 = st.columns(2)
        with col1:
            subject = st.text_input("Subject (e.g., Science, Math):")
            grade = st.selectbox("Grade Level:", ["Grade 1-3", "Grade 4-6", "Grade 7-10", "Grade 11-12", "College"])
        with col2:
            language = st.selectbox("Wika / Language:", ["Tagalog / Filipino", "English", "Taglish"])
            topic = st.text_input("Topic / Aralin:")
        
        if st.button("Generate Lesson Plan"):
            if not api_key:
                st.warning("Kailangan ng API Key para gumana.")
            elif not topic or not subject:
                st.warning("Paki-kumpleto ang Subject at Topic.")
            else:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.8-flash')
                    
                    # Strict prompt to prevent LaTeX and markdown clutter
                    prompt = f"Gumawa ng detalyadong DepEd/CHED Lesson Plan para sa {subject} ({grade}) na may topic na '{topic}'. Gamitin ang wikang {language} sa buong pagsulat. Isama ang Objectives, Subject Matter, Procedure, at Evaluation. MAHALAGA: Huwag gumamit ng Markdown symbols tulad ng #, *, _, o LaTeX mathematical codes (tulad ng \\begin, \\end, $$, \\textbf). Gumamit lamang ng malinis na plain text at standard numbers para madaling basahin at i-print sa Word."
                    
                    with st.spinner("Ginagawa ang Lesson Plan..."):
                        response = model.generate_content(prompt)
                        st.session_state.tries_used += 1
                        st.session_state.lesson_plan_result = response.text
                except Exception as e:
                    st.error(f"May error: {e}")

        # Result display and Word download
        if "lesson_plan_result" in st.session_state:
            st.success("Tapos na!")
            st.write(st.session_state.lesson_plan_result)
            
            docx_file = create_docx(st.session_state.lesson_plan_result, title=f"Lesson Plan: {topic}")
            st.download_button(
                label="📄 Download Editable Word (.docx) File",
                data=docx_file,
                file_name=f"Lesson_Plan_{topic}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # -------------------------------------------------------------
    # TAB 2: Quiz Generator
    # -------------------------------------------------------------
    elif selected_service == "❓ Quiz Generator":
        st.subheader("❓ Quick Quiz Generator")
        
        col1, col2 = st.columns(2)
        with col1:
            quiz_topic = st.text_input("Topic para sa Quiz:")
            num_items = st.slider("Bilang ng items:", 5, 20, 10)
        with col2:
            quiz_language = st.selectbox("Wika / Language:", ["Tagalog / Filipino", "English", "Taglish"])
        
        if st.button("Generate Quiz"):
            if not api_key:
                st.warning("Kailangan ng API Key para gumana.")
            elif not quiz_topic:
                st.warning("Paki-input ang Topic.")
            else:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.8-flash')
                    
                    # Strict prompt to prevent LaTeX and markdown clutter
                    prompt = f"Gumawa ng {num_items}-item multiple choice quiz tungkol sa '{quiz_topic}'. Gamitin ang wikang {quiz_language} sa pagsulat ng mga tanong at pagpipilian. Isama ang Answer Key sa pinakababa. MAHALAGA: Huwag gumamit ng Markdown symbols (#, *, _) o LaTeX codes. Gumamit lamang ng malinis na plain text na pwedeng-pwede agad i-print."
                    
                    with st.spinner("Ginagawa ang Quiz..."):
                        response = model.generate_content(prompt)
                        st.session_state.tries_used += 1
                        st.session_state.quiz_result = response.text
                except Exception as e:
                    st.error(f"May error: {e}")

        # Result display and Word download
        if "quiz_result" in st.session_state:
            st.success("Tapos na!")
            st.write(st.session_state.quiz_result)
            
            docx_file = create_docx(st.session_state.quiz_result, title=f"Quiz: {quiz_topic}")
            st.download_button(
                label="📄 Download Editable Word (.docx) File",
                data=docx_file,
                file_name=f"Quiz_{quiz_topic}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # -------------------------------------------------------------
    # TAB 3: Class List Cleaner
    # -------------------------------------------------------------
    elif selected_service == "🧹 Class List Cleaner":
        st.subheader("🧹 Class List Format Cleaner")
        
        col1, col2 = st.columns(2)
        with col1:
            list_title = st.text_input("Header / Class Name (e.g., Grade 1 - Sunflower):", value="Class List")
        with col2:
            list_language = st.selectbox("Header Language Format:", ["Tagalog / Filipino", "English"])

        raw_names = st.text_area("I-paste ang magulong listahan ng pangalan dito:")
        
        if st.button("Clean & Format Names"):
            if raw_names:
                lines = [name.strip().upper() for name in raw_names.split("\n") if name.strip()]
                lines.sort()
                st.session_state.tries_used += 1
                
                header_text = f"LISTAHAN NG MGA MAG-AARAL - {list_title}" if list_language == "Tagalog / Filipino" else f"CLASS LIST - {list_title}"
                formatted_text = f"{header_text}\n" + "="*30 + "\n\n" + "\n".join([f"{idx+1}. {name}" for idx, name in enumerate(lines)])
                
                st.session_state.cleaned_list_result = formatted_text

        # Result display and Word download
        if "cleaned_list_result" in st.session_state:
            st.success("Nalinis at Naka-alphabetical Order na:")
            st.code(st.session_state.cleaned_list_result)
            
            docx_file = create_docx(st.session_state.cleaned_list_result, title="Cleaned Class List")
            st.download_button(
                label="📄 Download Class List (.docx)",
                data=docx_file,
                file_name=f"{list_title}_Cleaned.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
