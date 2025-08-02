import streamlit as st
import fitz  # PyMuPDF
import re
import random

st.set_page_config(page_title="✈️ آزمون PPL", page_icon="🧠", layout="centered")
st.title("📝 آزمون تمرینی PPL")
st.markdown("برای شروع آزمون، تنظیم صفحات را انتخاب کن و شروع کن!")

# وضعیت شروع آزمون
if "started" not in st.session_state:
    st.session_state.started = False

# تنظیمات آزمون قبل از شروع
if not st.session_state.started:
    start_page = st.number_input("📄 صفحه شروع:", min_value=1, step=1, value=1)
    end_page = st.number_input("📄 صفحه پایان:", min_value=start_page, step=1, value=start_page+1)
    random_order = st.checkbox("🔀 سوالات به صورت تصادفی نمایش داده شوند", value=False)

    if st.button("▶️ شروع آزمون"):
        st.session_state.start_page = start_page
        st.session_state.end_page = end_page
        st.session_state.random_order = random_order
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.started = True

# تابع استخراج متن از PDF کنار فایل
def extract_text_from_pdf(file_path, start, end):
    doc = fitz.open(file_path)
    text = ""
    for i in range(start - 1, end):
        text += doc[i].get_text()
    return text

# تبدیل متن به سوالات
def parse_questions(text):
    questions = []
    pattern = re.compile(
        r"(\d+\..*?)(?=Answer \([A-D]\) is correct)", 
        re.DOTALL
    )
    answers = re.findall(r"Answer \(([A-D])\) is correct", text)
    q_matches = pattern.findall(text)

    for q_text, ans in zip(q_matches, answers):
        option_pattern = re.compile(r"\(([A-D])\)\s*([^\n]+)")
        options = dict(option_pattern.findall(q_text))
        question_text = re.sub(r"\(([A-D])\)\s*[^\n]+", "", q_text).strip()
        question_text = re.sub(r"\n+", "\n", question_text).strip()

        questions.append({
            "question": question_text,
            "options": options,
            "answer": ans
        })
    return questions

# نمایش سوال
def show_question(q, idx):
    st.markdown(f"**سوال {idx + 1}:**\n\n{q['question']}")
    choices = [f"{key}. {val}" for key, val in q["options"].items()]
    user_choice = st.radio("جواب خود را انتخاب کنید:", choices, key=f"q_{idx}")

    if st.button("ارسال جواب", key=f"submit_{idx}"):
        selected = user_choice[0]
        if selected == q["answer"]:
            st.success("جواب شما درست است! 🎉")
            st.session_state.score += 1
        else:
            st.error(f"جواب شما اشتباه است! جواب درست: {q['answer']}")

        st.session_state.current_q += 1
        st.experimental_rerun()

# منطق اصلی
if st.session_state.started:
    try:
        if "questions" not in st.session_state:
            text = extract_text_from_pdf("ppl.pdf", st.session_state.start_page, st.session_state.end_page)
            questions = parse_questions(text)
            if st.session_state.random_order:
                random.shuffle(questions)
            st.session_state.questions = questions

        questions = st.session_state.questions

        if not questions:
            st.warning("در این بازه صفحه سوالی پیدا نشد.")
            if st.button("بازگشت به تنظیمات"):
                st.session_state.started = False
                st.experimental_rerun()
        else:
            if st.session_state.current_q < len(questions):
                show_question(questions[st.session_state.current_q], st.session_state.current_q)
                st.write(f"سوال {st.session_state.current_q + 1} از {len(questions)}")
                st.write(f"امتیاز فعلی: {st.session_state.score}")
            else:
                st.success(f"آزمون تمام شد! نمره شما: {st.session_state.score} از {len(questions)}")
                if st.button("شروع مجدد آزمون"):
                    st.session_state.started = False
                    st.session_state.current_q = 0
                    st.session_state.score = 0
                    st.experimental_rerun()

    except Exception as e:
        st.error(f"خطا در پردازش فایل PDF یا استخراج سوالات: {e}")
        if st.button("بازگشت به تنظیمات"):
            st.session_state.started = False
            st.experimental_rerun()
else:
    st.info("لطفاً تنظیمات را انتخاب و آزمون را شروع کنید.")
