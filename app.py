import streamlit as st
from utils.pdf_reader import get_page_count, extract_text
from utils.chunker import split_into_chunks, chunk_stats
from utils.pdf_export import build_pdf
from utils.theme import inject_css, hero, section, stat_card, stepper_html
from services.ai_service import generate_paper, generate_flashcards, generate_quiz

# ---------- Page config + theme ----------
st.set_page_config(
    page_title="Smart Exam Paper Generator",
    page_icon="🎓",
    layout="wide",
)
inject_css()

# ---------- Session state ----------
defaults = {
    "pdf_text": "",
    "chunks": [],
    "paper": [],
    "cards": [],
    "card_idx": 0,
    "card_flipped": False,
    "quiz": [],
    "quiz_version": 0,
    "quiz_submitted": False,
    "quiz_answers": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🎓 Exam Generator")
    st.caption("AI powered study companion")
    st.divider()
    st.markdown("**Kaise use karein**")
    st.markdown(
        "1. 📄 PDF upload karo\n"
        "2. 📑 Page range chuno\n"
        "3. ⚙️ Subject bharo\n"
        "4. 📝 Paper / 🃏 Flashcards / 🧠 Quiz banao"
    )
    st.divider()
    st.caption("Built with Python, Streamlit & AI")

# ---------- Hero ----------
hero(
    "🎓 Smart Exam Paper Generator",
    "Notes upload karo, exam-ready paper, flashcards aur quiz paao, ek click me.",
    ["📝 Marks-wise Paper", "🃏 Flashcards", "🧠 MCQ Quiz", "⬇️ PDF Download"],
)
step_box = st.empty()   # stepper baad me yahan bharenge

# ---------- Step 1 & 2: Upload ----------
section(1, "Subject PDF upload karo", "Text-wali PDF use karo (scanned image nahi)")
uploaded = st.file_uploader("PDF file chuno", type=["pdf"], label_visibility="collapsed")

if uploaded:
    total_pages = get_page_count(uploaded)

    section(2, "Page range chuno", f"Is PDF me total {total_pages} pages hain")
    col1, col2 = st.columns(2)
    start = col1.number_input("Start page", min_value=1, max_value=total_pages, value=1)
    end = col2.number_input("End page", min_value=1, max_value=total_pages,
                            value=min(total_pages, 10))

    if st.button("📥 Text nikalo"):
        if start > end:
            st.error("Start page, End page se chhota hona chahiye.")
        else:
            with st.spinner("PDF padh raha hoon..."):
                st.session_state.pdf_text = extract_text(uploaded, int(start), int(end))
                st.session_state.chunks = split_into_chunks(st.session_state.pdf_text)
                st.session_state.paper = []
                st.session_state.cards = []
                st.session_state.card_idx = 0
                st.session_state.card_flipped = False
                st.session_state.quiz = []
                st.session_state.quiz_submitted = False
                st.session_state.quiz_answers = []

text = st.session_state.pdf_text
chunks = st.session_state.chunks

if text:
    st.success("Text successfully nikal gaya! ✅")

    # ---------- Step 3: Settings ----------
    st.divider()
    section(3, "Subject aur settings", "Ye settings paper, flashcards aur quiz teeno me use hongi")

    s1, s2 = st.columns([2, 1])
    subject = s1.text_input("Subject ka naam", placeholder="Jaise: DBMS, Python, Java",
                            key="subject")

    max_use = len(chunks)
    if max_use > 1:
        use_chunks = s2.slider(
            "Kitne chunks use karne hain?",
            min_value=1,
            max_value=max_use,
            value=min(3, max_use),
            help="Zyada chunks = zyada topics, lekin slow aur zyada token use",
            key="use_chunks",
        )
    else:
        use_chunks = 1
        s2.caption("Is PDF me sirf 1 chunk hai, wahi use hoga.")

    material = "\n\n".join(chunks[:use_chunks])

    # ---------- Step 4: Tabs ----------
    st.divider()
    section(4, "Generate karo", "Jo chahiye uska tab chuno")
    tab_paper, tab_cards, tab_quiz, tab_info = st.tabs(
        ["📝 Paper", "🃏 Flashcards", "🧠 Quiz", "📊 Text info"]
    )

    # ===================== TAB 1: PAPER =====================
    with tab_paper:
        st.markdown("**Kitne questions chahiye?**")
        q1, q2, q3, q4 = st.columns(4)
        n1 = q1.number_input("1 Mark", min_value=0, max_value=20, value=5, key="n1")
        n2 = q2.number_input("2 Marks", min_value=0, max_value=20, value=5, key="n2")
        n4 = q3.number_input("4 Marks", min_value=0, max_value=10, value=3, key="n4")
        n8 = q4.number_input("8 Marks", min_value=0, max_value=5, value=2, key="n8")

        total_marks = n1 * 1 + n2 * 2 + n4 * 4 + n8 * 8
        st.info(f"Total marks: **{total_marks}**")

        if st.button("⚡ Paper generate karo", key="btn_paper"):
            if not subject.strip():
                st.error("Pehle subject ka naam likho.")
            elif total_marks == 0:
                st.error("Kam se kam ek question chahiye.")
            else:
                counts = {1: int(n1), 2: int(n2), 4: int(n4), 8: int(n8)}
                try:
                    with st.spinner("AI paper bana raha hai... (30 se 60 second lag sakte hain)"):
                        st.session_state.paper = generate_paper(material, subject, counts)
                    st.success("Paper ready! 🎉")
                except Exception as e:
                    st.error(f"Error aaya: {e}")

        paper = st.session_state.paper
        if paper:
            st.markdown("### 📄 Generated Paper")
            for marks in (1, 2, 4, 8):
                items = [q for q in paper if str(q.get("marks")) == str(marks)]
                if not items:
                    continue
                st.markdown(f"#### Section: {marks} Mark Questions")
                for i, q in enumerate(items, 1):
                    with st.expander(f"Q{i}. {q['question']}  ({marks} marks)"):
                        st.markdown("**Answer:**")
                        st.write(q["answer"])

            st.divider()
            st.markdown("#### ⬇️ Download karo")
            d1, d2 = st.columns(2)
            d1.download_button(
                "📄 Question Paper (PDF)",
                data=build_pdf(subject or "Exam", paper, with_answers=False),
                file_name=f"{subject or 'exam'}_question_paper.pdf",
                mime="application/pdf",
                key="dl_paper",
            )
            d2.download_button(
                "✅ Paper + Answer Key (PDF)",
                data=build_pdf(subject or "Exam", paper, with_answers=True),
                file_name=f"{subject or 'exam'}_answer_key.pdf",
                mime="application/pdf",
                key="dl_answers",
            )

    # ===================== TAB 2: FLASHCARDS =====================
    with tab_cards:
        fc_count = st.slider("Kitne flashcards chahiye?", 5, 20, 10, key="fc_count")

        if st.button("🃏 Flashcards banao", key="btn_flashcards"):
            if not subject.strip():
                st.error("Pehle subject ka naam likho.")
            else:
                try:
                    with st.spinner("Flashcards ban rahe hain..."):
                        st.session_state.cards = generate_flashcards(material, subject, fc_count)
                        st.session_state.card_idx = 0
                        st.session_state.card_flipped = False
                    st.success("Flashcards ready! 🎉")
                except Exception as e:
                    st.error(f"Error aaya: {e}")

        cards = st.session_state.cards
        if cards:
            idx = st.session_state.card_idx
            card = cards[idx]
            flipped = st.session_state.card_flipped

            st.caption(f"Card {idx + 1} / {len(cards)}  •  {'Answer' if flipped else 'Question'}")
            st.progress((idx + 1) / len(cards))
            css_class = "fc-back" if flipped else "fc-front"
            content = card["back"] if flipped else card["front"]
            st.markdown(f'<div class="flashcard {css_class}">{content}</div>',
                        unsafe_allow_html=True)

            b1, b2, b3 = st.columns(3)
            if b1.button("⬅️ Previous", disabled=(idx == 0), key="fc_prev"):
                st.session_state.card_idx -= 1
                st.session_state.card_flipped = False
                st.rerun()
            if b2.button("🔄 Flip", key="fc_flip"):
                st.session_state.card_flipped = not flipped
                st.rerun()
            if b3.button("Next ➡️", disabled=(idx == len(cards) - 1), key="fc_next"):
                st.session_state.card_idx += 1
                st.session_state.card_flipped = False
                st.rerun()

    # ===================== TAB 3: QUIZ =====================
    with tab_quiz:
        qz_count = st.slider("Kitne MCQ chahiye?", 5, 20, 10, key="qz_count")

        if st.button("🧠 Quiz banao", key="btn_quiz"):
            if not subject.strip():
                st.error("Pehle subject ka naam likho.")
            else:
                try:
                    with st.spinner("Quiz ban raha hai..."):
                        st.session_state.quiz = generate_quiz(material, subject, qz_count)
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_answers = []
                        st.session_state.quiz_version += 1
                    if st.session_state.quiz:
                        st.success("Quiz ready! 🎉")
                    else:
                        st.error("Quiz nahi bana, dobara try karo.")
                except Exception as e:
                    st.error(f"Error aaya: {e}")

        quiz = st.session_state.quiz
        if quiz:
            ver = st.session_state.quiz_version

            with st.form(f"quiz_form_{ver}"):
                picked = []
                for i, q in enumerate(quiz):
                    st.markdown(f"**Q{i + 1}. {q['question']}**")
                    choice = st.radio(
                        "Option chuno",
                        q["options"],
                        index=None,
                        key=f"qz_{ver}_{i}",
                        label_visibility="collapsed",
                    )
                    picked.append(choice)
                submitted = st.form_submit_button("✅ Submit quiz")

            if submitted:
                st.session_state.quiz_submitted = True
                st.session_state.quiz_answers = picked

            if st.session_state.quiz_submitted:
                answers = st.session_state.quiz_answers
                score = sum(
                    1 for q, a in zip(quiz, answers)
                    if a == q["options"][q["answer_index"]]
                )
                total = len(quiz)
                percent = int(score * 100 / total)

                st.markdown("### 📊 Result")
                r1, r2, r3 = st.columns(3)
                stat_card(r1, f"{score}/{total}", "Score")
                stat_card(r2, f"{percent}%", "Percentage")
                stat_card(r3, total - score, "Galat / Chhoote")
                st.write("")

                if percent >= 80:
                    st.success("Shandaar! Tumhari taiyari bahut achhi hai 🔥")
                elif percent >= 50:
                    st.info("Achha hai, thodi aur revision karo 👍")
                else:
                    st.warning("Flashcards dobara dekho aur phir try karo 💪")

                st.markdown("### 🔍 Review")
                for i, (q, a) in enumerate(zip(quiz, answers), 1):
                    correct = q["options"][q["answer_index"]]
                    if a == correct:
                        st.success(f"Q{i}. {q['question']}\n\n✅ Sahi: **{correct}**")
                    else:
                        your = a if a else "Koi option nahi chuna"
                        st.error(
                            f"Q{i}. {q['question']}\n\n"
                            f"❌ Tumhara answer: {your}\n\n"
                            f"✅ Sahi answer: **{correct}**"
                        )
                    st.caption(f"💡 {q.get('explanation', '')}")

                if st.button("🔁 Naya quiz do", key="btn_retry"):
                    st.session_state.quiz = []
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers = []
                    st.rerun()

    # ===================== TAB 4: TEXT INFO =====================
    with tab_info:
        words = len(text.split())
        stats = chunk_stats(chunks)

        i1, i2, i3 = st.columns(3)
        stat_card(i1, f"{len(text):,}", "Characters")
        stat_card(i2, f"{words:,}", "Words")
        stat_card(i3, stats["count"], "Chunks")
        st.write("")

        with st.expander("👀 Extracted text preview"):
            st.text(text[:3000] + ("..." if len(text) > 3000 else ""))

        with st.expander("🔍 Chunks dekho"):
            for i, c in enumerate(chunks, 1):
                st.markdown(f"**Chunk {i}** ({len(c):,} chars)")
                st.text(c[:500] + ("..." if len(c) > 500 else ""))
                st.divider()

elif uploaded:
    st.info("Page range chun ke **Text nikalo** dabao.")

# ---------- Stepper (sabse last me, taaki latest state dikhe) ----------
if not uploaded:
    done = 0
elif not text:
    done = 1
elif not (st.session_state.paper or st.session_state.cards or st.session_state.quiz):
    done = 3
else:
    done = 4

step_box.markdown(
    stepper_html(["Upload PDF", "Text nikalo", "Settings", "Generate"], done),
    unsafe_allow_html=True,
)

st.markdown('<div class="footer-note">Made with ❤️ using Python, Streamlit & AI</div>',
            unsafe_allow_html=True)