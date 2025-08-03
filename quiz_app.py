import streamlit as st
import fitz  # PyMuPDF
import re
import random

st.set_page_config(page_title="✈️ آزمون PPL", layout="centered")
st.title("📝 آزمون تمرینی PPL - نسخه PDF")

# ---------- تنظیمات از سایدبار ----------
st.sidebar.header("🔧 تنظیمات آزمون")
start_page = st.sidebar.number_input("📄 صفحه شروع", min_value=1, value=1)
end_page = st.sidebar.number_input("📄 صفحه پایان", min_value=start_page, value=10)
random_order = st.sidebar.checkbox("🔀 سوالات به صورت تصادفی باشند")

# ---------- مسیر فایل PDF (با اسم درست شده ppl.pdf) ----------
file_path = "ppl.pdf"

# ---------- تابع استخراج متن از PDF ----------
def extract_text_from_pdf(file_path, start_page, end_page):
    doc = fitz.open(file_path)
    text = ""
    for i in range(start_page - 1, end_page):
        text += doc[i].get_text()
    return text

# ---------- پردازش سوالات و گزینه‌ها ----------
def parse_questions(text):
    questions = []

    # گرفتن سوال تا قبل از "Answer (X) is correct"
    q_pattern = re.compile(r"(\d+\..*?(?:\n[A-D]\..*?){2,4})", re.DOTALL)
    a_pattern = re.compile(r"Answer \(([A-D])\) is correct")

    q_matches = q_pattern.findall(text)
    a_matches = a_pattern.findall(text)

    for q_text, ans in zip(q_matches, a_matches):
        lines = q_text.strip().split("\n")
        question_line = lines[0].strip()
        option_lines = lines[1:]

        options = {}
        for line in option_lines:
            match = re.match(r"([A-D])\.\s*(.+)", line.strip())
            if match:
                label, content = match.groups()
                options[label] = content.strip()

        questions.append({
            "question": question_line,
            "options": options,
            "answer": ans.strip()
        })

    return questions

# ---------- شروع آزمون ----------
if st.sidebar.button("▶️ شروع آزمون"):
    text = extract_text_from_pdf(file_path, start_page, end_page)
    questions = parse_questions(text)

    if not questions:
        st.error("⛔ سوالی پیدا نشد. صفحات یا ساختار فایل را بررسی کن.")
    else:
        if random_order:
            random.shuffle(questions)

        st.session_state.questions = questions
        st.session_state.index = 0
        st.session_state.score = 0

# ---------- نمایش سوالات ----------
if "questions" in st.session_state:
    questions = st.session_state.questions
    idx = st.session_state.index
    score = st.session_state.score

    if idx < len(questions):
        q = questions[idx]
        st.markdown(f"### سوال {idx + 1}: {q['question']}")
        choice = st.radio("گزینه‌ی خود را انتخاب کن:", list(q['options'].keys()), format_func=lambda x: f"{x}. {q['options'][x]}", key=idx)

        if st.button("ثبت پاسخ"):
            if choice == q['answer']:
                st.success("✅ درست گفتی!")
                st.session_state.score += 1
            else:
                st.error(f"❌ اشتباه! جواب درست: {q['answer']}. {q['options'][q['answer']]}")
            st.session_state.index += 1
            st.experimental_rerun()
    else:
        st.markdown("### 🎉 آزمون تمام شد!")
        st.markdown(f"📊 نمره نهایی: **{score} از {len(questions)}**")
        if st.button("شروع مجدد"):
            del st.session_state.questions
            del st.session_state.index
            del st.session_state.score
            st.experimental_rerun()
