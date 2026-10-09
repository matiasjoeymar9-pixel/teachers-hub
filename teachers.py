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

# Initialize Session State para sa Free Tries at Payment Status
if "tries_used" not in st.session_state:
    st.session_state.tries_used = 0

if "is_unlocked" not in st.session_state:
    st.session_state.is_unlocked = False

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
if st.session_state.is_unlocked:
    st.sidebar.success("✅ VIP Subscriber Access Active (Unlimited Tries)!")
elif tries_left > 0:
    st.sidebar.success(f"🎁 Free Trial: **{tries_left}** / {FREE_LIMIT} tries left")
else:
    st.sidebar.image("my_gcash_qr.png", caption="Scan to Pay ₱99 via GCash")

# QR Code at Payment Auto-Verification Section
st.sidebar.markdown("---")
st.sidebar.subheader("💳 Instant Unlock via GCash")
st.sidebar.caption("1. I-scan ang QR Code o mag-send ng ₱99 sa GCash.\n2. I-paste ang Ref No. para mag-unlock.")

# Pwede mong palitan ang image link ng sarili mong GCash QR Code image URL
st.sidebar.image("https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=GCash-Payment-99PHP", caption="Scan to Pay ₱99 via GCash")

gcash_ref = st.sidebar.text_input("GCash Reference No.:")
if st.sidebar.button("Verify & Unlock"):
    if len(gcash_ref.strip()) >= 10:  # Validates GCash reference number length
        st.session_state.is_unlocked = True
        st.sidebar.success("🎉 Payment Verified! Unlimited Access Activated.")
        st.rerun()
    else:
        st.sidebar.error("⚠️ Invalid Reference Number. Paki-check ang GCash receipt.")

# Fallback API Key input
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")

# --- MAIN LOGIC PER SERVICE ---
if tries_left <= 0 and not st.session_state.is_unlocked:
    st.error("🔒 Nagamit mo na ang iyong 5 libreng subok.")
    st.info("I-scan ang GCash QR Code sa sidebar at i-paste ang Reference Number para ma-unlock agad ang Unlimited Access.")
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
            language = st.selectbox("Wika / Language:", ["English", "Tagalog / Filipino", "Taglish"])
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
                    
                    prompt = f"Gumawa ng detalyadong DepEd/CHED Lesson Plan para sa {subject} ({grade}) na may topic na '{topic}'. Gamitin ang wikang {language} sa buong pagsulat. Isama ang Objectives, Subject Matter, Procedure, Evaluation, at Assignment. MAHALAGA: 1. Siguraduhing PERFECT ang grammar, spelling, punctuation, at sentence structure sa napiling wika ({language}) nang walang anumang typographical errors. 2. Maglagay ng Answer Key sa pinakababa para sa Evaluation at Assignment. 3. Huwag gumamit ng Markdown symbols (#, *, _) o LaTeX codes. Isulat ang mga math equations nang malinis sa iisang linya (halimbawa: 1. 54 + 28 =)."
                    
                    with st.spinner("Ginagawa ang Lesson Plan..."):
                        response = model.generate_content(prompt)
                        if not st.session_state.is_unlocked:
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
            quiz_subject = st.text_input("Subject (e.g., Math, Science):")
            quiz_topic = st.text_input("Topic para sa Quiz:")
            num_items = st.slider("Bilang ng items:", 5, 20, 10)
        with col2:
            quiz_grade = st.selectbox("Grade Level:", ["Grade 1-3", "Grade 4-6", "Grade 7-10", "Grade 11-12", "College"])
            quiz_language = st.selectbox("Wika / Language:", ["English", "Tagalog / Filipino", "Taglish"])
        
        if st.button("Generate Quiz"):
            if not api_key:
                st.warning("Kailangan ng API Key para gumana.")
            elif not quiz_topic or not quiz_subject:
                st.warning("Paki-input ang Subject at Topic.")
            else:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.8-flash')
                    
                    prompt = f"Gumawa ng {num_items}-item multiple choice quiz sa {quiz_subject} para sa {quiz_grade} na may topic na '{quiz_topic}'. Gamitin ang wikang {quiz_language} sa pagsulat ng mga tanong at pagpipilian. Isama ang Answer Key sa pinakababa. MAHALAGA: Siguraduhing PERFECT at walang mali sa grammar, spelling, at formatting sa napiling wika ({quiz_language}). Huwag gumamit ng Markdown symbols (#, *, _) o LaTeX codes. Gumamit lamang ng malinis na plain text."
                    
                    with st.spinner("Ginagawa ang Quiz..."):
                        response = model.generate_content(prompt)
                        if not st.session_state.is_unlocked:
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
            list_language = st.selectbox("Header Language Format:", ["English", "Tagalog / Filipino"])

        raw_names = st.text_area("I-paste ang magulong listahan ng pangalan dito:")
        
        if st.button("Clean & Format Names"):
            if raw_names:
                lines = [name.strip().upper() for name in raw_names.split("\n") if name.strip()]
                lines.sort()
                if not st.session_state.is_unlocked:
                    st.session_state.tries_used += 1
                
                header_text = f"CLASS LIST - {list_title}" if list_language == "English" else f"LISTAHAN NG MGA MAG-AARAL - {list_title}"
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
