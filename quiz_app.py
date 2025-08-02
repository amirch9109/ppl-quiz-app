import streamlit as st
from docx import Document
import re
import random

st.set_page_config(page_title="✈️ آزمون PPL", page_icon="🧠", layout="centered")
st.title("📝 آزمون تمرینی PPL")
st.markdown("سوالات از فایل `ppl.docx` کنار این برنامه خوانده می‌شود.")

def load_docx_text(file_path):
    doc = Document(file_path)
    full_text = "\n".join([para.text for para in doc.paragraphs])
    return full_text

def parse_questions(text):
    questions = []
    # الگو برای هر سوال و جواب؛ دقت کن فقط متن سوال تا قبل از 'Answer (X) is correct' میگیره
    q_pattern = re.compile(r"(\d+\..*?)(?=Answer \([A-D]\) is correct)", re.DOTALL)
    a_pattern = re.compile(r"Answer \(([A-D])\) is correct")

    q_matches = q_pattern.findall(text)
    a_matches = a_pattern.findall(text)

    for q, a in zip(q_matches, a_matches):
        # حالا از متن سوال، خط های اضافی و متن دلیل جواب رو پاک کنیم
        # معمولاً دلیل جواب بعد از 'Answer...' در پاراگراف جداست؛ چون اون رو جداگانه نگرفتیم، باید خودمون حذف کنیم.
        # پاک کردن خطوطی که شامل 'Answer' یا دلیل هست:
        q_clean = "\n".join([line for line in q.split('\n') if not line.strip().startswith("Answer")])
        questions.append({
            "question": q_clean.strip(),
            "answer": a.strip()
        })
    return questions

docx_file = "ppl.docx"

st.sidebar.header("تنظیمات آزمون")
start_page = st.sidebar.number_input("📄 صفحه شروع (فقط عدد وارد کن، مثلاً 1)", min_value=1, value=1, step=1)
end_page = st.sidebar.number_input("📄 صفحه پایان (عدد >= شروع)", min_value=start_page, value=10, step=1)
random_order = st.sidebar.checkbox("🔀 سوالات به صورت تصادفی باشند")

if st.sidebar.button("▶️ شروع آزمون"):
    text = load_docx_text(docx_file)
    questions = parse_questions(text)

    if not questions:
        st.error("⛔ هیچ سوالی پیدا نشد! فرمت فایل یا متن را چک کن.")
    else:
        if random_order:
            random.shuffle(questions)
        st.session_state.score = 0
        st.session_state.index = 0
        st.session_state.questions = questions

if "questions" in st.session_state:
    questions = st.session_state.questions
    idx = st.session_state.index
    score = st.session_state.score

    if idx < len(questions):
        q = questions[idx]
        st.markdown(f"### سوال {idx+1}:\n{q['question']}")

        # استخراج گزینه‌ها (A تا D) دقیق‌تر
        options_pattern = re.compile(r"([A-D])\.\s*(.+)")
        opts = options_pattern.findall(q['question'])
        options_dict = {opt[0]: opt[1] for opt in opts}

        # اگر گزینه نبود، پیش‌فرض a تا d رو بگذار
        if not options_dict:
            options_dict = {"A": "گزینه A", "B": "گزینه B", "C": "گزینه C", "D": "گزینه D"}

        choice = st.radio("گزینه‌ی شما:", list(options_dict.keys()))

        if st.button("ثبت پاسخ"):
            if choice == q['answer']:
                st.success("✅ درست گفتی!")
                st.session_state.score += 1
            else:
                st.error(f"❌ اشتباه! جواب درست: {q['answer']}")
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
