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
    "🎓 Viva Presentation",
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
    PAGES[9]: ("Viva presentation mode", "An English-only, step-by-step demonstration of real MAS decisions and evidence."),
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
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {font-size:18px!important}
section[data-testid="stSidebar"] {min-width:310px!important;}
.smc-menu-group{font-size:12px;font-weight:850;letter-spacing:.13em;
    color:#7eaabd;margin:17px 4px 8px;text-transform:uppercase;}
section[data-testid="stSidebar"] [class*="st-key-smc_nav_"] button{
    width:100%;min-height:54px;text-align:left;justify-content:flex-start;
    border:1px solid transparent;border-radius:13px;padding:12px 15px;
    background:transparent;color:#bdcede;font-size:18px;font-weight:650;
    box-shadow:none;transition:background .15s ease,border-color .15s ease;
}
section[data-testid="stSidebar"] [class*="st-key-smc_nav_"] button p{
    font-size:18px!important;line-height:1.4;text-align:left;white-space:normal;
}
section[data-testid="stSidebar"] [class*="st-key-smc_nav_"] button:hover{
    background:#1c3b4e;border-color:#3c6e82;color:#fff;
}
section[data-testid="stSidebar"] [class*="st-key-smc_nav_"] button[kind="primary"]{
    background:linear-gradient(105deg,#1b5a66,#1c4e65)!important;
    border:1px solid #4aa6b3!important;color:#fff!important;
    box-shadow:inset 4px 0 #76e3d5,0 5px 14px rgba(0,0,0,.2)!important;
}
section[data-testid="stSidebar"] [class*="st-key-smc_nav_"] button:focus-visible{
    outline:2px solid #78ecde;outline-offset:2px;
}
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
/* Overview redesign: dimensional KPI cards and visual identity for every agent. */
.smc-overview-intro{
    display:flex;justify-content:space-between;align-items:center;gap:24px;
    padding:12px 0 18px;flex-wrap:wrap;
}
.smc-overview-intro h2{margin:0!important;font-size:32px!important}
.smc-overview-intro p{color:#aec6d7;margin:5px 0 0;font-size:18px!important}
.smc-overview-pill{
    border:1px solid #3b777d;background:#143b43;color:#9bf1dc;
    border-radius:999px;padding:9px 15px;font-size:15px;font-weight:750;
}
.smc-kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px;margin:6px 0 28px;}
.smc-kpi-card{
    position:relative;isolation:isolate;overflow:hidden;min-height:210px;
    padding:24px 25px 22px;border-radius:22px;
    background:linear-gradient(145deg,#162d42 0%,#193c50 100%);
    border:1px solid rgba(128,194,224,.38);
    box-shadow:0 17px 32px rgba(1,7,17,.3),inset 0 1px 0 rgba(255,255,255,.10);
    transform:translateY(0);transition:transform .22s ease,box-shadow .22s ease;
}
.smc-kpi-card:hover{transform:translateY(-5px);box-shadow:0 23px 44px rgba(0,0,0,.39);}
.smc-kpi-card::before{
    content:"";position:absolute;inset:-50% -30% auto auto;width:90%;height:115%;
    transform:rotate(28deg);background:linear-gradient(90deg,transparent,rgba(255,255,255,.065),transparent);
    pointer-events:none;z-index:-1;
}
.smc-kpi-card::after{
    content:"";position:absolute;right:-25px;bottom:-70px;width:165px;height:165px;
    border-radius:50%;background:var(--kpi-glow,rgba(74,203,219,.17));filter:blur(9px);z-index:-1;
}
.smc-kpi-card.smc-green{background:linear-gradient(145deg,#173b43,#14524d);--kpi-glow:rgba(77,234,170,.20)}
.smc-kpi-card.smc-blue{background:linear-gradient(145deg,#1b2c4b,#244a75);--kpi-glow:rgba(109,163,255,.23)}
.smc-kpi-card.smc-purple{background:linear-gradient(145deg,#292c52,#473b69);--kpi-glow:rgba(190,142,251,.22)}
.smc-kpi-top{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:10px;}
.smc-kpi-label{font-size:21px!important;font-weight:750;color:#f0f8ff;line-height:1.35;}
.smc-kpi-icon{display:grid;place-items:center;width:53px;height:53px;border-radius:16px;
    background:rgba(255,255,255,.12);font-size:27px;flex-shrink:0;}
.smc-kpi-value{font-size:70px!important;line-height:1.12;font-weight:850;letter-spacing:-.055em;color:#fff;margin:8px 0;}
.smc-kpi-detail{font-size:16px!important;color:#d1e4ef;line-height:1.45;}
.smc-agent-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin:10px 0 30px;}
.smc-agent-card{
    position:relative;overflow:hidden;min-height:210px;padding:24px;
    border-radius:21px;border:1px solid rgba(126,187,213,.31);
    background:linear-gradient(140deg,#18384b,#174856);
    box-shadow:0 14px 30px rgba(0,0,0,.25),inset 0 1px rgba(255,255,255,.10);
    transition:transform .22s ease,box-shadow .22s ease;
}
.smc-agent-card:hover{transform:translateY(-4px);box-shadow:0 20px 39px rgba(0,0,0,.36);}
.smc-agent-card::after{content:"";position:absolute;right:-42px;bottom:-60px;width:175px;height:175px;
    border-radius:50%;background:rgba(84,220,222,.13);filter:blur(1px);}
.smc-agent-card.retailer{background:linear-gradient(145deg,#182e4b,#284b77);}
.smc-agent-card.retailer::after{background:rgba(113,158,255,.18)}
.smc-agent-card.delivery{background:linear-gradient(145deg,#29284d,#4b3c73);}
.smc-agent-card.delivery::after{background:rgba(176,125,244,.18)}
.smc-agent-card.market{background:linear-gradient(145deg,#203c37,#255c53);}
.smc-agent-card.market::after{background:rgba(86,220,154,.18)}
.smc-agent-card.coordinator{background:linear-gradient(145deg,#473227,#664f36);}
.smc-agent-card.coordinator::after{background:rgba(242,179,109,.18)}
.smc-agent-upper{display:flex;align-items:center;gap:16px;position:relative;z-index:1;}
.smc-agent-avatar{width:64px;height:64px;display:grid;place-items:center;flex-shrink:0;
    background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.16);border-radius:19px;font-size:34px;}
.smc-agent-id{font-size:25px!important;font-weight:800;line-height:1.2;color:white;}
.smc-agent-title{font-size:17px!important;color:#d7e8f1;margin-top:3px;}
.smc-agent-description{font-size:18px!important;line-height:1.5;color:#e0edf4;margin:20px 0 14px;position:relative;z-index:1;}
.smc-agent-role{display:inline-flex;font-size:14px!important;font-weight:800;letter-spacing:.08em;
    border:1px solid rgba(255,255,255,.23);border-radius:999px;padding:7px 13px;
    color:#f1fbff;background:rgba(255,255,255,.09);position:relative;z-index:1;}
.smc-section-title{font-size:30px!important;font-weight:800;letter-spacing:-.02em;margin:18px 0 16px;}
/* Right-hand workflow launcher: visible, purposeful navigation rather than empty rows. */
.smc-launch-intro{
    font-size:17px!important;line-height:1.5;color:#b9ccdd;
    margin:-3px 0 15px;
}
.smc-launch-item{display:flex;gap:16px;align-items:center;padding:5px 0 13px;}
.smc-launch-icon{
    width:64px;height:64px;flex-shrink:0;display:grid;place-items:center;
    border-radius:18px;font-size:32px;
    background:linear-gradient(145deg,#234c60,#236d72);
    border:1px solid rgba(143,210,218,.33);box-shadow:0 7px 18px rgba(0,0,0,.22);
}
.smc-launch-compete .smc-launch-icon{background:linear-gradient(145deg,#35517e,#3e6c9b);}
.smc-launch-analytics .smc-launch-icon{background:linear-gradient(145deg,#3d3e71,#6a4d8a);}
.smc-launch-copy{min-width:0;flex:1;}
.smc-launch-kicker{font-size:13px!important;font-weight:850;letter-spacing:.12em;color:#7de5d8;}
.smc-launch-title{font-size:22px!important;font-weight:800;color:#f4faff;line-height:1.3;margin:3px 0 4px;}
.smc-launch-description{font-size:16px!important;line-height:1.48;color:#c0d0df;}
.st-key-quick_market button,
.st-key-quick_compete button,
.st-key-quick_experiment button{
    min-height:49px!important;border-radius:11px!important;
    background:#17374b!important;border:1px solid #3d7b8f!important;
    color:#dffaff!important;font-weight:700!important;
}
.st-key-quick_market button:hover,
.st-key-quick_compete button:hover,
.st-key-quick_experiment button:hover{
    background:#215269!important;border-color:#6cd4d3!important;
}
@media(max-width:760px){
  .smc-launch-icon{width:53px;height:53px;font-size:26px;}
  .smc-launch-title{font-size:19px!important;}
  .smc-launch-description{font-size:15px!important;}
}
.smc-mini-step{display:flex;align-items:flex-start;gap:13px;border-radius:14px;
    background:rgba(36,73,94,.35);padding:15px;margin-bottom:14px;}
.smc-mini-number{min-width:40px;height:40px;display:grid;place-items:center;
    background:#245868;border-radius:12px;font-size:17px;font-weight:800;color:#dbfefe;}
.smc-mini-title{font-size:19px!important;font-weight:750;color:#f4fbff}
.smc-mini-copy{font-size:16px!important;color:#b7ccdb;margin-top:4px}
@media(max-width:1280px){
    .smc-kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));}
    .smc-agent-grid{grid-template-columns:repeat(2,minmax(0,1fr));}
}
@media(max-width:760px){
    .smc-kpi-grid,.smc-agent-grid{grid-template-columns:1fr;}
    .smc-kpi-card{min-height:155px;padding:20px;}
    .smc-kpi-label{font-size:19px!important}
    .smc-kpi-value{font-size:53px!important}
    .smc-agent-card{min-height:165px;}
    .smc-agent-id{font-size:22px!important}
}
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
    """Switch workspace before the sidebar buttons are re-rendered."""
    if page not in PAGES:
        raise ValueError("Unknown navigation destination.")
    st.session_state["nav_page"] = page


def show_sidebar() -> str:
    """Use real Streamlit buttons, not radio inputs or noninteractive HTML links."""
    if st.session_state.get("nav_page") not in PAGES:
        st.session_state["nav_page"] = PAGES[0]
    selected = st.session_state["nav_page"]
    with st.sidebar:
        st.markdown(
            '<div class="smc-brand">◈ SME<span>Connect</span> AI</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="smc-sidebar-caption">MULTI-AGENT MARKETPLACE'
            '<br>ACADEMIC SIMULATION</p>',
            unsafe_allow_html=True,
        )
        st.divider()
        groups = (
            ("WORKSPACE", (0, 1)),
            ("AGENT WORKFLOWS", (2, 3, 4, 5)),
            ("LEARNING LABS", (6, 7, 8)),
            ("PRESENTATION", (9,)),
        )
        for group, indices in groups:
            st.markdown(
                f'<div class="smc-menu-group">{html.escape(group)}</div>',
                unsafe_allow_html=True,
            )
            for index in indices:
                page = PAGES[index]
                st.button(
                    page,
                    key=f"smc_nav_{index}",
                    type="primary" if selected == page else "secondary",
                    use_container_width=True,
                    on_click=navigate_to,
                    args=(page,),
                )
        st.divider()
        st.caption("MSc IT6415 · Software Agents & Swarm Intelligence")
        st.caption("Synthetic data · Local execution · No real orders")
    return selected


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
