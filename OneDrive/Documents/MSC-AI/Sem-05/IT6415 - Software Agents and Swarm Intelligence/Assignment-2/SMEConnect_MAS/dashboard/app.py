import streamlit as st
from smeconnect.simulation.engine import run_one_offer

st.set_page_config(page_title="SMEConnect AI", layout="wide")
st.title("SMEConnect AI — MAS Starter")
st.caption("A real LangGraph seller decision, not a completed marketplace simulation")
if st.button("Run first proposal"):
    result = run_one_offer()
    st.metric("Agent instances registered", len(result["agents"]))
    st.metric("Messages sent", len(result["messages"]))
    st.info(f"Seller response: {result['decision']}")
    st.subheader("Agent characters")
    for a in result["agents"]:
        with st.expander(f"{a.agent_id} | {a.role}"):
            st.write("Goal:", a.goal)
            st.write("Strategy:", a.strategy)
    st.subheader("Message log")
    st.json([m.model_dump(mode="json") for m in result["messages"]])
