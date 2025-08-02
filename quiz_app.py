import streamlit as st
import fitz  # PyMuPDF
import re
import random

st.set_page_config(page_title="✈️ آزمون PPL", page_icon="🧠", layout="centered")
st.title("📝 آزمون تمرینی PPL")
st.markdown("برای شروع آزمون، فایل PDF رو بارگذاری کن، صفحات رو مشخص کن و شروع کن!")

# ---------- بارگذاری فایل ----------
uploaded_file = st.file_uploader("📂 فایل PDF آزمون را انتخاب کن:", type=["pdf"])

# ---------- تنظیمات آزمون ----------
start_page = st.number_input("📄 صفحه شروع:", min_value=1, step=1)
end_page = st.number_input("📄 صفحه پایان:", min_value=start_page, step=1)
random_order = st.checkbox("🔀 سوالات به صورت تصادفی نمایش داده شوند")

# ---------- استخراج متن صفحات مشخص شده ----------
def extract_text_from_pdf(file, start, end):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for i in range(start - 1, end):
        text += doc[i].get_text()
    return text

# ---------- تبدیل متن به سوالات با گزینه و جواب ----------
def parse_questions(text):
    # جدا کردن سوال‌ها بر اساس شماره سوال (فرض: سوال با "1." شروع میشه)
    # و تا "Answer (X) is correct" ادامه داره
    questions = []
    # الگوی کامل سوال به همراه گزینه‌ها و جواب:
    # فرض: شماره سوال + متن سوال + خطوط گزینه‌ها (مثلا (A) گزینه) + خط جواب
    pattern = re.compile(
        r"(\d+\..*?)(?=Answer \([A-D]\) is correct)", 
        re.DOTALL
    )
    answers = re.findall(r"Answer \(([A-D])\) is correct", text)

    q_matches = pattern.findall(text)
    if len(q_matches) != len(answers):
        st.warning(f"⚠️ تعداد سوالات و جواب‌ها برابر نیست! سوال‌ها: {len(q_matches)} جواب‌ها: {len(answers)}")

    for q_text, ans in zip(q_matches, answers):
        # استخراج گزینه‌ها از متن سوال:
        option_pattern = re.compile(r"\(([A-D])\)\s*([^\n]+)")
        options = dict(option_pattern.findall(q_text))

        # استخراج متن سوال بدون گزینه‌ها
        question_text = re.sub(r"\(([A-D])\)\s*[^\n]+", "", q_text).strip()
        question_text = re.sub(r"\n+", "\n", question_text).strip()

        questions.append({
            "question": question_text,
            "options": options,
            "answer": ans
        })
    return questions

# ---------- بخش اصلی برنامه ----------

if uploaded_file is not None:
    full_text = extract_text_from_pdf(uploaded_file, start_page, end_page)
    questions = parse_questions(full_text)

    if not questions:
        st.warning("در این بازه صفحه سوالی پیدا نشد.")
    else:
        st.success(f"تعداد سوالات یافت شده: {len(questions)}")

        if random_order:
            random.shuffle(questions)

        if "current_q" not in st.session_state:
            st.session_state.current_q = 0
        if "score" not in st.session_state:
            st.session_state.score = 0

        def show_question(idx):
            q = questions[idx]
            st.markdown(f"**سوال {idx + 1}:**\n\n{q['question']}")
            choices = [f"{key}. {val}" for key, val in q["options"].items()]
            user_choice = st.radio("جواب خود را انتخاب کنید:", choices, key=f"q_{idx}")

            if st.button("ارسال جواب", key=f"submit_{idx}"):
                selected = user_choice[0]  # حرف گزینه انتخاب شده
                if selected == q["answer"]:
                    st.success("جواب شما درست است! 🎉")
                    st.session_state.score += 1
                else:
                    st.error(f"جواب شما اشتباه است! جواب درست: {q['answer']}")

                st.session_state.current_q += 1
                st.experimental_rerun()

        if st.session_state.current_q < len(questions):
            show_question(st.session_state.current_q)
            st.write(f"سوال {st.session_state.current_q + 1} از {len(questions)}")
            st.write(f"امتیاز فعلی: {st.session_state.score}")
        else:
            st.success(f"آزمون تمام شد! نمره شما: {st.session_state.score} از {len(questions)}")
            if st.button("شروع مجدد آزمون"):
                st.session_state.current_q = 0
                st.session_state.score = 0
                st.experimental_rerun()

else:
    st.info("لطفاً فایل PDF آزمون را بارگذاری کنید.")
