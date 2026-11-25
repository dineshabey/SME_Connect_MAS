import streamlit as st

from smeconnect.simulation.engine import run_one_offer, run_retailer_offer

st.set_page_config(page_title="SMEConnect AI", layout="wide")
st.title("SMEConnect AI — MAS Starter")
st.caption("LangGraph seller and retailer decision workflows; multi-round agent communication is next.")

tab_seller, tab_retailer = st.tabs(["Seller workflow (Phase 01)", "Retailer workflow (Phase 02)"])

with tab_seller:
    if st.button("Run first proposal", key="seller_run"):
        result = run_one_offer()
        st.metric("Agent instances registered", len(result["agents"]))
        st.metric("Messages sent", len(result["messages"]))
        st.info(f"Seller response: {result['decision']}")
        st.subheader("Agent characters")
        for agent in result["agents"]:
            with st.expander(f"{agent.agent_id} | {agent.role}"):
                st.write("Goal:", agent.goal)
                st.write("Strategy:", agent.strategy)
        st.subheader("Message log")
        st.json([m.model_dump(mode="json") for m in result["messages"]])

with tab_retailer:
    st.subheader("Autonomous Retailer Offer Evaluation")
    st.caption("Synthetic scenario: the retailer evaluates a received price independently. This does not send a message to the seller yet.")
    retailer_id = st.selectbox("Retailer character", ["R1", "R2"])
    offered_price = st.slider("Seller's offered price (Rs.)", 100, 220, 165, step=5)
    quantity = st.slider("Requested quantity (packets)", 1, 300, 200, step=1)
    target_price = st.slider("Retailer's preferred purchase price (Rs.)", 100, 200, 150, step=5)
    retail_price = st.slider("Expected retail selling price (Rs.)", 100, 250, 200, step=5)
    if st.button("Evaluate with Retailer LangGraph", key="retailer_run"):
        evaluation = run_retailer_offer(
            offered_price=float(offered_price),
            requested_quantity=quantity,
            target_price=float(target_price),
            expected_retail_price=float(retail_price),
            retailer_id=retailer_id,
        )
        agent = evaluation["retailer"]
        result = evaluation["result"]
        st.write(f"**Agent:** {agent.agent_id} | **Goal:** {agent.goal} | **Strategy:** {agent.strategy}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Purchase cost", f"Rs. {result['purchase_cost']:,.2f}")
        col2.metric("Expected gross profit", f"Rs. {result['expected_gross_profit']:,.2f}")
        col3.metric("Retailer budget", f"Rs. {agent.budget:,.2f}")
        st.info(f"Decision: {result['decision']}")
        if result["counter_price"] is not None:
            st.write(f"**Counter-offer:** Rs. {result['counter_price']:,.2f} per packet")
        st.write(f"**Reason:** {result['reason']}")
        with st.expander("Full LangGraph state"):
            st.json(result)
