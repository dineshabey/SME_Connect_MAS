"""Streamlit MAS Observatory: animate the real negotiation trace, not staged output."""
import html
import time
import streamlit as st
from smeconnect.simulation.engine import run_one_offer, run_retailer_offer
from smeconnect.simulation.negotiation import run_negotiation

st.set_page_config(page_title="SMEConnect AI", page_icon="🤝", layout="wide")
st.markdown("""
<style>
.block-container{max-width:1170px;padding-top:2rem}
.mas-hero{background:linear-gradient(110deg,#13263f,#174b4e);padding:26px;border:1px solid #2b7985;border-radius:18px;color:white;margin-bottom:20px}
.mas-hero h2{color:white;margin:0 0 7px;font-size:1.75rem}
.mas-hero p{margin:0;color:#bed8df}
.mas-stage{background:linear-gradient(140deg,#142034,#1e3048);color:#e9f1fb;padding:20px;border:1px solid #415973;border-radius:18px}
.mas-network{display:grid;grid-template-columns:1fr 1.5fr 1fr;gap:13px;align-items:center}
.mas-agent{background:#1d4358;border:1px solid #3c87a0;text-align:center;border-radius:14px;padding:20px 8px}
.mas-agent.seller{background:#1b473c;border-color:#3d9b82}
.mas-agent .emoji{font-size:35px}
.mas-agent strong{display:block;font-size:17px}
.mas-agent small{color:#c8dae4;font-size:12px}
.mas-link{text-align:center;min-height:110px;position:relative;padding-top:12px}
.mas-chip{display:inline-block;border-radius:30px;background:#215378;border:1px solid #4db1d7;padding:6px 12px;font-size:12px;font-weight:bold}
.mas-rail{position:relative;margin:25px 5px 12px;height:5px;border-radius:5px;background:linear-gradient(90deg,#35baa3,#69aeef)}
.mas-dot{position:absolute;top:-7px;width:18px;height:18px;background:white;border:3px solid #38bdf8;border-radius:50%;box-shadow:0 0 20px #38bdf8;animation:mas-right 1.1s ease-in-out infinite}
.mas-dot.back{animation:mas-left 1.1s ease-in-out infinite}
@keyframes mas-right{from{left:0}to{left:calc(100% - 18px)}}
@keyframes mas-left{from{left:calc(100% - 18px)}to{left:0}}
.mas-why{background:#102b40;border:1px solid #3b5d77;border-radius:10px;padding:13px;margin-top:15px;font-size:13px}
.mas-trace{display:flex;flex-wrap:wrap;gap:6px;margin-top:13px}
.mas-step{background:#214059;color:#dbe9f3;padding:7px 10px;border:1px solid #3d6280;border-radius:8px;font-size:11px}
.mas-step.active{background:#167982;color:white;box-shadow:0 0 12px #22d3ee55}
@media(max-width:650px){.mas-network{grid-template-columns:1fr}.mas-link{min-height:80px}}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="mas-hero"><h2>🤝 SMEConnect AI · Multi-Agent Observatory</h2><p>Independent LangGraph agents · Real message bus · Animated simulation events</p></div>',unsafe_allow_html=True)

def trace_frame(timeline, index):
    event=timeline[index]
    clean=lambda value: html.escape(str(value),quote=True)
    seller=clean(event["sender"] if event["sender"].startswith("S") else event["receiver"])
    retailer=clean(event["sender"] if event["sender"].startswith("R") else event["receiver"])
    reverse="back" if event["sender"].startswith("S") else ""
    steps="".join(f'<div class="mas-step {"active" if j==index else ""}">{j+1}. {clean(v["performative"])}</div>' for j,v in enumerate(timeline))
    return f"""<div class="mas-stage">
    <div class="mas-network">
      <div class="mas-agent"><div class="emoji">🛒</div><strong>Retailer {retailer}</strong><small>Budget · Demand · Profit</small></div>
      <div class="mas-link"><span class="mas-chip">{clean(event["performative"])} · Rs. {clean(event["price"])}</span>
        <div class="mas-rail"><div class="mas-dot {reverse}"></div></div>
        <small>{clean(event["sender"])} → {clean(event["receiver"])}</small></div>
      <div class="mas-agent seller"><div class="emoji">🏪</div><strong>Seller {seller}</strong><small>Stock · Target · Margin</small></div>
    </div>
    <div class="mas-why"><b>Round {clean(event["round"])} · Event {index+1}/{len(timeline)}</b><br>{clean(event["reason"])}</div>
    <div class="mas-trace">{steps}</div></div>"""

tab_live,tab_seller,tab_retailer=st.tabs(["🔄 Animated Negotiation","🏪 Seller Workflow","🛒 Retailer Workflow"])
with tab_live:
    st.subheader("Seller ↔ Retailer · Autonomous negotiation")
    st.caption("Messages below come from executed LangGraph decisions. Any agreement is provisional; no real orders are placed.")
    c1,c2,c3,c4=st.columns(4)
    seller_id=c1.selectbox("Seller Agent",["S1","S2"])
    retailer_id=c2.selectbox("Retailer Agent",["R1","R2"])
    start_price=c3.slider("Initial offer (Rs.)",100,190,150,step=5)
    quantity=c4.number_input("Packets",min_value=1,max_value=300,value=200,step=10)
    a,b,c=st.columns(3)
    target=a.slider("Retailer target (Rs.)",100,190,150,step=5)
    rounds=b.slider("Maximum rounds",1,10,5)
    speed=c.selectbox("Animation speed",["Slow","Normal","Fast"],index=1)
    if st.button("▶ Run negotiation and animate",type="primary",key="negotiate"):
        try:
            result=run_negotiation(seller_id=seller_id,retailer_id=retailer_id,
                initial_price=float(start_price),quantity=int(quantity),
                retailer_target=float(target),max_rounds=rounds)
            st.session_state["negotiation_result"]=result
        except (ValueError,RuntimeError,PermissionError) as exc:
            st.error(f"Simulation stopped: {exc}")
    result=st.session_state.get("negotiation_result")
    if result:
        timeline=result["timeline"]
        placeholder=st.empty()
        if st.session_state.get("last_animation")!=result["conversation_id"]:
            for i in range(len(timeline)):
                placeholder.markdown(trace_frame(timeline,i),unsafe_allow_html=True)
                time.sleep({"Slow":1.0,"Normal":0.55,"Fast":0.2}[speed])
            st.session_state["last_animation"]=result["conversation_id"]
        else:
            placeholder.markdown(trace_frame(timeline,len(timeline)-1),unsafe_allow_html=True)
        x,y,z=st.columns(3)
        x.metric("Negotiation outcome",result["status"])
        y.metric("Rounds",result["rounds"])
        z.metric("Provisional unit price",f'Rs. {result["agreed_price"]:,.2f}' if result["agreed_price"] is not None else "—")
        st.info(result["note"])
        st.subheader("Actual agent message timeline")
        st.dataframe(timeline,use_container_width=True,hide_index=True)
        with st.expander("Raw validated message records"):
            st.json([m.model_dump(mode="json") for m in result["messages"]])

with tab_seller:
    st.caption("Original seller-only workflow demonstration.")
    if st.button("Run first proposal",key="seller_run"):
        result=run_one_offer()
        st.metric("Registered agent instances",len(result["agents"]))
        st.metric("Messages sent",len(result["messages"]))
        st.info(f'Seller decision: {result["decision"]}')
        with st.expander("Agent characters"):
            for agent in result["agents"]:
                st.write(f"{agent.agent_id} | {agent.role} | {agent.goal} | {agent.strategy}")
        st.json([m.model_dump(mode="json") for m in result["messages"]])

with tab_retailer:
    st.subheader("Autonomous Retailer Offer Evaluation")
    st.caption("Standalone retailer workflow; no peer communication here. Use the first tab for actual messaging.")
    retailer=st.selectbox("Retailer character",["R1","R2"])
    offered=st.slider("Seller offered price",100,220,165,step=5)
    qty=st.slider("Requested quantity",1,300,200)
    preferred=st.slider("Retailer preferred price",100,200,150,step=5)
    retail_price=st.slider("Expected retail selling price",100,250,200,step=5)
    if st.button("Evaluate with Retailer LangGraph",key="retailer_run"):
        evaluation=run_retailer_offer(offered_price=float(offered),requested_quantity=qty,
            target_price=float(preferred),expected_retail_price=float(retail_price),
            retailer_id=retailer)
        agent,result=evaluation["retailer"],evaluation["result"]
        st.write(f'**Agent:** {agent.agent_id} | **Goal:** {agent.goal} | **Strategy:** {agent.strategy}')
        q1,q2,q3=st.columns(3)
        q1.metric("Purchase cost",f'Rs. {result["purchase_cost"]:,.2f}')
        q2.metric("Expected gross profit",f'Rs. {result["expected_gross_profit"]:,.2f}')
        q3.metric("Retailer budget",f'Rs. {agent.budget:,.2f}')
        st.info(f'Decision: {result["decision"]}')
        if result["counter_price"] is not None:
            st.write(f'**Counter-offer:** Rs. {result["counter_price"]:,.2f}')
        st.write(f'**Reason:** {result["reason"]}')
        with st.expander("Full LangGraph state"):
            st.json(result)
