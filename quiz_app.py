import streamlit as st
from docx import Document
import re
import random

st.set_page_config(page_title="✈️ آزمون PPL", page_icon="🧠", layout="centered")
st.title("📝 آزمون تمرینی PPL")
st.markdown("سوالات از فایل `ppl.docx` کنار این برنامه خوانده می‌شود.")

# تابع خواندن کل متن فایل ورد
def load_docx_text(file_path):
    doc = Document(file_path)
    full_text = "\n".join([para.text for para in doc.paragraphs])
    return full_text

# تابع استخراج سوال‌ها و جواب‌ها
def parse_questions(text):
    questions = []
    # الگوی سوال: شماره و متن تا قبل از جواب
    q_pattern = re.compile(r"(\d+\..*?)(?=Answer \([A-D]\) is correct)", re.DOTALL)
    # الگوی جواب صحیح
    a_pattern = re.compile(r"Answer \(([A-D])\) is correct")
    
    q_matches = q_pattern.findall(text)
    a_matches = a_pattern.findall(text)

    for q, a in zip(q_matches, a_matches):
        questions.append({
            "question": q.strip(),
            "answer": a.strip()
        })
    return questions

# متغیر فایل ورد (اسم دقیق فایل کنار کد)
docx_file = "ppl.docx"

# تنظیمات کاربر
st.sidebar.header("تنظیمات آزمون")
start_page = st.sidebar.number_input("📄 صفحه شروع (فقط عدد وارد کن، مثلاً 1)", min_value=1, value=1, step=1)
end_page = st.sidebar.number_input("📄 صفحه پایان (عدد >= شروع)", min_value=start_page, value=10, step=1)
random_order = st.sidebar.checkbox("🔀 سوالات به صورت تصادفی باشند")

if st.sidebar.button("▶️ شروع آزمون"):
    # کل متن رو بخون (چون ورد صفحه‌بندی نداره، گزینه صفحات فقط برای آینده‌س یا می‌تونی حذفش کنی)
    text = load_docx_text(docx_file)
    
    # استخراج سوال و جواب
    questions = parse_questions(text)

    if not questions:
        st.error("⛔ هیچ سوالی پیدا نشد! فرمت فایل یا متن را چک کن.")
    else:
        if random_order:
            random.shuffle(questions)
        st.session_state.score = 0
        st.session_state.index = 0
        st.session_state.questions = questions

# اگر آزمون شروع شده
if "questions" in st.session_state:
    questions = st.session_state.questions
    idx = st.session_state.index
    score = st.session_state.score

    if idx < len(questions):
        q = questions[idx]
        st.markdown(f"### سوال {idx+1}:\n{q['question']}")
        
        # گزینه‌های A تا D رو از متن سوال استخراج کنیم (خط به خط)
        options_pattern = re.compile(r"([A-D])\.\s*(.+)")
        opts = options_pattern.findall(q['question'])
        options_dict = {opt[0]: opt[1] for opt in opts}
        
        choice = st.radio("گزینه‌ی شما:", list(options_dict.keys()) if options_dict else ["A", "B", "C", "D"])
        
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
