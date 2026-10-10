import streamlit as st
import google.generativeai as genai
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
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
    return {}, None

def save_github_db(db_data, sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    content_encoded = base64.b64encode(json.dumps(db_data, indent=4).encode('utf-8')).decode('utf-8')
    payload = {
        "message": "Auto-update GCash Subscription DB",
        "content": content_encoded,
        "sha": sha
    }
    requests.put(url, headers=headers, json=payload)

def verify_and_register_payment(ref_number):
    try:
        db, sha = get_github_db()
        today = datetime.now().date()
        ref_str = str(ref_number).strip()

        if ref_str in db:
            exp_date = datetime.strptime(db[ref_str]["expiration_date"], "%Y-%m-%d").date()
            if today <= exp_date:
                return "ACTIVE", exp_date
            else:
                return "EXPIRED", exp_date

        new_exp_date = today + timedelta(days=30)
        db[ref_str] = {
            "date_activated": str(today),
            "expiration_date": str(new_exp_date)
        }
        save_github_db(db, sha)
        return "NEW_ACTIVATED", new_exp_date

    except Exception as e:
        return "ERROR", str(e)

# --- TRACKING SETUP (QUERY PARAMS + COOKIE) ---
cookie_manager = stx.CookieManager()

query_params = st.query_params
url_tries = query_params.get("tries", None)

try:
    cookie_tries = cookie_manager.get(cookie="guro_hub_tries")
except:
    cookie_tries = None

saved_tries = 0
if url_tries is not None:
    try: saved_tries = max(saved_tries, int(url_tries))
    except: pass
if cookie_tries is not None:
    try: saved_tries = max(saved_tries, int(cookie_tries))
    except: pass

FREE_LIMIT = 3
if "tries_count" not in st.session_state:
    st.session_state.tries_count = saved_tries

if "is_unlocked" not in st.session_state:
    st.session_state.is_unlocked = False

if st.session_state.tries_count > FREE_LIMIT:
    st.session_state.tries_count = FREE_LIMIT

tries_left = max(0, FREE_LIMIT - st.session_state.tries_count)

# --- SIDEBAR (NAVIGATION & GCASH UNLOCK) ---
st.sidebar.title("📌 Navigation")
service = st.sidebar.radio("Pumili ng Service:", ["📝 Lesson Plan Generator", "❓ Quiz Generator", "🧹 Class List Cleaner"])

st.sidebar.markdown("---")
if st.session_state.is_unlocked:
    st.sidebar.success("✅ VIP Subscriber Access Active (Unlimited for 1 Month)!")
else:
    if tries_left > 0:
        st.sidebar.success(f"🎁 Free Trial: **{tries_left}** / {FREE_LIMIT} tries left")
    else:
        st.sidebar.error("🔒 Ubos na ang iyong 3 Free Tries!")
    
    st.sidebar.subheader("💳 Instant Unlock via GCash")
    st.sidebar.caption("1. I-scan ang QR Code o mag-send ng ₱99 sa GCash.\n2. I-paste ang Ref No. para mag-unlock.")
    st.sidebar.image("gcashqrcode.jpg", caption="📲 Scan to Pay ₱99 via GCash for 1-Month VIP Access")
    
    gcash_ref = st.sidebar.text_input("GCash Reference No.:")
    if st.sidebar.button("Verify & Unlock"):
        ref_input = gcash_ref.strip()
        if len(ref_input) >= 10:
            status, exp_date = verify_and_register_payment(ref_input)
            
            if status in ["ACTIVE", "NEW_ACTIVATED"]:
                st.session_state.is_unlocked = True
                st.sidebar.success(f"🎉 VIP Access Active hanggang: {exp_date}")
                st.rerun()
            elif status == "EXPIRED":
                st.sidebar.error(f"❌ Expired na ang VIP Pass noong {exp_date}. Paki-renew via GCash.")
            else:
                st.sidebar.error("⚠️ Error sa pag-verify. Siguraduhing naisave ang GITHUB_TOKEN sa Secrets.")
        else:
            st.sidebar.error("⚠️ Invalid Reference Number. Paki-check ang GCash receipt.")

# --- MAIN APP HEADER ---
st.title("🏫 Guro Hub")
st.write("Ang iyong All-in-One Assistant para sa Lesson Plans, Quizzes, at Class Data.")

# --- CHECK USAGE LIMIT ---
def can_use_service():
    if st.session_state.is_unlocked:
        return True
    if st.session_state.tries_count < FREE_LIMIT:
        return True
    return False

def register_usage():
    if not st.session_state.is_unlocked:
        st.session_state.tries_count += 1
        try:
            cookie_manager.set("guro_hub_tries", str(st.session_state.tries_count), expires_at=datetime.now() + timedelta(days=365))
        except:
            pass
        st.query_params["tries"] = str(st.session_state.tries_count)

def generate_ai_response(prompt_text):
    # Sinusubukan gamitin ang gemini-1.5-flash na may explicit safety at configuration
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt_text)
        if response and response.text:
            return response.text
    except Exception as e:
        # Fallback sa gemini-pro kung magka-issue sa flash
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt_text)
            if response and response.text:
                return response.text
        except Exception:
            pass
        return f"⚠️ Error Details: {str(e)}"
    return "⚠️ Error: Hindi ma-access ang Gemini AI Model."

# --- SERVICE 1: LESSON PLAN GENERATOR ---
if service == "📝 Lesson Plan Generator":
    st.header("📝 DepEd/CHED Lesson Plan Generator")
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Subject (e.g., Science, Math):")
        grade_level = st.selectbox("Grade Level:", ["Grade 1-3", "Grade 4-6", "Grade 7-10", "Grade 11-12", "College"])
    with col2:
        language = st.selectbox("Wika / Language:", ["English", "Tagalog/Filipino"])
        topic = st.text_input("Topic / Aralin:")

    if st.button("Generate Lesson Plan"):
        if not can_use_service():
            st.error("🔒 Ubos na ang iyong 3 Free Tries! Mag-unlock via GCash para sa unlimited access.")
        elif not subject or not topic:
            st.warning("Paki-sulat ang Subject at Topic.")
        else:
            with st.spinner("Gumagawang Lesson Plan..."):
                prompt = f"Gumawa ng kumpletong 4As Lesson Plan (Objectives, Subject Matter, Procedure: Activity, Analysis, Abstraction, Application, Assessment) sa wikalang {language} para sa asignaturang {subject}, {grade_level}, tungkol sa araling '{topic}'."
                response_text = generate_ai_response(prompt)
                
                register_usage()
                st.markdown("### 📜 Resulta:")
                st.write(response_text)

# --- SERVICE 2: QUIZ GENERATOR ---
elif service == "❓ Quiz Generator":
    st.header("❓ Instant Quiz Generator")
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        quiz_topic = st.text_input("Topic ng Quiz:")
        quiz_grade = st.selectbox("Grade Level (Quiz):", ["Grade 1-3", "Grade 4-6", "Grade 7-10", "Grade 11-12", "College"], key="q_grade")
    with q_col2:
        quiz_lang = st.selectbox("Wika ng Quiz:", ["English", "Tagalog/Filipino"], key="q_lang")
        num_q = st.slider("Bilang ng Tanong:", 5, 20, 10)
    
    quiz_type = st.selectbox("Uri ng Exam:", ["Multiple Choice", "Identification", "True/False", "Mixed"])

    if st.button("Generate Quiz"):
        if not can_use_service():
            st.error("🔒 Ubos na ang iyong 3 Free Tries! Mag-unlock via GCash para sa unlimited access.")
        elif not quiz_topic:
            st.warning("Paki-sulat ang topic ng quiz.")
        else:
            with st.spinner("Gumagawang Quiz at Answer Key..."):
                prompt = f"Gumawa ng {num_q} items na {quiz_type} quiz tungkol sa '{quiz_topic}' para sa {quiz_grade} sa wikalang {quiz_lang}. Isama ang Answer Key sa dulo."
                response_text = generate_ai_response(prompt)
                
                register_usage()
                st.markdown("### 📄 Quiz Paper & Answer Key:")
                st.write(response_text)

# --- SERVICE 3: CLASS LIST CLEANER ---
elif service == "🧹 Class List Cleaner":
    st.header("🧹 Class List Format Cleaner")
    raw_names = st.text_area("I-paste ang magulong listahan ng pangalan dito:", height=150)
    sort_order = st.radio("Pagsusunod-sunod:", ["Alphabetical (A-Z)", "As Is (Naka-format lang)"])

    if st.button("Clean & Format List"):
        if not can_use_service():
            st.error("🔒 Ubos na ang iyong 3 Free Tries! Mag-unlock via GCash para sa unlimited access.")
        elif not raw_names.strip():
            st.warning("Paki-paste muna ang listahan ng mga pangalan.")
        else:
            names_list = [name.strip().title() for name in raw_names.split('\n') if name.strip()]
            if sort_order == "Alphabetical (A-Z)":
                names_list.sort()
            
            register_usage()
            st.markdown("### ✨ Malinis na Listahan:")
            formatted_text = "\n".join([f"{i+1}. {name}" for i, name in enumerate(names_list)])
            st.text_area("Resulta (Ready to Copy):", formatted_text, height=200)
