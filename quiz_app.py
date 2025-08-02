import streamlit as st
import fitz  # PyMuPDF
import random
import re

st.set_page_config(page_title="آزمون PPL", layout="centered")
st.title("🧪 آزمون تمرینی PPL")

# وضعیت اولیه
if "started" not in st.session_state:
    st.session_state.started = False
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

# بارگذاری فایل PDF
try:
    doc = fitz.open("ppl.pdf")
except:
    st.error("❌ فایل ppl.pdf پیدا نشد. آن را در کنار این اسکریپت قرار بده.")
    st.stop()

# فرم تنظیمات آزمون
if not st.session_state.started:
    st.success("✅ فایل آزمون با موفقیت بارگذاری شد.")

    col1, col2 = st.columns(2)
    start_page = col1.number_input("📄 صفحه شروع", min_value=0, max_value=len(doc)-1, value=0)
    end_page = col2.number_input("📄 صفحه پایان", min_value=0, max_value=len(doc)-1, value=min(5, len(doc)-1))

    order_type = st.radio("🔄 ترتیب سوالات", ["نوبتی", "تصادفی"])

    if st.button("🎯 شروع آزمون"):
        questions = []

        for i in range(start_page, end_page + 1):
            text = doc.load_page(i).get_text()
            lines = text.split("\n")

            for j in range(len(lines)):
                line = lines[j].strip()

                if line.startswith("Answer ("):
                    correct = line.split("Answer (")[1][0]
                    options = {}
                    question_lines = []

                    for k in range(j - 1, max(j - 15, -1), -1):
                        l = lines[k].strip()
                        if re.match(r"^\([A-D]\)", l):
                            label = l[1]
                            option_text = l[3:].strip()
                            options[label] = option_text
                        elif len(options) > 0:
                            question_lines.insert(0, l)

                    full_question = "\n".join(question_lines).strip()

                    if full_question and options:
                        questions.append({
                            "question": full_question,
                            "options": dict(sorted(options.items())),  # مرتب‌سازی
                            "answer": correct
                        })

        if order_type == "تصادفی":
            random.shuffle(questions)

        if questions:
            st.session_state.questions = questions
            st.session_state.started = True
        else:
            st.warning("❗ در این بازه سوالی پیدا نشد.")

# نمایش سوالات
else:
    questions = st.session_state.questions
    q_idx = st.session_state.current_q
    q_data = questions[q_idx]

    st.subheader(f"❓ سوال {q_idx + 1} از {len(questions)}")
    st.markdown(f"**{q_data['question']}**")

    options = q_data["options"]
    user_choice = st.radio(
        "گزینه‌ها:",
        list(options.keys()),
        format_func=lambda x: f"({x}) {options[x]}",
        key=f"opt_{q_idx}"
    )

    col1, col2, col3 = st.columns([1, 1, 2])

    if col1.button("بررسی پاسخ"):
        if user_choice == q_data["answer"]:
            st.success("✅ درست جواب دادی!")
        else:
            correct_text = f"({q_data['answer']}) {options[q_data['answer']]}"
            st.error(f"❌ اشتباه بود. پاسخ درست: {correct_text}")

    if col2.button("سوال بعدی"):
        if q_idx + 1 < len(questions):
            st.session_state.current_q += 1
        else:
            st.info("🎉 آزمون تموم شد! سوال دیگه‌ای نیست.")

    if col3.button("🔁 بازگشت به تنظیمات"):
        st.session_state.started = False
        st.session_state.current_q = 0
        st.session_state.questions = []
