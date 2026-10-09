import streamlit as st
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="Guro Hub - One-Stop Educator Assistant", page_icon="🏫", layout="centered")

# Initialize Session State para sa 5 Free Tries Counter
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

# Input ng API Key
api_key = st.sidebar.text_input("Gemini API Key:", type="password")

# --- MAIN LOGIC PER SERVICE ---
if tries_left <= 0:
    st.error("🔒 Nagamit mo na ang iyong 5 libreng subok.")
    st.info("I-send ang ₱99 subscription via GCash at i-send ang screenshot para ma-activate ang Pro Access.")
else:
    # Service 1: Lesson Plan Generator
    if selected_service == "📝 Lesson Plan Generator":
        st.subheader("📝 DepEd/CHED Lesson Plan Generator")
        subject = st.text_input("Subject (e.g., Science, English, Math):")
        grade = st.selectbox("Grade Level:", ["Grade 1-3", "Grade 4-6", "Grade 7-10", "Grade 11-12", "College"])
        topic = st.text_input("Topic / Aralin:")
        
        if st.button("Generate Lesson Plan"):
            if not api_key:
                st.warning("Paki-input ang iyong Gemini API Key sa sidebar.")
            elif not topic or not subject:
                st.warning("Paki-kumpleto ang Subject at Topic.")
            else:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    prompt = f"Gumawa ng detalyadong DepEd/CHED Lesson Plan para sa {subject} ({grade}) na may topic na '{topic}'. Isama ang Objectives, Subject Matter, Procedure, at Evaluation."
                    
                    with st.spinner("Ginagawa ang Lesson Plan..."):
                        response = model.generate_content(prompt)
                        st.session_state.tries_used += 1
                        st.success("Tapos na!")
                        st.write(response.text)
                except Exception as e:
                    st.error(f"May error sa API Key: {e}")

    # Service 2: Quiz Generator
    elif selected_service == "❓ Quiz Generator":
        st.subheader("❓ Quick Quiz Generator")
        quiz_topic = st.text_input("Topic para sa Quiz:")
        num_items = st.slider("Bilang ng items:", 5, 20, 10)
        
        if st.button("Generate Quiz"):
            if not api_key:
                st.warning("Paki-input ang iyong Gemini API Key sa sidebar.")
            elif not quiz_topic:
                st.warning("Paki-input ang Topic.")
            else:
                try:
                    genai.configure(api_key=api_key)
                   model = genai.GenerativeModel('gemini-2.5-flash')
                    prompt = f"Gumawa ng {num_items}-item multiple choice quiz tungkol sa '{quiz_topic}'. Isama ang Answer Key sa pinakababa."
                    
                    with st.spinner("Ginagawa ang Quiz..."):
                        response = model.generate_content(prompt)
                        st.session_state.tries_used += 1
                        st.success("Tapos na!")
                        st.write(response.text)
                except Exception as e:
                    st.error(f"May error sa API Key: {e}")

    # Service 3: Class List Cleaner
    elif selected_service == "🧹 Class List Cleaner":
        st.subheader("🧹 Class List Format Cleaner")
        raw_names = st.text_area("I-paste ang magulong listahan ng pangalan dito:")
        
        if st.button("Clean & Format Names"):
            if raw_names:
                lines = [name.strip().upper() for name in raw_names.split("\n") if name.strip()]
                lines.sort()
                st.session_state.tries_used += 1
                st.success("Nalinis at Naka-alphabetical Order na:")
                st.code("\n".join(lines))
