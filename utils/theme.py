import streamlit as st

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1200px; }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: #0e1426;
    border-right: 1px solid #1c2440;
}

/* ---------- Hero ---------- */
.hero {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #06b6d4 100%);
    border-radius: 20px; padding: 36px 40px; margin-bottom: 22px;
    box-shadow: 0 12px 40px rgba(79, 70, 229, 0.35);
}
.hero h1 { color: #fff; font-size: 2.3rem; font-weight: 800; margin: 0 0 6px 0; padding: 0; }
.hero p { color: rgba(255,255,255,0.92); margin: 0; font-size: 1.05rem; }
.chip {
    display: inline-block; background: rgba(255,255,255,0.18); color: #fff;
    padding: 5px 14px; border-radius: 999px; font-size: 0.82rem; font-weight: 600;
    margin: 16px 8px 0 0;
}

/* ---------- Stepper ---------- */
.stepper { display: flex; gap: 10px; margin-bottom: 26px; flex-wrap: wrap; }
.step {
    flex: 1; min-width: 150px; padding: 12px 16px; border-radius: 12px;
    background: #131a2e; border: 1px solid #232c4a; color: #94a3b8;
    font-weight: 600; font-size: 0.9rem;
}
.step.done { border-color: #10b981; color: #34d399; background: rgba(16,185,129,0.08); }
.step.active { border-color: #6366f1; color: #fff; background: rgba(99,102,241,0.2); }

/* ---------- Section header ---------- */
.sec { display: flex; align-items: center; gap: 12px; margin: 8px 0 14px 0; }
.sec-num {
    width: 34px; height: 34px; border-radius: 10px; display: flex;
    align-items: center; justify-content: center; font-weight: 800; color: #fff;
    background: linear-gradient(135deg, #6366f1, #06b6d4);
}
.sec-title { font-size: 1.3rem; font-weight: 700; color: #f1f5f9; }
.sec-desc { color: #94a3b8; font-size: 0.9rem; margin-top: 2px; }

/* ---------- Stat cards ---------- */
.stat-card {
    background: #131a2e; border: 1px solid #232c4a; border-radius: 14px;
    padding: 18px; text-align: center;
}
.stat-card h2 {
    margin: 0; font-size: 1.8rem; font-weight: 800;
    background: linear-gradient(90deg, #818cf8, #22d3ee);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-card p { margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem; }

/* ---------- Buttons ---------- */
div.stButton > button, div.stDownloadButton > button {
    background: linear-gradient(90deg, #4f46e5, #06b6d4);
    color: #fff; border: none; border-radius: 12px;
    padding: 0.65rem 1.5rem; font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    transform: translateY(-2px); color: #fff;
    box-shadow: 0 8px 22px rgba(99, 102, 241, 0.45);
}
div.stButton > button:disabled { opacity: 0.4; transform: none; box-shadow: none; }

/* ---------- Tabs ---------- */
button[data-baseweb="tab"] { font-weight: 600; font-size: 1rem; padding: 10px 18px; }

/* ---------- Expander ---------- */
div[data-testid="stExpander"] {
    background: #131a2e; border: 1px solid #232c4a; border-radius: 12px;
}

/* ---------- Inputs ---------- */
.stTextInput input, .stNumberInput input { border-radius: 10px; }
div[data-testid="stFileUploader"] section {
    border: 2px dashed #3b4670; border-radius: 16px; background: #131a2e;
}

/* ---------- Flashcard ---------- */
.flashcard {
    border-radius: 20px; padding: 56px 36px; text-align: center;
    font-size: 1.45rem; font-weight: 600; min-height: 220px;
    display: flex; align-items: center; justify-content: center;
    color: #fff; margin: 14px 0; box-shadow: 0 14px 40px rgba(0,0,0,0.35);
}
.fc-front { background: linear-gradient(135deg, #4f46e5, #7c3aed); }
.fc-back  { background: linear-gradient(135deg, #0891b2, #10b981); }

.footer-note { text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 40px; }
"""


def inject_css():
    st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)


def hero(title: str, subtitle: str, chips: list):
    chips_html = "".join(f'<span class="chip">{c}</span>' for c in chips)
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p>{chips_html}</div>',
        unsafe_allow_html=True,
    )


def stepper_html(labels: list, current: int) -> str:
    """current = kitne steps complete hue (0 se len(labels))."""
    parts = []
    for i, label in enumerate(labels):
        if i < current:
            cls, icon = "done", "✓"
        elif i == current:
            cls, icon = "active", str(i + 1)
        else:
            cls, icon = "", str(i + 1)
        parts.append(f'<div class="step {cls}">{icon}&nbsp;&nbsp;{label}</div>')
    return '<div class="stepper">' + "".join(parts) + "</div>"


def section(num: int, title: str, desc: str = ""):
    desc_html = f'<div class="sec-desc">{desc}</div>' if desc else ""
    st.markdown(
        f'<div class="sec"><div class="sec-num">{num}</div>'
        f'<div><div class="sec-title">{title}</div>{desc_html}</div></div>',
        unsafe_allow_html=True,
    )


def stat_card(col, value, label: str):
    col.markdown(
        f'<div class="stat-card"><h2>{value}</h2><p>{label}</p></div>',
        unsafe_allow_html=True,
    )