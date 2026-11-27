"""Phase 04 teaching dashboard: clear outcomes first, technical evidence on demand.

Displays only outcomes returned by existing simulation and session ledger.
"""
import html
import streamlit as st

from smeconnect.environment.marketplace import build_agents
from smeconnect.simulation.supplier_selection import run_supplier_competition
from smeconnect.simulation.reservation_ledger import ReservationLedger
from smeconnect.simulation.fulfillment import run_delivery_coordination


STATUS_LABELS = {
    "RESERVED_SIMULATED": "Simulated reservation successful",
    "NO_AGREEMENT": "No supplier agreement",
    "DEMAND_EXHAUSTED": "Retailer demand already allocated",
    "STOCK_UNAVAILABLE": "Selected seller has insufficient stock",
    "DELIVERY_UNAVAILABLE": "Delivery capacity unavailable",
    "RETAILER_DECLINED": "Retailer declined total cost",
    "RESERVATION_FAILED": "Resource reservation failed",
}

ACTION_LABELS = {
    "VERIFY": "Verify selected supplier",
    "CFP": "Request delivery capacity",
    "THINK": "Evaluate rules",
    "PROPOSE": "Send delivery price quotation",
    "INFORM": "Share order information",
    "ACCEPT-PROPOSAL": "Approve proposal",
    "REJECT-PROPOSAL": "Decline proposal",
    "RESERVED": "Reserve resources",
    "STOP": "Stop safely",
}


def _resources(ledger):
    return {
        "seller_stock": dict(ledger.seller_stock),
        "retailer_budget": dict(ledger.retailer_budget),
        "retailer_demand": dict(ledger.retailer_demand),
        "delivery_capacity": dict(ledger.delivery_capacity),
    }


def _resource_view(before, after, retailer, seller, delivery):
    st.markdown("#### Resources before and after this attempt")
    rows = [
        ("Seller stock", "packets", "seller_stock", seller),
        ("Delivery capacity", "packets", "delivery_capacity", delivery),
        ("Retailer demand", "packets", "retailer_demand", retailer),
        ("Retailer budget", "Rs.", "retailer_budget", retailer),
    ]
    columns = st.columns(4)
    for column, (label, unit, key, agent) in zip(columns, rows):
        if agent is None:
            continue
        first = before[key][agent]
        last = after[key][agent]
        with column:
            st.metric(
                f"{label} · {agent}",
                f"Rs. {last:,.2f}" if unit == "Rs." else f"{last:,}",
                delta=f"{last - first:+,.2f}" if unit == "Rs." else f"{last - first:+,}",
                delta_color="off",
                help=f"Before: {first:,.2f}. After: {last:,.2f}. Values are simulated.",
            )
    st.caption("A zero change means no allocation. Resource reductions are reservations, not completed payments or deliveries.")


def _milestones(events, outcome):
    """Translate actual event evidence into four informative checkpoints."""
    actions = {(e["actor"], e["action"]) for e in events}
    seller = outcome["selected_seller_id"]
    status = outcome["status"]
    stages = [
        ("🛒", "Supplier chosen",
         bool(seller),
         f"{seller} was selected through negotiation." if seller else "No feasible supplier."),
        ("📦", "Stock checked",
         any(e["action"] == "VERIFY" for e in events) and status != "STOCK_UNAVAILABLE",
         "Coordinator checks unreserved stock." if seller else "Waiting for agreement."),
        ("🚚", "Delivery evaluated",
         ("D1", "PROPOSE") in actions,
         "D1 checked capacity and quoted a trip fee." if ("D1", "PROPOSE") in actions
         else "No accepted delivery quotation."),
        ("🧭", "Reservation committed",
         status == "RESERVED_SIMULATED",
         "Stock, demand, budget and capacity reserved." if status == "RESERVED_SIMULATED"
         else "No reservation created for this attempt."),
    ]
    st.markdown("### 2 · What happened between agents?")
    for column, (symbol, title, passed, description) in zip(st.columns(4), stages):
        with column:
            with st.container(border=True):
                st.markdown(f"### {symbol} {'✓' if passed else '–'}")
                st.markdown(f"**{title}**")
                st.caption(description)
    if status != "RESERVED_SIMULATED":
        st.caption("Checkpoints show observed events, not a guarantee that every stage succeeded.")


def _readable_events(events):
    with st.expander("📖 Explore the actual agent decisions (step by step)", expanded=False):
        if not events:
            st.write("No coordination events recorded.")
        for event in events:
            actor = event["actor"]
            label = ACTION_LABELS.get(event["action"], event["action"])
            st.markdown(f"**{event['step']}. {actor} — {label}**")
            st.caption(event["explanation"])
        st.caption("THINK describes an implemented rule check; it is not hidden LLM reasoning.")


def render_delivery_coordination() -> None:
    st.subheader("🚚 Phase 04 · Delivery Coordination Lab")
    st.caption("Negotiate a supplier agreement, evaluate delivery, and reserve simulated resources — step by step.")

    if "delivery_ledger" not in st.session_state:
        st.session_state["delivery_ledger"] = ReservationLedger.from_marketplace()
    ledger = st.session_state["delivery_ledger"]
    agents = {agent.agent_id: agent for agent in build_agents()}

    # Put the outcome and explanation at the top on subsequent Streamlit reruns.
    result = st.session_state.get("delivery_result")
    if result:
        outcome = result["coordination"]
        title = STATUS_LABELS.get(outcome["status"], outcome["status"])
        if outcome["status"] == "RESERVED_SIMULATED":
            st.success(f"✅ {title} · Seller {outcome['selected_seller_id']} · Order {outcome['order_id']}")
        else:
            st.warning(f"⚠️ {title} — {outcome['reason']}")
        st.caption("This is an in-memory academic simulation. No physical shipment or payment occurs.")

    st.markdown("### 1 · Configure the order")
    col_a, col_b, col_c = st.columns([1, 1, 1])
    retailer = col_a.selectbox("🛒 Retailer", ["R1", "R2"], key="delivery_retailer")
    quantity = col_b.number_input(
        "📦 Requested packets", min_value=1, max_value=300,
        value=200, step=10, key="delivery_quantity",
    )
    remaining_budget = ledger.retailer_budget[retailer]
    remaining_demand = ledger.retailer_demand[retailer]
    col_c.metric("🚚 D1 trip fee", f"Rs. {agents['D1'].cost_per_trip:,.0f}")
    st.caption(
        f"Available to {retailer}: **{remaining_demand} packets** of demand, "
        f"**Rs. {remaining_budget:,.2f}** budget. "
        f"Seller stock: S1 **{ledger.seller_stock['S1']}**, "
        f"S2 **{ledger.seller_stock['S2']}** packets. "
        f"Delivery capacity: **{ledger.delivery_capacity['D1']}** packets."
    )
    with st.expander("⚙️ Negotiation settings", expanded=False):
        p, t, r = st.columns(3)
        initial = p.slider("Starting offer · Rs./packet", 100, 190, 150, 5, key="delivery_initial")
        target = t.slider("Preferred buying price · Rs./packet", 100, 190, 150, 5, key="delivery_target")
        max_rounds = r.slider("Maximum negotiation rounds", 1, 10, 5, key="delivery_rounds")
        st.caption("Starting offer is operator-supplied. Agents negotiate autonomously afterward.")

    primary, reset = st.columns([3, 1])
    with primary:
        execute = st.button(
            "▶ Run Negotiation & Delivery Simulation", type="primary",
            use_container_width=True, key="delivery_run",
        )
    with reset:
        restart = st.button("↺ Reset market", key="delivery_reset", use_container_width=True)
    if restart:
        st.session_state["delivery_ledger"] = ReservationLedger.from_marketplace()
        st.session_state.pop("delivery_result", None)
        st.rerun()

    if execute:
        before = _resources(ledger)
        try:
            competition = run_supplier_competition(
                retailer_id=retailer, quantity=int(quantity),
                initial_price=float(initial), retailer_target=float(target),
                max_rounds=max_rounds,
            )
            coordination = run_delivery_coordination(competition, ledger, quantity=int(quantity))
            st.session_state["delivery_result"] = {
                "competition": competition,
                "coordination": coordination,
                "before": before,
                "after": _resources(ledger),
                "request": {"retailer": retailer, "quantity": int(quantity)},
            }
            st.rerun()
        except (ValueError, RuntimeError, PermissionError) as exc:
            st.session_state.pop("delivery_result", None)
            st.error(f"Simulation stopped: {exc}")

    result = st.session_state.get("delivery_result")
    if not result:
        st.info("Choose an order and press **Run Negotiation & Delivery Simulation**. The result and explanation will appear here.")
        return

    outcome = result["coordination"]
    selection = result["competition"]["selection"]
    _milestones(outcome["events"], outcome)

    st.markdown("### 3 · Supplier and financial decision")
    l, r = st.columns([1, 1.2])
    with l:
        with st.container(border=True):
            st.markdown("**🏆 Retailer's selected supplier**")
            if selection["selected_seller_id"]:
                st.markdown(f"### Seller {selection['selected_seller_id']}")
                st.metric("Agreed price per packet", f"Rs. {selection['selected_price']:,.2f}")
                st.caption(selection["reasoning"])
            else:
                st.write("No supplier was selected.")
                st.caption(selection["reasoning"])
    with r:
        with st.container(border=True):
            st.markdown("**💳 Cost breakdown**")
            reservation = outcome["reservation"]
            fee = outcome["delivery_fee"]
            if selection["selected_price"] is not None:
                qty = result["request"]["quantity"]
                purchase = round(selection["selected_price"] * qty, 2)
                st.write(f"Packets: **{qty}** × Rs. {selection['selected_price']:,.2f}")
                st.write(f"Purchase cost: **Rs. {purchase:,.2f}**")
                st.write(f"Delivery quotation: **Rs. {fee:,.2f}**" if fee is not None
                         else "Delivery quotation: **Not available**")
                if reservation:
                    st.metric("Total reserved (purchase + delivery)", f"Rs. {reservation['reserved_total']:,.2f}")
                    st.metric("Expected margin after delivery", f"Rs. {outcome['expected_margin_after_delivery']:,.2f}")
                else:
                    st.caption("Not reserved. These are proposal amounts, not a charged total.")
            else:
                st.write("No agreed purchase cost.")

    if "before" in result and "after" in result:
        _resource_view(
            result["before"], result["after"],
            result["request"]["retailer"], outcome["selected_seller_id"], outcome["delivery_id"],
        )

    _readable_events(outcome["events"])
    with st.expander("🔬 Technical evidence · structured messages, raw state and IDs"):
        st.caption("FIPA-inspired communication generated by the actual simulation. No fabricated agent messages.")
        st.json([msg.model_dump(mode="json") for msg in outcome["messages"]], expanded=False)
        st.dataframe(outcome["events"], hide_index=True, use_container_width=True)
        st.json({
            "conversation_id": outcome["conversation_id"],
            "order_id": outcome["order_id"],
            "status": outcome["status"],
            "reservation": outcome["reservation"],
        }, expanded=False)

    st.markdown("### 4 · Simulated reservation history")
    if ledger.reservations:
        summary = [
            {
                "Order": row["order_id"], "Seller": row["seller_id"],
                "Retailer": row["retailer_id"], "Delivery": row["delivery_id"],
                "Packets": row["quantity"], "Total (Rs.)": row["reserved_total"],
                "Status": "Reserved (simulation)",
            }
            for row in ledger.reservations
        ]
        st.dataframe(summary, hide_index=True, use_container_width=True)
    else:
        st.caption("No simulated reservations yet.")

    st.caption("The ledger is limited to this Streamlit session and sequential simulation. "
               "No real order fulfillment, payment, dispatched delivery, or persistent stock update.")
