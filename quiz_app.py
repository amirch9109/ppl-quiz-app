import streamlit as st
import fitz  # PyMuPDF
import re

def load_questions_from_pdf_path(file_path, start_page, end_page):
    doc = fitz.open(file_path)
    questions = []

    for i in range(start_page - 1, end_page):
        text = doc.load_page(i).get_text()
        lines = text.split("\n")

        for j in range(len(lines)):
            line = lines[j].strip()

            if line.startswith("Answer (") and "is correct" in line:
                match = re.search(r"Answer \(([A-D])\)", line)
                if not match:
                    continue
                correct = match.group(1)

                options = {}
                question_lines = []

                # به بالا برمی‌گردیم تا گزینه‌ها و سوال رو پیدا کنیم
                for k in range(j - 1, max(j - 25, -1), -1):
                    l = lines[k].strip()
                    if re.match(r"^\([A-D]\)", l):
                        label = l[1]
                        option_text = l[3:].strip()
                        options[label] = option_text
                    elif len(options) > 0:
                        question_lines.insert(0, l)
                    elif l == "":
                        continue
                    else:
                        continue

                full_question = "\n".join(question_lines).strip()

                if full_question and len(options) >= 2:
                    questions.append({
                        "question": full_question,
                        "options": dict(sorted(options.items())),
                        "answer": correct
                    })

    doc.close()
    return questions

def main():
    st.title("اپلیکیشن آزمون (خواندن PDF کنار کد)")

    pdf_file_path = "ppl.pdf"  # نام فایل PDF کنار کد

    start_page = st.number_input("صفحه شروع", min_value=1, step=1)
    end_page = st.number_input("صفحه پایان", min_value=start_page, step=1)

    if st.button("شروع آزمون"):
        try:
            questions = load_questions_from_pdf_path(pdf_file_path, start_page, end_page)
        except Exception as e:
            st.error(f"خطا در خواندن فایل PDF: {e}")
            return

        if not questions:
            st.warning("در این بازه صفحه، سوالی پیدا نشد.")
            return

        st.success(f"تعداد سوالات یافت شده: {len(questions)}")

        if "current_q" not in st.session_state:
            st.session_state.current_q = 0

        def show_question(idx):
            q_data = questions[idx]
            st.markdown(f"**سوال {idx + 1}:** {q_data['question']}")
            choices = [f"{key}. {val}" for key, val in q_data["options"].items()]
            user_choice = st.radio("جواب خود را انتخاب کنید:", choices, key=f"q_{idx}")

            if st.button("ارسال جواب", key=f"submit_{idx}"):
                selected_label = user_choice[0]  # حرف اول گزینه مثل A
                if selected_label == q_data["answer"]:
                    st.success("جواب شما درست است! 🎉")
                else:
                    st.error(f"جواب شما اشتباه است! جواب درست: {q_data['answer']}")
                st.session_state.current_q += 1
                st.experimental_rerun()

        if st.session_state.current_q < len(questions):
            show_question(st.session_state.current_q)
        else:
            st.info("آزمون به پایان رسید. تبریک!")

if __name__ == "__main__":
    main()
