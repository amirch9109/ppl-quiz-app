import streamlit as st
import fitz  # PyMuPDF
import re
import random

st.set_page_config(page_title="✈️ آزمون PPL", page_icon="🧠", layout="centered")
st.title("📝 آزمون تمرینی PPL")
st.markdown("سوالات از فایل PDF `ppl.pdf` کنار این برنامه خوانده می‌شود.")

# تنظیمات آزمون
start_page = st.sidebar.number_input("📄 صفحه شروع:", min_value=1, value=1, step=1)
end_page = st.sidebar.number_input("📄 صفحه پایان:", min_value=start_page, value=10, step=1)
random_order = st.sidebar.checkbox("🔀 سوالات به صورت تصادفی نمایش داده شوند")

def extract_text_from_pdf(file_path, start_page, end_page):
    doc = fitz.open(file_path)
    text = ""
    for i in range(start_page - 1, end_page):
        text += doc[i].get_text()
    return text

def parse_questions(text):
    questions = []
    # regex گرفتن هر سوال به همراه گزینه‌ها، تا قبل از Answer (X) is correct
    pattern = re.compile(
        r"(\d+\..*?(?:\n[A-D]\..*?)+)(?=Answer \([A-D]\) is correct)", 
        re.DOTALL
    )
    answer_pattern = re.compile(r"Answer \(([A-D])\) is correct")

    q_matches = pattern.findall(text)
    a_matches = answer_pattern.findall(text)

    for q_text, ans in zip(q_matches, a_matches):
        # جدا کردن گزینه‌ها
        opts = re.findall(r"([A-D])\.\s*(.*)", q_text)
        question_lines = q_text.split('\n')
        # خط اول سوال بدون گزینه‌ها
        question_title = question_lines[0].strip()
        options = {opt[0]: opt[1].strip() for opt in opts}
        questions.append({
            "question": question_title,
            "options": options,
            "answer": ans
        })
    return questions

if st.sidebar.button("▶️ شروع آزمون"):
    file_path = "ppl.pdf"
    text = extract_text_from_pdf(file_path, start_page, end_page)
    questions = parse_questions(text)
    if not questions:
        st.error("⛔ هیچ سوالی پیدا نشد! لطفاً بازه صفحات یا فایل PDF را چک کنید.")
    else:
        if random_order:
            random.shuffle(questions)
        st.session_state.questions = questions
        st.session_state.index = 0
        st.session_state.score = 0

if "questions" in st.session_state:
    questions = st.session_state.questions
    idx = st.session_state.index
    score = st.session_state.score

    if idx < len(questions):
        q = questions[idx]
        st.markdown(f"### سوال {idx + 1}:\n{q['question']}")

        choice = st.radio("گزینه‌ی شما:", list(q['options'].keys()), format_func=lambda x: f"{x}. {q['options'][x]}")

        if st.button("ثبت پاسخ"):
            if choice == q['answer']:
                st.success("✅ درست گفتی!")
                st.session_state.score += 1
            else:
                st.error(f"❌ اشتباه! جواب درست: {q['answer']}. {q['options'][q['answer']]}")
            st.session_state.index += 1
            st.experimental_rerun()

    else:
        st.markdown(f"### آزمون تمام شد! 🎉")
        st.markdown(f"نمره‌ی شما: **{score}** از **{len(questions)}**")
        if st.button("شروع مجدد آزمون"):
            del st.session_state.questions
            del st.session_state.index
            del st.session_state.score
            st.experimental_rerun()
