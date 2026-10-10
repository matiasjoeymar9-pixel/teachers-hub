import streamlit as st
from docx import Document
import io
import json
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Guro Hub - One-Stop Educator Assistant",
    page_icon="🏫",
    layout="wide"
)

# --- SMART TEMPLATE GENERATOR ENGINE ---
def generate_template_lesson_plan(subject, grade_level, language, topic):
    if language == "Filipino":
        return f"""DETAILED LESSON PLAN IN {subject.upper()} ({grade_level.upper()})

I. MGA LAYUNIN
Sa pagtatapos ng araling ito, ang mga mag-aaral ay inaasahang:
1. Natutukoy at naipaliliwanag ang mga pangunahing konseptong tungkol sa {topic}.
2. Nailalapat ang mga kaalaman sa pagsagot sa mga pagsasanay at gawain.
3. Naipamamalas ang kawilihan, kooperasyon, at katumpakan sa pakikilahok sa klase.

II. PAKSANG-ARALIN
* Paksa: {topic}
* Asignatura: {subject}
* Antas: {grade_level}
* Sanggunian: DepEd Curriculum Guide at Gabay ng Guro
* Kagamitan: Visual aids, activity sheets, chalk and board

III. PAMAMARAAN (4-As Framework)
A. Panimulang Gawain (Balik-aral at Pagganyak)
- Maikling panalangin at pagtala ng liban.
- Pagbabalik-aral sa mga nakaraang aralin na may kinalaman sa {topic}.
- Pagbibigay ng maikling motibasyon o laro para sa mga mag-aaral.

B. Paglalahad (Activity)
- Paghahati ng klase sa maliliit na grupo.
- Pagbibigay ng gawain o senaryo na susubok sa paunang kaalaman ng mga bata tungkol sa {topic}.

C. Pagsusuri (Analysis)
- Pagtalakay sa mga naging sagot ng bawat grupo sa pamamagitan ng mga gabay na tanong.
- Pagpapaliwanag kung bakit gayon ang naging resulta ng gawain.

D. Paghahalaw (Abstraction)
- Pagbibigay ng guro ng pormal na lektura at paglalahad ng mga patakaran, pormula, o mahahalagang konseptong nakapaloob sa {topic}.
- Pagbibigay ng mga halimbawa at hakbang-hakbang na solusyon.

E. Paglalapat (Application)
- Pagsasagawa ng mga mag-aaral ng praktikal na gawain o sitwasyon sa pang-araw-araw na buhay kung saan magagamit ang {topic}.

IV. PAGTATAYA (Evaluation)
Panuto: Sagutin ang mga sumusunod na tanong sa isang malinis na papel.
1. Ano ang pangunahing katangian ng {topic}?
2. Magbigay ng isang halimbawa na nagpapakita ng aplikasyon nito.
3-5. Lutasin o sagutin ang ibinigay na pagsasanay ng guro.

SUSI SA PAGTATAYA (ANSWER KEY):
1. Ang {topic} ay tumutukoy sa... (Gabay ng guro para sa wastong sagot).
2. Halimbawa ng tamang aplikasyon o solusyon.
3-5. Detalyadong solusyon at tamang sagot para sa mga item 3 hanggang 5.

V. TAKDANG-ARALIN (Assignment)
Panuto: Kopyahin at sagutin sa inyong kwaderno.
1. Magsaliksik o magbigay ng dalawang karagdagang halimbawa tungkol sa {topic}.
2. Ihanda ang sarili para sa maikling pagsusulit sa susunod na pagkikita.

GABAY SA TAKDANG-ARALIN:
- Ang inaasahang sagot sa takdang-aralin ay kinabibilangan ng tamang paglalarawan at kumpletong hakbang.
"""
    else:
        return f"""DETAILED LESSON PLAN IN {subject.upper()} ({grade_level.upper()})

I. OBJECTIVES
At the end of the lesson, the students should be able to:
1. Define and explain fundamental concepts related to {topic}.
2. Apply learned concepts and solve exercises accurately.
3. Demonstrate active participation, cooperation, and critical thinking.

II. SUBJECT MATTER
* Topic: {topic}
* Subject Area: {subject}
* Grade Level: {grade_level}
* References: DepEd Curriculum Guide / Teacher's Guide
* Materials: Visual aids, worksheets, whiteboard markers

III. LEARNING PROCEDURE (4-As Framework)
A. Preliminary Activities
- Routine opening prayer and attendance check.
- Brief review of prerequisite concepts relevant to {topic}.
- Motivational activity to engage students.

B. Activity (Aktiviti)
- Group students into small collaborative teams.
- Distribute task cards or scenario worksheets focusing on {topic}.

C. Analysis (Analisis)
- Facilitate class discussion on group findings using guide questions.
- Connect student observations to the core lesson.

D. Abstraction (Abstraksyon)
- Deliver formal instruction outlining rules, theories, formulas, or steps regarding {topic}.
- Provide worked examples with clear explanations.

E. Application (Aplikasyon)
- Engage students in real-world problem-solving or practical exercises applying {topic}.

IV. EVALUATION (Pagtataya)
Directions: Answer the following questions on a separate sheet of paper.
1. State the core definition or principle of {topic}.
2. Provide an illustration or practical application.
3-5. Solve the given problem sets completely.

ANSWER KEY:
1. Correct conceptual definition of {topic}.
2. Standard expected example or illustration.
3-5. Complete step-by-step solution guide and final answers.

V. ASSIGNMENT (Takdang-Aralin)
Directions: Copy and answer the following exercises in your notebook.
1. Research and provide two additional examples related to {topic}.
2. Prepare for a short review session in our next meeting.

ASSIGNMENT SOLUTION GUIDE:
- Step-by-step breakdown of expected student answers for homework reinforcement.
"""

def generate_template_quiz(quiz_topic, num_items):
    quiz_body = f"""COMPREHENSIVE QUIZ IN {quiz_topic.upper()}
Total Items: {num_items}

DIRECTIONS: Read each item carefully. Write your complete answers and necessary solutions on a separate sheet of paper.

"""
    answer_key = f"""---
COMPLETE ANSWER KEY AND SOLUTION GUIDE\n"""
    
    for i in range(1, num_items + 1):
        quiz_body += f"{i}. (Question regarding {quiz_topic} - Item {i})\n   A) Choice A\n   B) Choice B\n   C) Choice C\n   D) Choice D\n\n"
        answer_key += f"Item {i}: Correct Answer is [Option/Value] \n- Explanation: Detailed step-by-step justification and solution for item {i}.\n"
        
    return quiz_body + "\n" + answer_key

# --- HELPER: CONVERT TEXT TO DOCX ---
def create_docx(text_content):
    doc = Document()
    doc.add_heading('Guro Hub - Generated Output', 0)
    for line in text_content.split('\n'):
        if line.startswith('# '):
            doc.add_heading(line.replace('# ', ''), level=1)
        elif line.startswith('## '):
            doc.add_heading(line.replace('## ', ''), level=2)
        elif line.startswith('### '):
            doc.add_heading(line.replace('### ', ''), level=3)
        else:
            if line.strip():
                doc.add_paragraph(line)
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- MAIN APP INTERFACE ---
st.title("🏫 Guro Hub")
st.write("Ang iyong All-in-One Assistant para sa Lesson Plans, Quizzes, at Class Data (Lightning Fast & Unlimited!).")

# Sidebar Navigation
st.sidebar.markdown("## 📌 Navigation")
service = st.sidebar.radio("Pumili ng Service:", ["📝 Lesson Plan Generator", "❓ Quiz Generator", "🧹 Class List Cleaner"])

st.sidebar.success("VIP Subscriber Access Active (Unlimited & No Quota Limits)!")

if service == "📝 Lesson Plan Generator":
    st.header("📝 DepEd/CHED Lesson Plan Generator")
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
    topic = st.text_input("Topic / Aralin:", "Addition of Fractions")

    if st.button("Generate Lesson Plan"):
        with st.spinner("Mabilis na gumagawa ng Lesson Plan..."):
            result = generate_template_lesson_plan(subject, grade_level, language, topic)
            st.markdown("## 📜 Resulta:")
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
    st.header("❓ Quiz Generator")
    quiz_topic = st.text_input("Paksa ng Quiz:", "Pandiwa")
    num_items = st.slider("Bilang ng Items:", 5, 20, 10)
    
    if st.button("Generate Quiz"):
        with st.spinner("Mabilis na gumagawa ng Quiz..."):
            result = generate_template_quiz(quiz_topic, num_items)
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
