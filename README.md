# 🎓 Smart Exam Paper Generator

Student apni subject ki PDF upload kare aur turant paaye:
- 📝 Marks-wise question paper (1 / 2 / 4 / 8 marks) with answers
- 🃏 Flashcards for quick revision
- 🧠 MCQ quiz with score and explanations
- ⬇️ Question paper aur answer key PDF download

## Tech Stack
Python, Streamlit, pdfplumber, fpdf2, Groq API (LLM)

## Project Structure
```
exam-paper-generator/
├── app.py
├── requirements.txt
├── utils/        # pdf_reader, chunker, pdf_export
└── services/     # ai_service (LLM calls)
```

## Setup
```bash
pip install -r requirements.txt
```
`.env` file banao:
```
GROQ_API_KEY=your_key_here
```
Run:
```bash
streamlit run app.py
```

## How it works
PDF upload → text extraction → chunking → LLM prompt → JSON → Streamlit UI