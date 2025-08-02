import streamlit as st
import fitz  # PyMuPDF
import re
import random
import os

st.set_page_config(page_title="✈️ آزمون PPL", page_icon="🧠", layout="centered")
st.title("📝 آزمون تمرینی PPL")

# ---------- وضعیت‌ها ----------
if "started" not in st.session_state:
    st.session_state.started = False
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0

# ---------- تابع‌ها ----------
def extract_text_from_pdf(file_path, start_page, end_page):
    if not os.path.exists(file_path):
        st.error("⛔ فایل ppl.pdf پیدا نشد. مطمئن شو فایل کنار این برنامه هست.")
        st.stop()

    doc = fitz.open(file_path)
    text = ""
    for i in range(start_page - 1, end_page):
        text += doc[i].get_text()
    return text

def parse_questions(text):
    questions = []

    q_pattern = re.compile(r"(\d+\..*?)(?=Answer \([A-D]\) is correct)", re.DOTALL)
    a_pattern = re.compile(r"Answer \(([A-D])\) is correct")

    q_matches = q_pattern.findall(text)
    a_matches = a_pattern.findall(text)

    for q, a in zip(q_matches, a_matches):
        option_pattern = re.compile(r"\(([A-D])\)\s*([^\n]+)")
        options = dict(option_pattern.findall(q))
        question_text = re.sub(r"\(([A-D])\)\s*[^\n]+", "", q).strip()

        questions.append({
            "question": question_text,
            "options": options,
            "answer": a
        })
    return questions

def show_question(q_data, idx):
    st.markdown(f"**سوال {idx + 1}:**")
    st.markdown(q_data["question"])

    options = q_data["options"]
    if not options:
        st.warning("⚠️ گزینه‌ای برای این سوال پیدا نشد.")
        return

    choices = [f"{k}. {v}" for k, v in options.items()]
    user_answer = st.radio("جواب شما:", choices, key=f"q_{idx}")

    if st.button("ثبت پاسخ", key=f"submit_{idx}"):
        selected = user_answer[0]
        if selected == q_data["answer"]:
            st.success("✅ درست گفتی!")
            st.session_state.score += 1
        else:
            st.error(f"❌ غلط بود. جواب درست: {q_data['answer']}")
        st.session_state.current_q += 1
        st.experimental_rerun()

# ---------- رابط تنظیمات ----------
if not st.session_state.started:
    with st.form("settings_form"):
        start_page = st.number_input("📄 از چه صفحه‌ای شروع کنم؟", min_value=1, step=1, value=1)
        end_page = st.number_input("📄 تا چه صفحه‌ای برم؟", min_value=start_page, step=1, value=start_page+1)
        random_order = st.checkbox("🔀 سوالات رندوم باشن؟", value=True)
        submit = st.form_submit_button("▶️ شروع آزمون")

    if submit:
        try:
            text = extract_text_from_pdf("ppl.pdf", start_page, end_page)
            questions = parse_questions(text)
            if not questions:
                st.warning("⛔ هیچ سوالی پیدا نشد. صفحات رو بررسی کن.")
            else:
                if random_order:
                    random.shuffle(questions)
                st.session_state.questions = questions
                st.session_state.started = True
                st.session_state.current_q = 0
                st.session_state.score = 0
                st.experimental_rerun()
        except Exception as e:
            st.error(f"خطایی رخ داد: {e}")

# ---------- آزمون ----------
if st.session_state.started:
    questions = st.session_state.questions
    current_q = st.session_state.current_q

    if current_q < len(questions):
        show_question(questions[current_q], current_q)
        st.info(f"سوال {current_q + 1} از {len(questions)} | امتیاز: {st.session_state.score}")
    else:
        st.success(f"🎉 آزمون تموم شد! نمره نهایی شما: {st.session_state.score} از {len(questions)}")
        if st.button("🔁 شروع دوباره"):
            for k in ["started", "current_q", "score", "questions"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.experimental_rerun()
