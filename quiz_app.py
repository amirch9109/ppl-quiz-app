import streamlit as st
import fitz
import random

# --- تنظیمات صفحه ---
st.set_page_config(page_title="آزمون PPL", layout="centered")
st.title("🧪 آزمون تمرینی PPL")

# --- باز کردن فایل PDF ---
try:
    doc = fitz.open("ppl.pdf")
except:
    st.error("❌ فایل ppl.pdf یافت نشد.")
    st.stop()

st.success("✅ فایل آزمون با موفقیت بارگذاری شد.")

# --- انتخاب صفحه ---
col1, col2 = st.columns(2)
start_page = col1.number_input("📄 صفحه شروع", min_value=0, max_value=len(doc)-1, value=0)
end_page = col2.number_input("📄 صفحه پایان", min_value=0, max_value=len(doc)-1, value=min(5, len(doc)-1))

# --- انتخاب نوع سوال ---
order_type = st.radio("🔄 ترتیب نمایش سوالات", ["نوبتی", "تصادفی"])

# --- استخراج سوالات ---
questions = []
for i in range(start_page, end_page + 1):
    text = doc.load_page(i).get_text()
    blocks = text.split("\n")
    for j in range(len(blocks)):
        if blocks[j].strip().startswith("Answer ("):
            question = blocks[j - 1].strip()  # سوال
            correct_answer = blocks[j].strip().split("Answer (")[1][0]  # حرف پاسخ
            questions.append((question, correct_answer))

# --- تنظیم ترتیب سوالات ---
if order_type == "تصادفی":
    random.shuffle(questions)

# --- سیستم سوال‌پرس ---
if questions:
    st.markdown("---")
    st.subheader("🎯 پاسخ به سوال")

    q_idx = st.number_input("شماره سوال", 1, len(questions), step=1) - 1
    question, correct = questions[q_idx]

    st.write(f"**سوال:** {question}")
    user_answer = st.radio("پاسخ شما:", ["A", "B", "C", "D"], horizontal=True)

    if st.button("بررسی پاسخ"):
        if user_answer.upper() == correct.upper():
            st.success("✅ درست جواب دادی!")
        else:
            st.error(f"❌ غلطه. پاسخ صحیح: {correct}")
else:
    st.warning("توی این بازه صفحه سوالی پیدا نشد.")
