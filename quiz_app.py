import streamlit as st
import fitz
import random

st.set_page_config(page_title="آزمون PPL", layout="centered")
st.title("🧪 آزمون تمرینی PPL")

# ✅ نگه‌داشتن وضعیت آزمون
if "started" not in st.session_state:
    st.session_state.started = False

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

# --- بارگذاری فایل PDF ---
try:
    doc = fitz.open("ppl.pdf")
except:
    st.error("❌ فایل ppl.pdf یافت نشد.")
    st.stop()

# ✅ اگر آزمون هنوز شروع نشده:
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
                if lines[j].strip().startswith("Answer ("):
                    # گرفتن چند خط قبل از Answer
                    chunk = lines[j-5:j]
                    question_text = "\n".join(chunk).strip()
                    correct_answer = lines[j].strip().split("Answer (")[1][0]
                    questions.append((question_text, correct_answer))
        if order_type == "تصادفی":
            random.shuffle(questions)

        if questions:
            st.session_state.questions = questions
            st.session_state.started = True
        else:
            st.warning("سوالی در این بازه پیدا نشد.")
else:
    # ✅ آزمون شروع شده
    questions = st.session_state.questions
    q_idx = st.session_state.current_q
    question, correct = questions[q_idx]

    st.subheader(f"❓ سوال {q_idx + 1} از {len(questions)}")

    st.text_area("📘 متن سوال", question, height=200, disabled=True)

    user_answer = st.radio("پاسخ شما چیست؟", ["A", "B", "C", "D"], key=f"q_{q_idx}")

    col1, col2, col3 = st.columns([1, 1, 2])
    if col1.button("بررسی پاسخ"):
        if user_answer.upper() == correct.upper():
            st.success("✅ درست جواب دادی!")
        else:
            st.error(f"❌ اشتباه بود. پاسخ درست: {correct}")

    if col2.button("سوال بعدی"):
        if q_idx + 1 < len(questions):
            st.session_state.current_q += 1
        else:
            st.info("🎉 تموم شد! سوال دیگه‌ای باقی نمونده.")

    if col3.button("🔄 بازگشت به تنظیمات"):
        st.session_state.started = False
        st.session_state.current_q = 0
        st.session_state.questions = []
