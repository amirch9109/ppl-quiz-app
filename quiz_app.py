
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

# ---------- تابع استخراج متن ----------
def extract_text_from_pdf(file, start, end):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for i in range(start - 1, end):
        text += doc[i].get_text()
    return text

# ---------- تابع تبدیل به سوال ----------
def parse_questions(text):
    questions = []
    q_pattern = re.compile(r"(\d+\..*?)(?=Answer \([A-D]\) is correct)", re.DOTALL)
    a_pattern = re.compile(r"Answer \(([A-D])\) is correct")
    q_matches = q_pattern.findall(text)
    a_matches = a_pattern.findall(text)
    for q, a in zip(q_matches, a_matches):
        questions.append({"question": q.strip(), "answer": a.strip()})
    return questions
