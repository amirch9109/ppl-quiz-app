import streamlit as st
import fitz  # PyMuPDF
import re

def load_questions_from_pdf(file_path, start_page, end_page):
    doc = fitz.open(file_path)
    questions = []

    for page_num in range(start_page - 1, end_page):
        text = doc.load_page(page_num).get_text()
        lines = text.split('\n')

        # پیدا کردن سوالات و جواب‌ها
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("Answer (") and "is correct" in line:
                match = re.search(r"Answer \(([A-D])\) is correct", line)
                if not match:
                    continue
                correct_answer = match.group(1)

                # حالا گزینه‌ها و سوال رو پیدا می‌کنیم؛
                options = {}
                question_lines = []

                # برمیگردیم بالاتر از خط جواب تا سوال و گزینه ها رو پیدا کنیم
                for j in range(i - 1, max(i - 30, -1), -1):
                    current_line = lines[j].strip()

                    # اگر گزینه هست
                    if re.match(r"^\([A-D]\)", current_line):
                        label = current_line[1]
                        option_text = current_line[3:].strip()
                        options[label] = option_text
                    # اگر گزینه ها شروع شده‌اند، بقیه خط ها سوالند
                    elif len(options) > 0:
                        question_lines.insert(0, current_line)
                    # خطوط خالی را رد می‌کنیم
                    elif current_line == "":
                        continue
                    else:
                        continue

                question_text = "\n".join(question_lines).strip()
                if question_text and len(options) >= 2:
                    questions.append({
                        "question": question_text,
                        "options": dict(sorted(options.items())),
                        "answer": correct_answer
                    })

    doc.close()
    return questions

def main():
    st.title("اپلیکیشن آزمون از PDF")

    pdf_file_path = "ppl.pdf"

    start_page = st.number_input("صفحه شروع", min_value=1, step=1)
    end_page = st.number_input("صفحه پایان", min_value=start_page, step=1)

    if st.button("شروع آزمون"):
        try:
            questions = load_questions_from_pdf(pdf_file_path, start_page, end_page)
        except Exception as e:
            st.error(f"خطا در خواندن فایل PDF: {e}")
            return

        if not questions:
            st.warning("در این بازه صفحه سوالی پیدا نشد.")
            return

        st.success(f"تعداد سوالات یافت شده: {len(questions)}")

        if "current_q" not in st.session_state:
            st.session_state.current_q = 0

        def show_question(idx):
            q = questions[idx]
            st.markdown(f"**سوال {idx + 1}:** {q['question']}")
            choices = [f"{key}. {val}" for key, val in q["options"].items()]
            user_choice = st.radio("جواب خود را انتخاب کنید:", choices, key=f"q_{idx}")

            if st.button("ارسال جواب", key=f"submit_{idx}"):
                selected = user_choice[0]
                if selected == q["answer"]:
                    st.success("جواب شما درست است! 🎉")
                else:
                    st.error(f"جواب شما اشتباه است! جواب درست: {q['answer']}")
                st.session_state.current_q += 1
                st.experimental_rerun()

        if st.session_state.current_q < len(questions):
            show_question(st.session_state.current_q)
        else:
            st.info("آزمون تمام شد. تبریک!")

if __name__ == "__main__":
    main()
