"""English-only guided MSc viva presentation driven by authentic MAS data.

No timers, fabricated events, real orders, or external network calls.
"""
import html

import streamlit as st

from smeconnect.environment.marketplace import build_agents
from smeconnect.environment.catalogue import public_listings
from smeconnect.simulation.supplier_selection import run_supplier_competition
from smeconnect.simulation.reservation_ledger import ReservationLedger
from smeconnect.simulation.fulfillment import run_delivery_coordination
from smeconnect.simulation.market_experiment import run_market_experiment
from smeconnect.simulation.experiment_evaluation import run_experiment_batch

STEPS = (
    ("Architecture", "Full multi-agent architecture", "System architecture, autonomy and observable communication"),
    ("Sellers", "Meet the two seller agents", "Distinct goals, strategies, public offers and available stock"),
    ("Retailer", "Meet retailer R1", "Buyer goal, purchasing budget and decision constraints"),
    ("Discovery", "Discover available suppliers", "Coordinator-assisted discovery and public information"),
    ("Negotiation", "Replay actual negotiations", "PROPOSE, ACCEPT-PROPOSAL and REJECT-PROPOSAL"),
    ("Selection", "Retailer selects the supplier", "Compare negotiated prices, feasibility and expected gross profit"),
    ("Delivery", "Cooperate on delivery", "Capacity request, quotation and retailer approval"),
    ("Reservation", "Reserve simulated resources", "All-or-none allocation and repeated-booking rejection"),
    ("Adaptation", "Respond to a market shock", "Independent agent decisions under changed synthetic inputs"),
    ("Evaluation", "Evaluate MAS characteristics", "Measured paired trials, trace evidence and limitations"),
)

VIVA_CSS = """
<style>
.viva-progress{display:flex;gap:5px;margin:10px 0 18px}
.viva-progress span{height:9px;flex:1;border-radius:9px;background:#284153}
.viva-progress span.on{background:#58d5bc}
.viva-kicker{color:#77e7cf;font-size:16px;font-weight:850;letter-spacing:.11em;text-transform:uppercase}
.viva-explain{background:linear-gradient(110deg,#172c41,#153d46);border:1px solid #3a7181;
   border-radius:17px;padding:20px 24px;margin:16px 0 22px;font-size:19px;line-height:1.6}
.viva-explain b{color:#abf4dc}
.viva-entity-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;margin:14px 0}
.viva-entity{background:linear-gradient(140deg,#18344b,#215569);border:1px solid #488fa7;
    border-radius:18px;padding:24px;min-height:195px;box-shadow:0 10px 28px #040d1b55}
.viva-entity.retailer{background:linear-gradient(140deg,#1c3059,#274c7e)}
.viva-entity h3{color:white;font-size:27px!important;margin:0 0 8px!important}
.viva-entity p{font-size:19px!important;color:#d7eaf3}
.viva-stat{font-size:28px;font-weight:800;color:white}
.viva-muted{font-size:16px!important;color:#b8d2df}
.viva-network{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px;
   border:1px solid #39657a;border-radius:18px;padding:24px;background:linear-gradient(125deg,#11263b,#143d4d)}
.viva-node{text-align:center;padding:22px 12px;border:1px solid #4389a0;border-radius:13px;
  background:#20435b;color:white;font-size:19px;font-weight:750}
.viva-node small{display:block;color:#cce1ec;font-size:15px;font-weight:400;margin-top:5px}
.viva-connector{grid-column:1/-1;text-align:center;color:#8ef0dc;font-size:17px;font-weight:800}
.viva-focus{background:#174944;border-color:#60d4b8}
.viva-seller{background:#245068}
.viva-retailer{background:#2b4777}
.viva-support{background:#383c64}
.viva-mini{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.viva-mini div{border:1px solid #466a80;border-radius:12px;background:#1b3044;text-align:center;padding:15px}
.viva-mini b{font-size:20px;color:#fff}
.viva-mini small{display:block;font-size:14px;color:#c1d8e3}
@media(max-width:850px){.viva-entity-grid,.viva-network{grid-template-columns:1fr}
 .viva-node,.viva-connector{grid-column:1/-1}
 .viva-mini{grid-template-columns:1fr}}
</style>
"""


def _escape(value):
    return html.escape(str(value), quote=True)


def _say(what: str, why: str, mas: str):
    st.markdown(
        '<div class="viva-explain">'
        '<b>What is happening?</b> ' + _escape(what) + '<br>'
        '<b>Why?</b> ' + _escape(why) + '<br>'
        '<b>MAS evidence:</b> ' + _escape(mas) +
        '</div>', unsafe_allow_html=True,
    )


def _architecture():
    st.markdown(
        '<div class="viva-network">'
        '<div class="viva-node viva-seller">🏪 Seller S1<small>Margin policy</small></div>'
        '<div class="viva-node viva-focus">🛒 Retailer R1<small>Price and supplier choice</small></div>'
        '<div class="viva-node viva-seller">📦 Seller S2<small>Volume policy</small></div>'
        '<div class="viva-connector">↕ Independent PROPOSE / ACCEPT / REJECT conversations ↕</div>'
        '<div class="viva-node viva-retailer">🛍️ Retailer R2<small>Other independent buyer</small></div>'
        '<div class="viva-node viva-support">🧭 Coordinator C1<small>Discovery and reservations</small></div>'
        '<div class="viva-node viva-support">🚚 Delivery D1<small>Capacity and fee</small></div>'
        '<div class="viva-connector">Typed Pydantic messages · In-memory message bus</div>'
        '<div class="viva-node viva-support">📡 Market M1<small>Synthetic change signal</small></div>'
        '<div class="viva-node">🧠 LangGraph<small>Per-agent decision workflows</small></div>'
        '<div class="viva-node">🗂️ Reservation ledger<small>Session-only allocations</small></div>'
        '</div>', unsafe_allow_html=True,
    )
    st.caption(
        "Conceptual component architecture, not a live packet trace. "
        "Agents own their decision rules; one local Python process schedules their turns."
    )
    with st.expander("Why LangGraph rather than NetLogo or SPADE?"):
        st.write(
            "NetLogo is well suited to agent-based population simulations; SPADE supports "
            "message-oriented agent behaviours over XMPP. This implementation uses "
            "LangGraph to inspect stateful decision paths and a validated in-memory "
            "message bus to study negotiation and coordination. It does not claim "
            "distributed execution or learned agent policies."
        )
    _say(
        "Seven agents with different responsibilities interact through validated messages.",
        "A marketplace has stakeholders with different goals and constraints.",
        "Agent heterogeneity, autonomy, message exchange and coordination.",
    )


def _agents():
    return {a.agent_id: a for a in build_agents()}


def _sellers():
    listings = {row.seller_id: row for row in public_listings()}
    agents = _agents()
    boxes = ['<div class="viva-entity-grid">']
    for sid, symbol in (("S1", "🏪"), ("S2", "📦")):
        seller, listing = agents[sid], listings[sid]
        boxes.append(
            '<div class="viva-entity">'
            f'<h3>{symbol} Seller {sid}</h3>'
            f'<p>Goal: {_escape(seller.goal)}<br>Strategy: {_escape(listing.seller_strategy)}</p>'
            f'<div class="viva-stat">Rs. {listing.listed_price:,.2f}</div>'
            '<div class="viva-muted">Public asking price · per 100g packet</div>'
            f'<div class="viva-stat">{listing.advertised_stock} packets</div>'
            '<div class="viva-muted">Advertised synthetic stock</div></div>'
        )
    boxes.append("</div>")
    st.markdown("".join(boxes), unsafe_allow_html=True)
    st.info(
        "Public asking price is NOT an agreed negotiation price. "
        "Seller minimum and target prices are private decision constraints and "
        "are intentionally not disclosed as retailer-visible data."
    )
    _say(
        "Two autonomous sellers publish different public offers and stock availability.",
        "S1 prioritizes margin while S2 prioritizes volume; they need not respond identically.",
        "Heterogeneous goals, autonomy and private knowledge boundaries.",
    )


def _retailer():
    buyer = _agents()["R1"]
    st.markdown(
        '<div class="viva-entity-grid"><div class="viva-entity retailer">'
        '<h3>🛒 Retailer R1</h3>'
        f'<p>Goal: {_escape(buyer.goal)}<br>Strategy: {_escape(buyer.strategy)}</p>'
        f'<div class="viva-stat">Rs. {buyer.budget:,.2f}</div>'
        '<div class="viva-muted">Synthetic available budget</div></div>'
        '<div class="viva-entity retailer"><h3>Order constraints</h3>'
        f'<div class="viva-stat">{buyer.demand} packets</div>'
        '<div class="viva-muted">Total baseline demand</div>'
        f'<div class="viva-stat">Rs. {buyer.maximum_price:,.2f}</div>'
        '<div class="viva-muted">Maximum unit buying price</div></div></div>',
        unsafe_allow_html=True,
    )
    st.caption("The demo uses an assumed resale price of Rs.200 per packet to calculate expected gross profit.")
    _say(
        "R1 searches for the most favorable feasible purchase terms.",
        "Price alone is insufficient: quantity, budget, price limit and expected margin matter.",
        "Goal-oriented rational decisions and local constraints.",
    )


def _discovery():
    listings = public_listings()
    st.dataframe([
        {"Seller": row.seller_id, "Product": row.product_name,
         "Public asking price (Rs.)": row.listed_price,
         "Advertised stock": row.advertised_stock, "Strategy": row.seller_strategy}
        for row in listings
    ], hide_index=True, use_container_width=True)
    agents = _agents()
    sellers = agents["C1"].discover_sellers(list(agents.values()))
    st.info("Discovered seller IDs: " + ", ".join(sellers))
    _say(
        "The coordinator discovers registered seller agents; public listings supply visible product information.",
        "Discovery identifies candidates without the coordinator deciding the retailer's final choice.",
        "Discovery, structured public information and separation of agent responsibilities.",
    )


def _get_competition():
    return st.session_state.get("viva_competition")


def _run_competition():
    st.session_state["viva_competition"] = run_supplier_competition(
        retailer_id="R1", quantity=200, initial_price=150.0,
        retailer_target=150.0, max_rounds=5,
    )
    st.session_state["viva_message_step"] = 0
    # Each new competition establishes a new story; old reservations are cleared.
    st.session_state["viva_ledger"] = ReservationLedger.from_marketplace()
    st.session_state.pop("viva_delivery", None)
    st.session_state.pop("viva_delivery_repeat", None)


def _competition_button():
    if st.button("▶ Run actual S1 / S2 negotiations", type="primary",
                 key="viva_run_competition", use_container_width=True):
        try:
            _run_competition()
        except (ValueError, RuntimeError) as exc:
            st.error(f"Negotiation failed: {exc}")
    return _get_competition()


def _negotiation():
    result = _competition_button()
    if not result:
        st.info("Run the competition to generate genuine message traces.")
        return
    seller = st.selectbox("Conversation to replay", ["S1", "S2"], key="viva_seller_filter")
    events = result["negotiations"][seller]["timeline"]
    if not events:
        st.info("No messages were recorded.")
        return
    index = min(int(st.session_state.get("viva_message_step", 0)), len(events) - 1)
    st.session_state["viva_message_step"] = index
    selected = events[index]
    st.progress((index + 1) / len(events),
                text=f"Recorded message {index+1} of {len(events)}")
    with st.container(border=True):
        st.markdown(f"### {_escape(selected['sender'])} → {_escape(selected['receiver'])}")
        st.metric("Message performative", selected["performative"])
        st.metric("Proposed packet price", f"Rs. {selected['price']:,.2f}")
        st.write("**Decision explanation:** " + selected["reason"])
        st.caption(f"Negotiation round {selected['round']} · authentic recorded event")
    left, right = st.columns(2)
    if left.button("← Previous message", disabled=index == 0, key="viva_msg_back"):
        st.session_state["viva_message_step"] = index-1
        st.rerun()
    if right.button("Next message →", disabled=index == len(events)-1, key="viva_msg_next"):
        st.session_state["viva_message_step"] = index+1
        st.rerun()
    with st.expander("Technical evidence · complete recorded conversation"):
        st.dataframe(events, hide_index=True, use_container_width=True)
        st.json([m.model_dump(mode="json") for m in result["negotiations"][seller]["messages"]])
    _say(
        "R1 and a seller exchange actual price proposals, responses and reasoned rule checks.",
        "Seller and retailer decisions are independently calculated from their respective constraints.",
        "Autonomy, validated social communication, negotiation and traceability.",
    )


def _selection():
    result = _get_competition()
    if not result:
        st.info("Step 05 must run the negotiations before supplier selection can be shown.")
        result = _competition_button()
        if not result:
            return
    choice = result["selection"]
    st.dataframe(choice["evaluations"], hide_index=True, use_container_width=True)
    if choice["selected_seller_id"]:
        st.success(
            f"Retailer R1 selected {choice['selected_seller_id']} at "
            f"Rs. {choice['selected_price']:,.2f} per packet. "
            f"Expected gross profit: Rs. {choice['expected_gross_profit']:,.2f}."
        )
    else:
        st.warning("No eligible negotiated supplier was selected.")
    st.write("**Actual retailer decision:** " + choice["reasoning"])
    st.caption("Supplier selection is provisional. It does not deduct stock, budget or delivery capacity.")
    _say(
        "R1 compares feasible negotiated agreements, then chooses a supplier.",
        "The retailer, not the coordinator, owns the supplier-selection policy.",
        "Rational utility evaluation and independent agent decision ownership.",
    )


def _get_ledger():
    if "viva_ledger" not in st.session_state:
        st.session_state["viva_ledger"] = ReservationLedger.from_marketplace()
    return st.session_state["viva_ledger"]


def _run_delivery(*, repeat=False):
    competition = _get_competition()
    if not competition:
        raise ValueError("Run supplier negotiation before delivery coordination.")
    return run_delivery_coordination(competition, _get_ledger(), quantity=200)


def _delivery():
    competition = _get_competition()
    if not competition:
        st.info("Complete the negotiation step first.")
        return
    if st.button("▶ Request delivery and retailer approval", key="viva_delivery_run", type="primary"):
        try:
            st.session_state["viva_delivery"] = _run_delivery()
        except (ValueError, RuntimeError) as exc:
            st.error(f"Delivery coordination failed: {exc}")
    outcome = st.session_state.get("viva_delivery")
    if not outcome:
        st.info("Run delivery coordination to reveal the recorded D1 and R1 decisions.")
        return
    st.markdown("### Recorded coordination actions")
    st.dataframe(outcome["events"], hide_index=True, use_container_width=True)
    st.write("**Outcome:** " + outcome["status"] + " — " + outcome["reason"])
    if outcome["delivery_fee"] is not None:
        st.metric("Delivery quote", f"Rs. {outcome['delivery_fee']:,.2f}")
    with st.expander("Validated inter-agent messages"):
        st.json([m.model_dump(mode="json") for m in outcome["messages"]])
    _say(
        "D1 checks capacity, quotes a trip, and R1 independently evaluates the full commitment.",
        "Approval depends on delivery capacity, price, retailer budget and demand.",
        "Cooperation, coordination and independent decision workflows.",
    )


def _reservation():
    outcome = st.session_state.get("viva_delivery")
    ledger = _get_ledger()
    if not outcome:
        st.info("Run the delivery-coordination step to create the first simulated reservation.")
        return
    if outcome["status"] == "RESERVED_SIMULATED":
        reservation = outcome["reservation"]
        st.success("RESERVED_SIMULATED — all resources reserved in this session.")
        st.dataframe([reservation], use_container_width=True, hide_index=True)
    else:
        st.warning(outcome["status"] + ": " + outcome["reason"])
    st.markdown("#### Remaining synthetic resources")
    st.dataframe([
        {"Resource": "S2 stock", "Remaining": ledger.seller_stock["S2"], "Units": "packets"},
        {"Resource": "R1 demand", "Remaining": ledger.retailer_demand["R1"], "Units": "packets"},
        {"Resource": "R1 budget", "Remaining": ledger.retailer_budget["R1"], "Units": "Rs."},
        {"Resource": "D1 delivery", "Remaining": ledger.delivery_capacity["D1"], "Units": "packets"},
    ], hide_index=True, use_container_width=True)
    if st.button("▶ Retry the same order without resetting", key="viva_repeat"):
        try:
            st.session_state["viva_delivery_repeat"] = _run_delivery(repeat=True)
        except (ValueError, RuntimeError) as exc:
            st.error(f"Retry failed: {exc}")
    repeat = st.session_state.get("viva_delivery_repeat")
    if repeat:
        st.info("Repeated attempt: " + repeat["status"] + " — " + repeat["reason"])
    st.caption("In-memory sequential reservation only. No real purchase, financial charge or delivery.")
    _say(
        "The coordinator validates inventory, demand, budget and capacity before reserving.",
        "An infeasible duplicate allocation must be rejected instead of silently committed.",
        "Coordinated resource allocation, constraint handling and observable failures.",
    )


def _adaptation():
    if st.button("▶ Compare normal vs S2 stock-shortage market", type="primary", key="viva_adapt_run"):
        try:
            st.session_state["viva_market"] = run_market_experiment(
                scenario="s2_shortage", retailer_id="R1", quantity=200,
                initial_price=150.0, retailer_target=150.0, max_rounds=5,
            )
        except (ValueError, RuntimeError) as exc:
            st.error(f"Market experiment failed: {exc}")
    result = st.session_state.get("viva_market")
    if not result:
        st.info("Run the before-and-after scenario to see actual changes in agent decisions.")
        return
    a, b = st.columns(2)
    for col, name, data in ((a, "Normal market", result["before"]),
                            (b, "After stock shortage", result["after"])):
        with col:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.metric("Chosen supplier", data["selected_seller"] or "None")
                st.metric("Agreed price", f"Rs. {data['agreed_price']:,.2f}"
                          if data["agreed_price"] is not None else "No agreement")
                st.metric("Expected gross profit", f"Rs. {data['expected_gross_profit']:,.2f}")
    st.dataframe([
        {"Condition": "S2 stock", "Normal": result["observable_state"]["before"]["stock_S2"],
         "After shortage": result["observable_state"]["after"]["stock_S2"]},
    ], hide_index=True, use_container_width=True)
    st.info("Market M1: " + result["market_signal"]["summary"])
    _say(
        "An input market condition changes, and the same seller/retailer policies are evaluated again.",
        "The system must respond to availability rather than forcing a fixed winning supplier.",
        "Reactive rule-based adaptation; this is not online policy learning.",
    )


def _evaluation():
    if st.button("▶ Run reproducible experiment grid", type="primary", key="viva_eval_run"):
        try:
            st.session_state["viva_evaluation"] = run_experiment_batch()
        except (ValueError, RuntimeError) as exc:
            st.error(f"Evaluation failed: {exc}")
    result = st.session_state.get("viva_evaluation")
    if not result:
        st.info("Run the actual batch evaluation to calculate metrics instead of displaying invented values.")
    else:
        config = result["config"]
        a, b, c = st.columns(3)
        a.metric("Paired trials", config["paired_trials"])
        b.metric("Marketplace runs", config["snapshot_runs"])
        c.metric("Supplier switches", sum(row["supplier_switches"] for row in result["summary"]))
        st.dataframe([
            {"Scenario": row["scenario_name"],
             "Trials": row["paired_trials"],
             "Supplier switches": row["supplier_switches"],
             "Switch rate (%)": row["supplier_switch_rate_pct"],
             "Normal expected gross profit (Rs.)": row["normal"]["mean_expected_gross_profit_rs"],
             "Changed expected gross profit (Rs.)": row["changed"]["mean_expected_gross_profit_rs"]}
            for row in result["summary"]
        ], hide_index=True, use_container_width=True)
    st.markdown("### MAS features supported by implementation evidence")
    st.dataframe([
        {"Feature": "Autonomy", "Evidence": "Separate LangGraph seller and retailer policies"},
        {"Feature": "Communication", "Evidence": "Pydantic-validated message bus"},
        {"Feature": "Competition", "Evidence": "Independent bilateral seller negotiations"},
        {"Feature": "Cooperation", "Evidence": "D1 delivery quote and R1 approval"},
        {"Feature": "Coordination", "Evidence": "C1 all-or-none session resource reservation"},
        {"Feature": "Reactivity", "Evidence": "Recomputed choices under synthetic market snapshots"},
    ], hide_index=True, use_container_width=True)
    st.caption(
        "LangGraph is a stateful workflow library. This example executes agents sequentially "
        "within one Python process; NetLogo and SPADE address different agent simulation "
        "and communication needs. No real SMEs, distributed deployment, or learned policy."
    )


RENDER = (_architecture, _sellers, _retailer, _discovery, _negotiation,
          _selection, _delivery, _reservation, _adaptation, _evaluation)


def _set_step(value: int):
    st.session_state["viva_step"] = max(0, min(value, len(STEPS)-1))


def render_viva_mode():
    st.markdown(VIVA_CSS, unsafe_allow_html=True)
    st.session_state.setdefault("viva_step", 0)
    index = st.session_state["viva_step"]
    st.markdown('<div class="viva-kicker">Guided MSc demonstration · English only</div>',
                unsafe_allow_html=True)
    st.markdown(f"## Step {index + 1:02d} / {len(STEPS)} — {STEPS[index][1]}")
    st.caption(STEPS[index][2])
    st.markdown(
        '<div class="viva-progress">' +
        "".join('<span class="' + ("on" if i <= index else "") + '"></span>'
                for i in range(len(STEPS))) + '</div>',
        unsafe_allow_html=True,
    )
    with st.expander("Jump to a presentation step", expanded=False):
        chosen = st.selectbox("Section", range(len(STEPS)),
                              format_func=lambda i: f"{i+1:02d} · {STEPS[i][1]}",
                              index=index, key="viva_jump")
        if st.button("Go to section", key="viva_jump_go"):
            _set_step(chosen)
            st.rerun()

    RENDER[index]()
    st.divider()
    back, current, forward = st.columns([1, 1.2, 1])
    with back:
        st.button("← Previous step", disabled=index == 0, key="viva_previous",
                  on_click=_set_step, args=(index - 1,), use_container_width=True)
    with current:
        st.caption("Presenter navigation · no scripted or fake agent replies.")
    with forward:
        st.button("Next step →", disabled=index == len(STEPS)-1,
                  key="viva_next", type="primary",
                  on_click=_set_step, args=(index + 1,), use_container_width=True)
