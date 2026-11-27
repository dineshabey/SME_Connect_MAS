"""Shared presentation components for SMEConnect AI's Streamlit dashboard.

CSS/navigation only. All simulation decisions remain in smeconnect/.
"""
import html

import streamlit as st


PAGES = (
    "🏠 Overview",
    "🏬 Marketplace",
    "🤝 Supplier Competition",
    "🚚 Order & Delivery",
    "📈 Market Adaptation",
    "🧪 Experiment Analytics",
    "💬 Guided Negotiation",
    "🏪 Seller Decision Lab",
    "🛒 Retailer Decision Lab",
)

PAGE_METADATA = {
    PAGES[0]: ("Academic control center", "Meet the agents, understand the system and launch a real scenario."),
    PAGES[1]: ("Seller marketplace", "Browse public synthetic listings and negotiate with available sellers."),
    PAGES[2]: ("Supplier competition", "Compare two independent seller negotiations and the retailer's choice."),
    PAGES[3]: ("Order & delivery", "Coordinate a simulated reservation with budget, stock and delivery checks."),
    PAGES[4]: ("Market adaptation", "Compare agent decisions before and after a controlled market event."),
    PAGES[5]: ("Experiment analytics", "Run reproducible paired simulations and export measured evidence."),
    PAGES[6]: ("Guided negotiation", "Replay actual proposals and responses one step at a time."),
    PAGES[7]: ("Seller decision lab", "Evaluate a single offer using an independent seller policy."),
    PAGES[8]: ("Retailer decision lab", "Inspect affordability and utility constraints on a retailer's offer."),
}

CSS = """
<style>
/* Minimal modern dashboard shell: high contrast, wide and readable. */
:root { --smc-cyan:#43c8d0; --smc-blue:#5c9be8; --smc-muted:#a9bacb; }
.block-container {
    max-width: 100% !important;
    width: 100% !important;
    padding: 1.35rem clamp(1.1rem,2.4vw,3rem) 3rem !important;
}
.stApp {
    background: radial-gradient(circle at 80% 0%,rgba(31,80,111,.13),transparent 35%), #0e141d;
}
section[data-testid="stSidebar"] {
    background: #111f2c;
    border-right:1px solid #2b4257;
    min-width: 275px;
}
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-size:18px !important; }
section[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: .52rem .6rem;
    border-radius: .65rem;
    margin-bottom: .13rem;
}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background:rgba(78,160,186,.11);
}
section[data-testid="stSidebar"] [role="radiogroup"] label p {font-size:17px !important;}
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li {font-size:19px;line-height:1.6;}
.stApp h1 {font-size:clamp(2rem,2.7vw,2.7rem);line-height:1.16;}
.stApp h2 {font-size:clamp(1.7rem,2.1vw,2.2rem);line-height:1.2;}
.stApp h3 {font-size:clamp(1.45rem,1.8vw,1.8rem);line-height:1.3;}
.stApp [data-testid="stCaptionContainer"] p {font-size:16px !important;line-height:1.55;}
.stApp [data-testid="stMetricLabel"] p {font-size:17px !important;font-weight:650;}
.stApp [data-testid="stMetricValue"] {font-size:clamp(1.8rem,2.5vw,2.5rem) !important;}
.stApp [data-testid="stWidgetLabel"] p {font-size:18px !important;font-weight:650;}
.stApp [data-testid="stBaseButton-primary"],
.stApp [data-testid="stBaseButton-secondary"] {
    min-height:48px;
    border-radius:11px;
    font-size:18px;
}
.stApp button p {font-size:17px !important;}
.stApp [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px;
}
.stApp [data-testid="stDataFrame"] {font-size:16px;}
.stApp [data-testid="stExpander"] {border-radius:12px;}
.stApp [data-baseweb="input"] input {font-size:18px;}
.stApp [data-baseweb="select"] {font-size:18px;}
.smc-header {
    padding:25px clamp(22px,3vw,44px);
    background:linear-gradient(115deg,#142a40 0%,#15475b 60%,#145c5c 100%);
    border:1px solid #387487;
    border-radius:19px;
    margin-bottom:22px;
}
.smc-overline {
    color:#a3e5e5;
    letter-spacing:.13em;
    font-size:13px;
    font-weight:750;
    text-transform:uppercase;
    margin-bottom:8px;
}
.smc-header h1 {
    margin:0 0 8px !important;
    color:#fff;
    font-size:clamp(29px,2.9vw,45px) !important;
}
.smc-header p {color:#d4e5ef;font-size:18px !important;margin:0;}
.smc-brand {
    font-size:27px;
    font-weight:800;
    letter-spacing:-.03em;
    color:#f0f6fb;
    margin-bottom:4px;
}
.smc-brand span {color:#69e4cf;}
.smc-sidebar-caption {color:#a9c1ce;font-size:14px;line-height:1.5;}
.smc-trail {font-size:16px;color:#a9c1ce;margin:4px 0 19px;}
.smc-trail b {color:#f4faff;}
.smc-card-head {font-size:20px;font-weight:750;line-height:1.3;}
.smc-card-muted {color:#b4c5d3;font-size:16px;line-height:1.45;}
.smc-tag {color:#8adccf;font-size:14px;font-weight:750;letter-spacing:.05em;}
.smc-step {border-left:3px solid #4cbfc0;padding:12px 16px;margin:8px 0;background:rgba(60,120,155,.10);border-radius:0 10px 10px 0;}
.smc-step strong{font-size:18px;}
/* Legacy negotiation cards remain functional but more readable. */
.guide {padding:16px 20px;border:1px solid #3b5b70;border-radius:12px;background:#173044;}
.guide b{color:#b8f2f2;}
.diagram {background:linear-gradient(135deg,#17283c,#1b3644);color:#f2f8fc;padding:22px;border:1px solid #375c72;border-radius:17px;}
.network {display:grid;grid-template-columns:1fr 1.35fr 1fr;align-items:center;gap:13px;}
.actor {background:#1d4565;border:1px solid #4589b1;padding:20px 10px;border-radius:12px;text-align:center;min-height:135px;}
.actor.seller{background:#21513e;border-color:#3aa784;}
.actor .emoji{font-size:32px;margin-bottom:6px;}
.actor strong{font-size:19px;display:block;}
.actor small{color:#d8e8ed;font-size:15px;display:block;margin-top:6px;}
.signal {text-align:center;min-height:116px;padding-top:13px;}
.signal b{display:inline-block;background:#14597a;border:1px solid #45afd0;padding:7px 13px;border-radius:24px;font-size:16px;}
.signal small{display:block;margin:6px 0;color:#d6e5ed;font-size:15px;}
.rail {height:5px;background:linear-gradient(90deg,#21c59d,#55a9f1);position:relative;margin:19px 8px 10px;border-radius:10px;}
.dot {position:absolute;top:-8px;height:20px;width:20px;border-radius:50%;background:#fff;border:3px solid #38bdf8;box-shadow:0 0 14px #50c2fe;}
.dot.forward{animation:forward 1.2s ease-in-out infinite;}
.dot.backward{animation:backward 1.2s ease-in-out infinite;}
@keyframes forward{0%{left:0}100%{left:calc(100% - 20px)}}
@keyframes backward{0%{left:calc(100% - 20px)}100%{left:0}}
.explainer{background:#0f3040;border-left:4px solid #37b4c5;border-radius:7px;padding:14px;margin-top:17px;line-height:1.7;}
.steps{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px;}
.step{background:#2d4256;border:1px solid #46617b;padding:9px 13px;border-radius:7px;font-size:15px;}
.step.current{background:#126f7c;border-color:#3ad0d0;font-weight:700;}
@media(max-width:760px){
  .block-container{padding:.9rem .75rem 2rem!important;}
  .smc-header{padding:18px;}
  .smc-header p{font-size:16px!important;}
  .stApp [data-testid="stMarkdownContainer"] p{font-size:17px;}
  .network{grid-template-columns:1fr;}
}
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def navigate_to(page: str):
    """Run as an on_click callback before Streamlit re-instantiates its radio."""
    if page not in PAGES:
        raise ValueError("Unknown navigation destination.")
    st.session_state["nav_page"] = page


def show_sidebar() -> str:
    with st.sidebar:
        st.markdown('<div class="smc-brand">◈ SME<span>Connect</span> AI</div>', unsafe_allow_html=True)
        st.markdown('<p class="smc-sidebar-caption">MULTI-AGENT MARKETPLACE<br>ACADEMIC SIMULATION</p>', unsafe_allow_html=True)
        st.divider()
        page = st.radio("WORKSPACE", PAGES, label_visibility="collapsed", key="nav_page")
        st.divider()
        st.caption("MSc IT6415 · Software Agents & Swarm Intelligence")
        st.caption("Synthetic data · Local execution · No real orders")
    return page


def show_header(page: str):
    title, description = PAGE_METADATA[page]
    st.markdown(
        '<div class="smc-header">'
        '<div class="smc-overline">SMECONNECT AI  /  SOFTWARE AGENTS & SWARM INTELLIGENCE</div>'
        '<h1>' + html.escape(title) + '</h1>'
        '<p>' + html.escape(description) + '</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="smc-trail">Workspace / <b>' + html.escape(page) + '</b> · Synthetic simulation</div>', unsafe_allow_html=True)
