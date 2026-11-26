"""Three-agent competition teaching screen using recorded LangGraph negotiations."""
import html
import time
import streamlit as st
from dashboard.negotiation_viz import neon_scene
from smeconnect.simulation.supplier_selection import run_supplier_competition


def render_competition():
    st.markdown("### Phase 03 · Multiple Sellers, One Independent Retailer")
    st.caption("Retailer discovers sellers, negotiates separately, compares public outcomes and selects a supplier using its own LangGraph decision graph.")
    st.info("**සිංහලෙන්:** Retailer Agent එක Seller S1 සහ S2 සමඟ වෙන වෙනම සාකච්ඡා කරලා, තමන්ට වැඩි ලාභයක් දෙන සුදුසු Seller තෝරනවා.")
    c1,c2,c3=st.columns(3)
    retailer=c1.selectbox("🛒 Retailer",["R1","R2"],key="multi_retailer")
    first_price=c2.slider("Initial offer (Rs.)",100,190,150,5,key="multi_offer")
    quantity=c3.number_input("Required packets",1,300,200,10,key="multi_qty")
    c4,c5,c6=st.columns(3)
    preferred=c4.slider("Retailer target (Rs.)",100,190,150,5,key="multi_target")
    max_rounds=c5.slider("Maximum rounds",1,10,5,key="multi_rounds")
    replay_speed=c6.selectbox("Replay speed",["Slow","Normal","Fast"],key="multi_speed",index=1)
    st.caption("Discovery includes S1 (margin-oriented) and S2 (volume-oriented). No seller shares private pricing limits with the retailer.")
    if st.button("▶ Run Supplier Competition",key="multi_run",type="primary",use_container_width=True):
        try:
            outcome=run_supplier_competition(retailer_id=retailer,initial_price=float(first_price),
                quantity=int(quantity),retailer_target=float(preferred),max_rounds=max_rounds)
            st.session_state["multi_outcome"]=outcome
            st.session_state["multi_step"]=0
            st.session_state["multi_seller"]="S1"
            st.session_state["multi_speed_used"]=replay_speed
        except (ValueError,RuntimeError,PermissionError) as err:
            st.session_state.pop("multi_outcome",None)
            st.error(f"Competition not started: {err}")
    outcome=st.session_state.get("multi_outcome")
    if not outcome:
        st.markdown("**Step 1:** Choose the business scenario and run a competition to discover two sellers.")
        return
    selection=outcome["selection"]
    winner=selection["selected_seller_id"]
    def card(agent_id,title,detail,selected=False):
        bg="#103d52" if not selected else "#095d57"
        border="#2e99bf" if not selected else "#38efc5"
        glow="box-shadow:0 0 20px #00d8bb55;" if selected else ""
        badge = ('<div style="color:#baffeb;font-size:12px;margin-top:8px">'
                 '✓ Selected supplier</div>') if selected else ''
        return (f'<div style="background:{bg};border:1px solid {border};{glow}border-radius:16px;'
                f'padding:20px 12px;text-align:center;color:white;min-height:133px">'
                f'<div style="font-size:34px">{title}</div><b>{html.escape(agent_id)}</b>'
                f'<div style="font-size:12px;color:#c9e6f1">{html.escape(detail)}</div>'
                f'{badge}</div>')

    st.markdown("### Step 2 · See the competing agent network")
    with st.container(border=True):
        s1,buyer,s2=st.columns([1,1.2,1])
        s1.markdown(card("Seller S1","🏪","Margin-oriented",winner=="S1"),unsafe_allow_html=True)
        buyer.markdown(card(outcome["retailer"].agent_id,"🛒","Independent supplier choice"),unsafe_allow_html=True)
        s2.markdown(card("Seller S2","🏬","Volume-oriented",winner=="S2"),unsafe_allow_html=True)
        st.caption("↖ Separate message conversation with S1                 Separate message conversation with S2 ↗")
        st.markdown("**Two independent negotiations → Retailer evaluation → One provisional supplier choice**")
    st.markdown("### Step 3 · Compare real negotiation outcomes")
    st.dataframe(selection["evaluations"],use_container_width=True,hide_index=True)
    if winner:
        st.success(f'🏆 Retailer chose **{winner}** at **Rs. {selection["selected_price"]:,.2f}** per packet. '
                   f'Expected gross profit: **Rs. {selection["expected_gross_profit"]:,.2f}**.')
    else:
        st.warning("No feasible agreement; the retailer did not select a seller.")
    st.write("**Why the retailer decided:**",selection["reasoning"])
    st.caption("Expected gross profit excludes transport/overhead. Supplier choice is provisional and reserves no stock or payment.")
    st.markdown("### Step 4 · Explore each agent's Thinking and messages")
    selected=st.radio("Which seller negotiation would you like to inspect?",
                      outcome["evaluated_seller_ids"],horizontal=True,key="multi_inspect")
    timeline=outcome["negotiations"][selected]["timeline"]
    position=st.slider("Recorded message",1,len(timeline),1,key=f"multi_event_{selected}")-1
    placeholder=st.empty()
    placeholder.markdown(neon_scene(timeline,position,outcome["retailer"].agent_id,selected),
                         unsafe_allow_html=True)
    if st.button("▶ Animate this conversation",key="multi_replay"):
        delay={"Slow":1.0,"Normal":0.6,"Fast":0.25}[st.session_state.get("multi_speed_used","Normal")]
        for k in range(len(timeline)):
            placeholder.markdown(neon_scene(timeline,k,outcome["retailer"].agent_id,selected),
                                 unsafe_allow_html=True)
            time.sleep(delay)
    with st.expander("🔍 Technical evidence: both conversations and actual messages"):
        for agent_id,run in outcome["negotiations"].items():
            st.markdown(f'**{agent_id} — {run["status"]} — {run["conversation_id"]}**')
            st.dataframe(run["timeline"],use_container_width=True,hide_index=True)
    st.markdown("### What MAS characteristics are demonstrated?")
    st.write("**Discovery:** coordinator returns registered seller IDs. "
             "**Competition:** sellers pursue distinct strategies in separate conversations. "
             "**Autonomy:** retailer decides with its own utility-based LangGraph graph. "
             "**Communication and negotiation:** all offers are genuine recorded message-bus events.")
