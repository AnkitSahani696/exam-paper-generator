import json
import os
import re

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def _get_api_key():
    key = os.getenv("GROQ_API_KEY")          # laptop par .env se
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]    # online par Secrets se
    except Exception:
        return None


client = Groq(api_key=_get_api_key())
MODEL = "openai/gpt-oss-120b"

ANSWER_GUIDE = {
    1: "ek line ka chhota answer (definition ya one-word/one-line)",
    2: "2 se 3 lines ka answer, seedha point par",
    4: "lagbhag 100 se 150 words, 3 se 4 points me explain karo",
    8: "lagbhag 300 se 400 words, heading, points aur example ke saath detailed answer",
}


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    return json.loads(raw)


def _ask(prompt: str, temperature: float = 0.4, max_tokens: int = 6000) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return _parse_json(response.choices[0].message.content)


def generate_paper(text: str, subject: str, counts: dict) -> list[dict]:
    wanted = "\n".join(
        f"- {n} questions of {marks} mark(s): answer = {ANSWER_GUIDE[marks]}"
        for marks, n in counts.items()
        if n > 0
    )
    prompt = f"""You are an experienced university paper-setter for the subject: {subject}.

Using ONLY the study material below, create an exam paper.

Questions required:
{wanted}

Rules:
- Questions must come from the material, no outside topics.
- Questions must not repeat each other.
- Difficulty must match the marks (higher marks = deeper question).
- Write questions and answers in simple English.
- Return ONLY valid JSON, no extra text, no markdown fences.

JSON format:
{{
  "paper": [
    {{"marks": 1, "question": "...", "answer": "..."}}
  ]
}}

STUDY MATERIAL:
\"\"\"
{text}
\"\"\"
"""
    data = _ask(prompt, max_tokens=6000)
    return data["paper"]


def generate_flashcards(text: str, subject: str, count: int = 10) -> list[dict]:
    prompt = f"""You are a study assistant for the subject: {subject}.

Using ONLY the study material below, create {count} flashcards for quick revision.

Rules:
- "front" = a short question or a key term.
- "back" = a short, clear answer (maximum 2 sentences).
- Cover different topics, do not repeat.
- Simple English.
- Return ONLY valid JSON, no extra text, no markdown fences.

JSON format:
{{
  "flashcards": [
    {{"front": "...", "back": "..."}}
  ]
}}

STUDY MATERIAL:
\"\"\"
{text}
\"\"\"
"""
    data = _ask(prompt, max_tokens=4000)
    return data["flashcards"]


def generate_quiz(text: str, subject: str, count: int = 10) -> list[dict]:
    prompt = f"""You are a quiz maker for the subject: {subject}.

Using ONLY the study material below, create {count} multiple choice questions (MCQ).

Rules:
- Each question has exactly 4 options.
- Only one option is correct.
- "answer_index" is the position of the correct option (0, 1, 2 or 3).
- Spread the correct answers across positions, do not always use the same index.
- Wrong options must look believable.
- "explanation" = 1 or 2 sentences on why the answer is correct.
- Simple English.
- Return ONLY valid JSON, no extra text, no markdown fences.

JSON format:
{{
  "quiz": [
    {{"question": "...", "options": ["...", "...", "...", "..."],
      "answer_index": 0, "explanation": "..."}}
  ]
}}

STUDY MATERIAL:
\"\"\"
{text}
\"\"\"
"""
    data = _ask(prompt, temperature=0.5, max_tokens=5000)

    clean = []
    for q in data.get("quiz", []):
        opts = q.get("options", [])
        idx = q.get("answer_index")
        if len(opts) == 4 and isinstance(idx, int) and 0 <= idx <= 3:
            clean.append(q)
    return clean