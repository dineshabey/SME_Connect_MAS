"""SMEConnect AI: step-by-step teaching dashboard driven by real agent events."""
import html
import time

import streamlit as st

from smeconnect.environment.marketplace import build_agents
from smeconnect.simulation.engine import run_one_offer, run_retailer_offer
from smeconnect.simulation.negotiation import run_negotiation
from dashboard.negotiation_viz import neon_scene
from dashboard.competition_viz import render_competition
from dashboard.marketplace_viz import render_marketplace
from dashboard.delivery_viz import render_delivery_coordination
from dashboard.market_experiment_viz import render_market_experiment
from dashboard.experiment_evaluation_viz import render_experiment_evaluation

st.set_page_config(page_title="SMEConnect AI | MAS Learning Lab", page_icon="🤝", layout="wide")
st.markdown(
    """
    <style>
    .block-container{max-width:1120px;padding-top:1.7rem;padding-bottom:3rem}
    .hero{background:linear-gradient(110deg,#142b42,#136b73);border:1px solid #328a93;
      padding:23px 26px;border-radius:17px;color:#f5fafc;margin-bottom:14px}
    .hero h2{font-size:1.8rem;color:white;margin:0 0 7px}
    .hero p{margin:0;color:#d7e7f0}
    .eyebrow{font-size:.8rem;font-weight:700;letter-spacing:.08em;color:#70d5d6}
    .guide{padding:14px 18px;border:1px solid #39536f;border-radius:12px;
      background:#14283b;color:#e8f1f9;margin:12px 0}
    .guide b{color:#b8f2f2}
    .diagram{background:linear-gradient(135deg,#17283c,#1b3644);color:#f2f8fc;
      padding:20px;border:1px solid #375c72;border-radius:17px;margin-top:8px}
    .network{display:grid;grid-template-columns:1fr 1.35fr 1fr;align-items:center;gap:13px}
    .actor{background:#1d4565;border:1px solid #4589b1;padding:20px 10px;
      border-radius:12px;text-align:center;min-height:135px}
    .actor.seller{background:#21513e;border-color:#3aa784}
    .actor .emoji{font-size:32px;margin-bottom:6px}
    .actor strong{font-size:17px;display:block}
    .actor small{color:#d8e8ed;font-size:12px;display:block;margin-top:6px}
    .signal{text-align:center;min-height:116px;padding-top:13px}
    .signal b{display:inline-block;background:#14597a;border:1px solid #45afd0;
      padding:7px 13px;border-radius:24px;font-size:13px}
    .signal small{display:block;margin:6px 0;color:#d6e5ed}
    .rail{height:5px;background:linear-gradient(90deg,#21c59d,#55a9f1);position:relative;margin:19px 8px 10px;border-radius:10px}
    .dot{position:absolute;top:-8px;height:20px;width:20px;border-radius:50%;
      background:#fff;border:3px solid #38bdf8;box-shadow:0 0 14px #50c2fe}
    .dot.forward{animation:forward 1.2s ease-in-out infinite}
    .dot.backward{animation:backward 1.2s ease-in-out infinite}
    @keyframes forward{0%{left:0}100%{left:calc(100% - 20px)}}
    @keyframes backward{0%{left:calc(100% - 20px)}100%{left:0}}
    .explainer{background:#0f3040;border-left:4px solid #37b4c5;border-radius:7px;
      padding:14px;margin-top:17px;line-height:1.7}
    .steps{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}
    .step{background:#2d4256;border:1px solid #46617b;padding:6px 10px;
      border-radius:7px;font-size:11px}
    .step.current{background:#126f7c;border-color:#3ad0d0;font-weight:700}
    @media(max-width:700px){.network{grid-template-columns:1fr}.actor{min-height:95px}
      .signal{min-height:95px}.hero h2{font-size:1.4rem}}
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero"><div class="eyebrow">MSc IT6415 · SOFTWARE AGENTS AND SWARM INTELLIGENCE</div>'
    '<h2>🤝 SMEConnect AI — Multi-Agent Learning Lab</h2>'
    '<p>See what each agent knows, why it responds, and how a negotiation develops — one message at a time.</p></div>',
    unsafe_allow_html=True,
)

def safe(value):
    return html.escape(str(value), quote=True)

def event_explanation(event):
    """Teaching labels are derived from the actual recorded event, never fake messages."""
    sender, action = event["sender"], event["performative"]
    if action == "ACCEPT-PROPOSAL":
        return ("Agreement / එකඟතාව",
                f"{sender} accepts the latest offer at Rs. {event['price']:,.2f}. "
                "This is a provisional price agreement, not a completed order.",
                "Negotiation + Autonomy")
    if action == "REJECT-PROPOSAL":
        return ("Rejection / ප්‍රතික්ෂේප කිරීම",
                f"{sender} refuses the offer at Rs. {event['price']:,.2f}. "
                "There is no price agreement.",
                "Autonomy + Rationality")
    if sender.startswith("R"):
        return ("Retailer offer / මිලදී ගැනීමේ යෝජනාව",
                f"Retailer {sender} proposes Rs. {event['price']:,.2f} per packet. "
                "The seller will evaluate it using its own rules.",
                "Communication + Goal-oriented behaviour")
    return ("Seller counter-offer / විකුණුම්කරුගේ යෝජනාව",
            f"Seller {sender} proposes Rs. {event['price']:,.2f} per packet. "
            "The retailer will evaluate its own affordability and profit.",
            "Negotiation + Independent decisions")

def event_visual(timeline, index, buyer, seller):
    """The visual is driven by recorded messages from the negotiation engine."""
    return neon_scene(timeline, index, buyer, seller)


def set_step(index, count):
    st.session_state["walk_step"] = min(max(index, 0), count - 1)

tab_marketplace, tab_competition, tab_delivery, tab_market, tab_evaluation, tab_tour, tab_seller, tab_retailer = st.tabs(
    ["🏬 Marketplace", "🏆 Phase 03 · Supplier Competition",
     "🚚 Phase 04 · Delivery Coordination", "📈 Phase 05 · Market Adaptation",
     "🧪 Phase 05.2 · Experiments", "🎓 Guided Negotiation",
     "🏪 Seller Decision Lab", "🛒 Retailer Decision Lab"]
)
with tab_marketplace:
    render_marketplace()
with tab_market:
    render_market_experiment()
with tab_evaluation:
    render_experiment_evaluation()
with tab_delivery:
    render_delivery_coordination()
with tab_competition:
    render_competition()
with tab_tour:
    st.markdown("### STEP 1 · Understand the business scenario")
    st.markdown(
        '<div class="guide"><b>Why?</b> A retailer wants to buy peanut packets at a good price; '
        'a seller wants to protect its margin. Their goals differ, so they need to negotiate.'
        '<br><b>සිංහලෙන්:</b> Retailer අඩු මිලක් බලාපොරොත්තු වෙනවා. Seller ඉහළ මිලක් බලාපොරොත්තු වෙනවා. '
        'ඒ නිසා දෙන්නා අතර සාකච්ඡාවක් අවශ්‍යයි.</div>',
        unsafe_allow_html=True,
    )
    with st.expander("ℹ️ Learn the MAS terms before starting", expanded=False):
        st.markdown(
            "**Agent:** A software participant with its own goal and decision rules.\n\n"
            "**PROPOSE:** Offer a unit price.\n\n"
            "**COUNTER-OFFER:** Respond with a different price (encoded as another PROPOSE).\n\n"
            "**ACCEPT-PROPOSAL:** Agree on the offered price.\n\n"
            "**REJECT-PROPOSAL:** Refuse the offer.\n\n"
            "**One round:** Seller evaluation plus possible retailer response. One round can contain several messages."
        )
    agents = {a.agent_id: a for a in build_agents()}
    with st.container(border=True):
        a, b = st.columns(2)
        seller_id = a.selectbox("🏪 Choose seller", ["S1", "S2"], help="Each seller uses its own stock and pricing constraints.")
        retailer_id = b.selectbox("🛒 Choose retailer", ["R1", "R2"], help="Each retailer has its own budget, demand and maximum price.")
        x, y = st.columns(2)
        x.info(f"**{seller_id} — Seller**\n\nGoal: {agents[seller_id].goal}  \nStrategy: {agents[seller_id].strategy}")
        y.info(f"**{retailer_id} — Retailer**\n\nGoal: {agents[retailer_id].goal}  \nStrategy: {agents[retailer_id].strategy}")
        p, q, r = st.columns(3)
        start_price = p.slider("Retailer's first offer (Rs.)", 100, 190, 150, 5)
        quantity = q.number_input("Packets wanted", min_value=1, max_value=300, value=200, step=10)
        target = r.slider("Retailer's target price (Rs.)", 100, 190, 150, 5)
        with st.expander("⚙️ Advanced settings", expanded=False):
            maximum_rounds = st.slider("Maximum negotiation rounds", 1, 10, 5)
            speed = st.selectbox("Replay speed", ["Slow", "Normal", "Fast"], index=1)
        st.caption("All figures are synthetic. No real buyer, payment or order is involved.")
        start = st.button("▶ Start negotiation", type="primary", use_container_width=True)
    if start:
        try:
            outcome = run_negotiation(
                seller_id=seller_id, retailer_id=retailer_id, initial_price=float(start_price),
                quantity=int(quantity), retailer_target=float(target),
                max_rounds=maximum_rounds,
            )
            st.session_state["guided_outcome"] = outcome
            st.session_state["walk_step"] = 0
            st.session_state["guided_speed"] = speed
        except (ValueError, RuntimeError, PermissionError, KeyError) as exc:
            st.error(f"Negotiation could not start: {exc}")
    outcome = st.session_state.get("guided_outcome")
    if not outcome:
        st.markdown(
            '<div class="guide"><b>Next:</b> Select your two agents and press '
            '<b>Start negotiation</b>. Then inspect each real message one by one.</div>',
            unsafe_allow_html=True,
        )
    else:
        timeline = outcome["timeline"]
        current = min(st.session_state.get("walk_step", 0), len(timeline)-1)
        st.markdown("### STEP 2 · Watch the agents communicate and think")
        st.caption("Neon robot view: the glowing 'Thinking' panels explain which implemented decision rules apply at this event. They are not private AI thoughts. Use Previous / Next or Replay to follow the actual recorded messages.")
        st.progress((current+1)/len(timeline), text=f"Message {current+1} of {len(timeline)}")
        view = st.empty()
        view.markdown(event_visual(
            timeline, current, outcome["retailer"].agent_id, outcome["seller"].agent_id
        ), unsafe_allow_html=True)
        back, forward, play = st.columns([1, 1, 2])
        with back:
            if st.button("← Previous", disabled=current==0, use_container_width=True):
                set_step(current-1, len(timeline))
                st.rerun()
        with forward:
            if st.button("Next →", disabled=current==len(timeline)-1, use_container_width=True):
                set_step(current+1, len(timeline))
                st.rerun()
        with play:
            if st.button("▶ Replay all messages", use_container_width=True):
                delay = {"Slow":1.2, "Normal":0.75, "Fast":0.3}[st.session_state.get("guided_speed", "Normal")]
                for i in range(len(timeline)):
                    view.markdown(event_visual(timeline, i, outcome["retailer"].agent_id,
                        outcome["seller"].agent_id), unsafe_allow_html=True)
                    time.sleep(delay)
                st.session_state["walk_step"] = len(timeline)-1
                st.rerun()
        st.markdown("### STEP 3 · Understand the result")
        d1,d2,d3 = st.columns(3)
        d1.metric("Negotiation result", outcome["status"])
        d2.metric("Rounds used", outcome["rounds"])
        d3.metric("Agreed unit price", f'Rs. {outcome["agreed_price"]:,.2f}' if outcome["agreed_price"] is not None else "No agreement")
        if outcome["status"]=="AGREED":
            st.success("✅ The two agents reached a **provisional price agreement**.")
        elif outcome["status"]=="REJECTED":
            st.warning("⚠️ An agent rejected an offer. No price agreement was reached.")
        else:
            st.warning("⏹️ The maximum number of rounds was reached without agreement.")
        st.info("Negotiation only: **no payment, inventory update, delivery booking or real sale**.")
        st.markdown("### STEP 4 · Explain the MAS evidence")
        st.markdown(
            "**Communication:** Messages have a sender, receiver, and performative.\n\n"
            "**Autonomy:** Each LangGraph agent evaluates offers with its own constraints.\n\n"
            "**Negotiation:** Offers can be accepted, rejected, or counter-proposed.\n\n"
            "**Bounded interaction:** The process stops on an outcome or a round limit."
        )
        with st.expander("🔍 Professor / developer view — actual message timeline and raw JSON"):
            st.dataframe(timeline, use_container_width=True, hide_index=True)
            st.caption(f'Conversation ID: {outcome["conversation_id"]}')
            st.json([m.model_dump(mode="json") for m in outcome["messages"]])

with tab_seller:
    st.subheader("Seller Decision Lab")
    st.write("A single seller evaluates one incoming proposal. This is **not** a full negotiation.")
    if st.button("Evaluate one seller offer", key="seller_test"):
        r = run_one_offer()
        st.metric("Registered agent instances", len(r["agents"]))
        st.metric("Messages sent", len(r["messages"]))
        st.info(f'Seller decision: **{r["decision"]}**')
        with st.expander("Agent characters"):
            for agent in r["agents"]:
                st.write(f"{agent.agent_id} · {agent.role} · {agent.goal} · {agent.strategy}")
        with st.expander("Raw message"):
            st.json([m.model_dump(mode="json") for m in r["messages"]])

with tab_retailer:
    st.subheader("Retailer Decision Lab")
    st.write("A retailer evaluates an offered price using its own budget, demand and expected profit.")
    retailer = st.selectbox("Retailer", ["R1", "R2"], key="retailer_lab")
    a,b = st.columns(2)
    offered = a.slider("Seller's offered price", 100, 220, 165, 5, key="price_lab")
    qty = b.slider("Quantity", 1, 300, 200, key="qty_lab")
    c,d = st.columns(2)
    preferred = c.slider("Preferred price", 100, 200, 150, 5, key="target_lab")
    retail_price = d.slider("Expected selling price", 100, 250, 200, 5, key="sale_lab")
    if st.button("Evaluate retailer offer", key="retailer_test"):
        r = run_retailer_offer(offered_price=float(offered), requested_quantity=qty,
            target_price=float(preferred), expected_retail_price=float(retail_price), retailer_id=retailer)
        state = r["result"]
        a,b,c = st.columns(3)
        a.metric("Purchase cost", f'Rs. {state["purchase_cost"]:,.2f}')
        b.metric("Expected gross profit", f'Rs. {state["expected_gross_profit"]:,.2f}')
        c.metric("Budget", f'Rs. {r["retailer"].budget:,.2f}')
        st.info(f'**Decision:** {state["decision"]} — {state["reason"]}')
        if state["counter_price"] is not None:
            st.write(f'**Counter-offer:** Rs. {state["counter_price"]:,.2f}')
        with st.expander("Full LangGraph state (developer view)"):
            st.json(state)
