from __future__ import annotations

import json

import streamlit as st

from src.models import ChatTurn
from src.service import SupportService

st.set_page_config(page_title="Lumina Support AI", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700&display=swap');
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
h1,h2,h3 { font-family:'Manrope',sans-serif; letter-spacing:-.025em; }
.stApp { background:radial-gradient(circle at 85% 5%,#e9e7ff 0,transparent 28%),#f7f8fc; }
[data-testid="stSidebar"] { background:#111827; color:#f8fafc; }
[data-testid="stSidebar"] * { color:#e5e7eb; }
.hero { padding:.2rem 0 1.2rem; }
.eyebrow { color:#6c63ff;font-weight:700;text-transform:uppercase;letter-spacing:.13em;font-size:.72rem; }
.hero h1 { font-size:clamp(2rem,4vw,3.25rem);margin:.35rem 0;color:#121827; }
.hero p { max-width:720px;color:#64748b;font-size:1.05rem; }
.status-card { background:white;border:1px solid #e8eaf2;border-radius:16px;padding:1rem;box-shadow:0 10px 30px rgba(30,41,59,.05); }
.persona { display:inline-flex;padding:.3rem .65rem;border-radius:99px;background:#eeecff;color:#4f46e5;font-size:.8rem;font-weight:700; }
.escalated { background:#fff1f2;color:#be123c; }
[data-testid="stChatMessage"] { background:rgba(255,255,255,.82);border:1px solid #eaecf3;border-radius:18px;padding:.45rem 1rem;box-shadow:0 5px 20px rgba(15,23,42,.04); }
.source-card { border-left:3px solid #6c63ff;padding:.65rem .8rem;margin:.45rem 0;background:#fafaff;border-radius:0 10px 10px 0; }
.confidence { color:#64748b;font-size:.8rem; }
@media(max-width:640px){.hero h1{font-size:2rem}.block-container{padding:1.2rem .8rem 5rem}.status-card{padding:.75rem}}
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def get_service() -> SupportService:
    service = SupportService()
    service.ingest()
    return service


try:
    service = get_service()
except Exception as exc:
    st.error(f"The knowledge base could not be initialized: {exc}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.markdown("## ✦ Lumina")
    st.caption("Persona-adaptive customer care")
    # st.divider()
    st.markdown(f"**Runtime**  \n{service.mode}")
    st.markdown(f"**Knowledge chunks**  \n{service.rag.collection.count()}")
    st.markdown("**Grounding**  \nCitations + confidence gate")
    # st.divider()
    st.markdown("##### Try a scenario")
    examples = {
        "API authentication": "Our API returns 401. What Authorization header and token checks should I run?",
        "Nothing is loading": "I've cleared cookies twice and nothing works! I need this fixed now!",
        "Operational impact": "What is the operational impact of an outage, and what timeline should leadership expect?",
        "Billing escalation": "I have duplicate charges and demand an immediate refund!",
    }
    for label, value in examples.items():
        if st.button(
            label,
            use_container_width=True,
            type="primary",
            key=f"scenario_{label}"
        ):
            st.session_state.prefill = value
    if st.button("Clear conversation", use_container_width=True, type="primary", key="clear_conversation"):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

st.markdown("""<div class="hero"><div class="eyebrow">Grounded support, shaped for every customer</div><h1>Resolve the issue. Respect the person.</h1><p>Lumina identifies communication style, retrieves verified guidance, and adapts every answer - with a clean human handoff when judgment matters.</p></div>""", unsafe_allow_html=True)

if not st.session_state.messages:
    left, middle, right = st.columns(3)
    for col, title, copy in [(left,"01 · Understand","Persona and sentiment detection on every turn."),(middle,"02 · Ground","Relevant support guidance with source metadata."),(right,"03 · Safeguard","Configurable escalation and a structured handoff.")]:
        with col:
            st.markdown(f'<div class="status-card"><b>{title}</b><p style="color:#64748b;margin:.45rem 0 0">{copy}</p></div>', unsafe_allow_html=True)
    st.write("")

for item in st.session_state.messages:
    # with st.chat_message(item["role"], avatar="*" if item["role"] == "assistant" else None):
    with st.chat_message(item["role"]):
        
        st.markdown(item["content"])
        if item.get("result"):
            result = item["result"]
            badge = "persona escalated" if result["escalation"]["escalated"] else "persona"
            label = result["persona"]["persona"]
            st.markdown(f'<span class="{badge}">{label}</span> <span class="confidence">{result["persona"]["confidence"]:.0%} confidence</span>', unsafe_allow_html=True)
            with st.expander(f"Sources · {len(result['sources'])}"):
                for source in result["sources"]:
                    st.markdown(f'<div class="source-card"><b>{source["source"]}</b><br><span class="confidence">{source["section"]} · relevance {source["score"]:.0%}</span></div>', unsafe_allow_html=True)
            if result["escalation"]["escalated"]:
                st.warning("Escalated · " + "; ".join(result["escalation"]["reasons"]))
                with st.expander("Human handoff summary", expanded=True):
                    st.json(result["handoff"])
                    st.download_button("Download handoff JSON", json.dumps(result["handoff"], indent=2), "lumina-handoff.json", "application/json", key=f"download-{item['id']}")

prompt = st.chat_input("Describe what’s happening…")
if st.session_state.get("prefill"):
    prompt = st.session_state.pop("prefill")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Understanding the issue and checking verified guidance…"):
            try:
                result = service.respond(prompt, st.session_state.history)
                st.markdown(result.response)
                payload = result.to_dict()
                st.session_state.messages.append({"id": len(st.session_state.messages), "role": "assistant", "content": result.response, "result": payload})
                st.session_state.history.extend([ChatTurn("user", prompt, result.persona.persona.value), ChatTurn("assistant", result.response)])
                st.rerun()
            except ValueError as exc:
                st.warning(str(exc))
            except Exception as exc:
                st.error("I couldn’t complete that request. Please retry; if it continues, check the service configuration.")
                st.caption(str(exc))

