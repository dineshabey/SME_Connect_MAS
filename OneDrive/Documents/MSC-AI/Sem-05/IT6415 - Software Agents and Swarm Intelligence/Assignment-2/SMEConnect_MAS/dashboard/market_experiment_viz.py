"""Phase 05.1: guided market-shock comparison with actual agent outcomes."""
import streamlit as st

from smeconnect.environment.market_state import SCENARIO_NAMES
from smeconnect.simulation.market_experiment import run_market_experiment


def render_market_experiment() -> None:
    st.subheader("📈 Phase 05 · Market Changes & Agent Adaptation")
    st.caption("Compare two actual LangGraph negotiations under controlled synthetic market conditions.")
    st.info("**සිංහලෙන්:** Market එක වෙනස් කළාම Seller සහ Retailer Agents තමන්ගේ rules අනුව අලුත් තීරණ ගන්නේ කොහොමද බලමු.")
    st.markdown("### 1 · Choose a market event")
    scenarios = [key for key in SCENARIO_NAMES if key != "normal"]
    event = st.selectbox(
        "Market shock", scenarios, format_func=lambda key: SCENARIO_NAMES[key],
        key="market5_scenario",
    )
    explanatory = {
        "s2_shortage": "Seller S2's available stock drops from 300 to 100 packets. "
                       "A 200-packet order can no longer be served by S2.",
        "price_pressure": "A synthetic input-cost shock raises S2's private pricing "
                          "limits. Its minimum price is never published to the retailer.",
        "demand_surge": "Retailer R1's demand increases from 200 to 240 packets. "
                        "This change may not alter the winner for a 200-packet order.",
    }
    st.caption(explanatory[event])
    left, middle, right = st.columns(3)
    retailer = left.selectbox("Retailer", ["R1", "R2"], key="market5_retailer")
    quantity = middle.number_input(
        "Packets (comparable across scenarios)", 1, 200 if retailer == "R1" else 150,
        200 if retailer == "R1" else 150, step=10, key="market5_qty",
    )
    initial = right.slider("Initial offer (Rs.)", 100, 190, 150, 5, key="market5_initial")
    with st.expander("Advanced negotiation settings"):
        target = st.slider("Retailer target (Rs.)", 100, 190, 150, 5, key="market5_target")
        rounds = st.slider("Maximum rounds", 1, 10, 5, key="market5_rounds")
    if st.button("▶ Run before / after experiment", type="primary",
                 use_container_width=True, key="market5_run"):
        try:
            result = run_market_experiment(
                scenario=event, retailer_id=retailer, quantity=int(quantity),
                initial_price=float(initial), retailer_target=float(target),
                max_rounds=rounds,
            )
            st.session_state["market5_result"] = result
        except (ValueError, RuntimeError, PermissionError) as exc:
            st.session_state.pop("market5_result", None)
            st.error(f"Experiment could not run: {exc}")
    result = st.session_state.get("market5_result")
    if result is None:
        st.write("Select a shock and run the comparison. Both runs start from independent snapshots.")
        return
    st.markdown(f"### 2 · Market Agent M1 reports: {result['market_signal']['signal']}")
    st.write(result["market_signal"]["summary"])
    st.caption("Market signal is a typed public observation. No seller's private minimum price is included.")
    st.markdown("### 3 · Market state before and after")
    baseline = result["observable_state"]["before"]
    changed = result["observable_state"]["after"]
    labels = {"stock_S1": "S1 stock (packets)",
              "stock_S2": "S2 stock (packets)",
              "demand_R1": "R1 demand (packets)"}
    st.dataframe(
        [{"Resource": labels[k], "Normal": baseline[k], "Changed": changed[k],
          "Difference": changed[k] - baseline[k]} for k in labels],
        use_container_width=True, hide_index=True,
    )
    st.markdown("### 4 · What did agents decide?")
    before, after = st.columns(2)
    for col, label, payload in (
        (before, "Before · Normal market", result["before"]),
        (after, f"After · {result['scenario_name']}", result["after"]),
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"**{label}**")
                selected = payload["selected_seller"]
                st.markdown(f"### {'🏆 ' + selected if selected else 'No supplier'}")
                st.metric("Negotiated unit price",
                          f"Rs. {payload['agreed_price']:,.2f}"
                          if payload["agreed_price"] is not None else "No agreement")
                st.metric("Expected gross profit", f"Rs. {payload['expected_gross_profit']:,.2f}")
                st.caption("Provisional price only; no simulated order booked.")
    if result["before"]["selected_seller"] != result["after"]["selected_seller"]:
        st.success("Supplier selection changed because agents evaluated the new market constraints.")
    else:
        st.info("The selected supplier did not change. Adaptation does not always mean a different winner.")
    st.markdown("### 5 · Compare actual negotiation outcomes")
    table = []
    for seller_id in sorted({r["seller_id"] for r in result["before"]["offers"]}):
        prev = next(r for r in result["before"]["offers"] if r["seller_id"] == seller_id)
        later = next(r for r in result["after"]["offers"] if r["seller_id"] == seller_id)
        table.append({
            "Seller": seller_id,
            "Normal status": prev["status"], "Normal price (Rs.)": prev["price"],
            "Changed status": later["status"], "Changed price (Rs.)": later["price"],
        })
    st.dataframe(table, use_container_width=True, hide_index=True)
    with st.expander("🔍 Academic evidence · message bus and negotiation events"):
        st.markdown("**Market Agent M1 → Retailer typed signal**")
        st.json([msg.model_dump(mode="json") for msg in result["signal_messages"]])
        for name in ("baseline", "changed"):
            st.markdown(f"**{name.title()} negotiated messages**")
            for seller_id, negotiation in result[name]["negotiations"].items():
                st.markdown(f"Seller {seller_id}: {negotiation['status']}")
                st.dataframe(negotiation["timeline"], hide_index=True,
                             use_container_width=True)
    st.caption("This is controlled rule-based response to changed inputs, not machine-learned online adaptation, "
               "emergent self-organization, or real-time market sensing.")
