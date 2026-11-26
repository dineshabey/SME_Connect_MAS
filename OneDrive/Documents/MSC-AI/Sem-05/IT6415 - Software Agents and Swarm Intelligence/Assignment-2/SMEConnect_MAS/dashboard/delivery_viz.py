"""Phase 04: visual, step-by-step resource and delivery coordination dashboard."""
import streamlit as st
from smeconnect.environment.marketplace import build_agents
from smeconnect.simulation.supplier_selection import run_supplier_competition
from smeconnect.simulation.reservation_ledger import ReservationLedger
from smeconnect.simulation.fulfillment import run_delivery_coordination


def render_delivery_coordination() -> None:
    st.subheader("🚚 Phase 04 · Cooperative Order & Delivery Simulation")
    st.caption("Four roles: Retailer → Seller → Delivery Agent → Coordinator. Fully synthetic; no physical orders.")
    st.info("**සිංහලෙන්:** මිලට එකඟ වුණාට පස්සේ stock, budget සහ delivery capacity තහවුරු කරලා, එකවර reserve කරන ක්‍රියාවලිය.")
    if "delivery_ledger" not in st.session_state:
        st.session_state["delivery_ledger"] = ReservationLedger.from_marketplace()
    ledger = st.session_state["delivery_ledger"]
    agents = {a.agent_id: a for a in build_agents()}
    st.markdown("### Step 1 · Current simulated resources")
    stock1, stock2, capacity = st.columns(3)
    stock1.metric("🏪 S1 unreserved stock", f"{ledger.seller_stock['S1']} packets")
    stock2.metric("🏬 S2 unreserved stock", f"{ledger.seller_stock['S2']} packets")
    capacity.metric("🚛 D1 remaining capacity", f"{ledger.delivery_capacity['D1']} packets")
    left, right = st.columns(2)
    retailer = left.selectbox("Retailer Agent", ["R1", "R2"], key="delivery_retailer")
    quantity = right.number_input("Quantity (packets)", min_value=1, max_value=300, value=100,
                                  step=10, key="delivery_quantity")
    start_price, target_price, rounds = st.columns(3)
    initial = start_price.slider("Initial offer (Rs.)",100,190,150,5,key="delivery_initial")
    target = target_price.slider("Retailer target (Rs.)",100,190,150,5,key="delivery_target")
    max_rounds = rounds.slider("Maximum negotiation rounds",1,10,5,key="delivery_rounds")
    st.caption(
        f"{retailer}: remaining budget Rs. {ledger.retailer_budget[retailer]:,.2f}; "
        f"remaining demand {ledger.retailer_demand[retailer]} packets. "
        f"Delivery D1 charges Rs. {agents['D1'].cost_per_trip:,.2f} per simulated trip."
    )
    if st.button("♻️ Reset synthetic market resources", key="delivery_reset"):
        st.session_state["delivery_ledger"] = ReservationLedger.from_marketplace()
        st.session_state.pop("delivery_result", None)
        st.rerun()
    if st.button("▶ Negotiate → Coordinate → Reserve", type="primary",
                 use_container_width=True, key="delivery_run"):
        try:
            competition = run_supplier_competition(
                retailer_id=retailer, quantity=int(quantity),
                initial_price=float(initial), retailer_target=float(target),
                max_rounds=max_rounds,
            )
            coordination = run_delivery_coordination(
                competition, ledger, quantity=int(quantity),
            )
            st.session_state["delivery_result"] = {
                "competition": competition, "coordination": coordination,
            }
        except (ValueError, RuntimeError, PermissionError) as error:
            st.session_state.pop("delivery_result", None)
            st.error(f"Simulation stopped: {error}")
    result = st.session_state.get("delivery_result")
    if not result:
        st.markdown("**Next:** Start the simulation to see each agent's actual decisions and simulated reservations.")
        return
    competition = result["competition"]
    outcome = result["coordination"]
    selected = outcome["selected_seller_id"]
    st.markdown("### Step 2 · Follow the four-agent coordination")
    st.markdown(
        """
        <style>
        .delivery-lane{background:linear-gradient(120deg,#101d38,#153e55);border:1px solid #3589a8;
          border-radius:18px;padding:19px 13px;margin:12px 0;color:#effaff}
        .delivery-nodes{display:grid;grid-template-columns:1fr auto 1fr auto 1fr auto 1fr;
          align-items:center;gap:8px}
        .delivery-node{border:1px solid #397fa4;background:#193a57;padding:14px 7px;border-radius:14px;
          text-align:center;box-shadow:inset 0 0 16px #188bea24}
        .delivery-node .symbol{font-size:29px;display:block;margin-bottom:5px}
        .delivery-node b{font-size:12px;display:block}
        .delivery-node small{font-size:10px;color:#a8d9ea}
        .delivery-arrow{font-size:23px;color:#64e4ff;text-shadow:0 0 12px #4bdbff;
          animation:delivery-beat 1.5s ease-in-out infinite}
        @keyframes delivery-beat{50%{opacity:.3;transform:translateX(3px)}}
        @media(max-width:650px){.delivery-nodes{grid-template-columns:1fr;gap:4px}
          .delivery-arrow{text-align:center;transform:rotate(90deg)}}
        @media(prefers-reduced-motion:reduce){.delivery-arrow{animation:none}}
        </style>
        <div class="delivery-lane"><div class="delivery-nodes">
          <div class="delivery-node"><span class="symbol">🛒</span><b>Retailer</b><small>Check full budget</small></div>
          <div class="delivery-arrow">➜</div>
          <div class="delivery-node"><span class="symbol">🏪</span><b>Seller</b><small>Validate stock</small></div>
          <div class="delivery-arrow">➜</div>
          <div class="delivery-node"><span class="symbol">🚚</span><b>Delivery D1</b><small>Capacity + trip fee</small></div>
          <div class="delivery-arrow">➜</div>
          <div class="delivery-node"><span class="symbol">🧭</span><b>Coordinator</b><small>All-or-none reserve</small></div>
        </div></div>
        """,
        unsafe_allow_html=True,
    )

    stages = [
        ("🛒 Retailer", "Negotiate & select"),
        ("🏪 Seller", "Confirm available stock"),
        ("🚚 Delivery D1", "Evaluate trip capacity"),
        ("🧭 Coordinator C1", "Reserve all resources"),
    ]
    cols = st.columns(4)
    for col, (name, subtitle) in zip(cols, stages):
        with col:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.caption(subtitle)
    st.markdown(f"**Selected supplier:** {selected or 'None'}")
    if outcome["status"] == "RESERVED_SIMULATED":
        st.success("✅ Simulated resources reserved together — no real purchase or delivery.")
    else:
        st.warning(f"⛔ {outcome['status']}: {outcome['reason']}")
    st.markdown("### Step 3 · Agent actions and explanations")
    for event in outcome["events"]:
        with st.container(border=True):
            st.write(f"**{event['step']}. {event['actor']} · {event['action']}**")
            st.caption(event["explanation"])
    st.markdown("### Step 4 · Reservation and cost breakdown")
    if outcome["reservation"]:
        record = outcome["reservation"]
        a, b, c = st.columns(3)
        a.metric("Agreed packet price", f"Rs. {record['unit_price']:,.2f}")
        b.metric("Delivery quote", f"Rs. {record['delivery_fee']:,.2f}")
        c.metric("Reserved order total", f"Rs. {record['reserved_total']:,.2f}")
        st.metric("Expected margin after delivery", f"Rs. {outcome['expected_margin_after_delivery']:,.2f}")
        st.json(record, expanded=False)
    else:
        st.caption("No resources were reserved. The ledger remains unchanged by this failed attempt.")
    with st.expander("🔍 Actual agent communication (FIPA-inspired messages)"):
        st.json([message.model_dump(mode="json") for message in outcome["messages"]])
        st.dataframe(outcome["events"], hide_index=True, use_container_width=True)
    st.markdown("### Step 5 · Current session reservations")
    if ledger.reservations:
        st.dataframe(ledger.reservations, hide_index=True, use_container_width=True)
    else:
        st.write("No synthetic reservations yet.")
    st.caption("Reservations live only in this Streamlit session and are resettable. "
               "Delivery is capacity-allocated, not physically dispatched or marked delivered. "
               "This sequential in-memory ledger is not safe for concurrent production orders.")
