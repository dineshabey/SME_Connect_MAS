"""Interactive full-workflow presentation, replaying real MAS execution evidence.

One user click performs a *fresh, isolated synthetic* computation; subsequent
navigation/animation merely replays recorded events, without re-reserving stock.
"""
from __future__ import annotations

from html import escape
import time

import streamlit as st

from dashboard.negotiation_viz import neon_scene
from smeconnect.environment.marketplace import build_agents
from smeconnect.environment.catalogue import public_listings
from smeconnect.simulation.supplier_selection import run_supplier_competition
from smeconnect.simulation.fulfillment import run_delivery_coordination
from smeconnect.simulation.reservation_ledger import ReservationLedger


WORKFLOW_CSS = """
<style>
.wf-top{padding:20px 25px;background:linear-gradient(115deg,#142e43,#155765);
border:1px solid #468594;border-radius:18px;margin-bottom:21px}
.wf-top strong{color:white;font-size:30px}
.wf-top p{color:#d4eaf2;font-size:20px!important;margin:6px 0 0}
.wf-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:16px 0}
.wf-card{border:1px solid #438ba3;border-radius:16px;padding:24px;
background:linear-gradient(145deg,#16334c,#225368);min-height:175px}
.wf-card.retailer{background:linear-gradient(145deg,#25365e,#2d5984)}
.wf-card.delivery{background:linear-gradient(145deg,#3c305e,#554779)}
.wf-card .name{font-size:25px;font-weight:850;color:#fff}
.wf-card .details{font-size:19px;color:#d5ecf4;line-height:1.6;margin-top:9px}
.wf-stage{background:linear-gradient(135deg,#10243d,#153c56);
 border:1px solid #397c97;border-radius:22px;padding:28px;
 box-shadow:0 15px 38px #0005;min-height:345px}
.wf-stage-head{font-size:17px;letter-spacing:.09em;font-weight:850;color:#90f4df}
.wf-stage-title{font-size:31px;font-weight:850;color:#fff;margin:9px 0}
.wf-stage-copy{font-size:23px;color:#e3f4fc;line-height:1.6}
.wf-route{display:flex;align-items:center;justify-content:center;gap:22px;flex-wrap:wrap;
 margin:24px 0 22px}
.wf-person{min-width:160px;max-width:340px;flex:1;text-align:center;border:1px solid #5da5be;
 border-radius:16px;padding:20px 16px;background:#20465d;font-size:24px;font-weight:800;color:#fff}
.wf-person small{display:block;font-size:17px;color:#d2e8f3;font-weight:500}
.wf-arrow{font-size:42px;color:#72f2e8;text-shadow:0 0 17px #21bec6;
 animation:wf-pulse 1.2s infinite alternate}
@keyframes wf-pulse{to{opacity:.45;transform:translateX(5px)}}
.wf-message{padding:16px 22px;border-left:5px solid #6ce9d7;background:#133d4d;
font-size:22px;line-height:1.55;color:#f1fafc;border-radius:10px}
.wf-pills{display:flex;gap:6px;margin:19px 0}
.wf-pills span{height:10px;flex:1;border-radius:10px;background:#244a61}
.wf-pills span.active{background:#64dcc8}
.wf-note{color:#bbcedc;font-size:18px!important}
@media(max-width:900px){
 .wf-cards{grid-template-columns:1fr}
 .wf-stage{padding:18px}
 .wf-person{font-size:19px;min-width:110px}
 .wf-stage-title{font-size:25px}
 .wf-stage-copy{font-size:19px}
}
@media(prefers-reduced-motion:reduce){.wf-arrow{animation:none}}
</style>
"""


def _safe(value):
    return escape(str(value), quote=True)


def _recorded_events(competition: dict, coordination: dict) -> list[dict]:
    """Construct one trace from authentic negotiated messages and coordination events."""
    events: list[dict] = []
    retailer = competition["retailer"]
    events.append({
        "phase": "Discovery", "sender": "C1", "receiver": retailer.agent_id,
        "action": "DISCOVERY_RESULT",
        "description": "Coordinator returned registered seller IDs: "
                       + ", ".join(competition["discovered_seller_ids"]),
        "note": "Summary of the actual discover_sellers() result; not a wire message.",
    })
    for seller_id in competition["evaluated_seller_ids"]:
        negotiation = competition["negotiations"][seller_id]
        for record in negotiation["timeline"]:
            events.append({
                "phase": "Negotiation", "sender": record["sender"],
                "receiver": record["receiver"], "action": record["performative"],
                "price": record["price"], "round": record["round"],
                "description": record["reason"], "seller": seller_id,
                "note": "Recorded negotiation message and LangGraph decision explanation.",
            })
    choice = competition["selection"]
    winner = choice["selected_seller_id"]
    events.append({
        "phase": "Supplier selection", "sender": retailer.agent_id,
        "receiver": winner or "—", "action": "SELECT" if winner else "NO_SELECTION",
        "description": choice["reasoning"],
        "note": "Recorded retailer-owned supplier selection; not an inter-agent message.",
    })
    for record in coordination["events"]:
        # These events are the real coordinator/delivery log; THINK is a rule-based
        # explanation, not a hidden LLM thought or a sent message.
        events.append({
            "phase": "Delivery & reservation",
            "sender": record["actor"], "receiver": "C1" if record["actor"] == "D1" else "—",
            "action": record["action"], "description": record["explanation"],
            "note": "Actual coordination event. THINK indicates rule evaluation.",
        })
    events.append({
        "phase": "Final outcome",
        "sender": "C1", "receiver": retailer.agent_id,
        "action": coordination["status"], "description": coordination["reason"],
        "note": "Simulation status only. No real payment, delivery, or external stock changes.",
    })
    return events


def _run_session(retailer_id: str, seller_ids: list[str], quantity: int,
                 initial_price: float, target: float, rounds: int,
                 resale_price: float) -> dict:
    """One run generates an isolated one-time ledger; playback is read-only."""
    competition = run_supplier_competition(
        retailer_id=retailer_id, seller_ids=seller_ids, quantity=quantity,
        initial_price=initial_price, retailer_target=target,
        max_rounds=rounds, expected_retail_price=resale_price,
    )
    ledger = ReservationLedger.from_marketplace()
    before = {
        "seller_stock": dict(ledger.seller_stock),
        "retailer_demand": dict(ledger.retailer_demand),
        "retailer_budget": dict(ledger.retailer_budget),
        "delivery_capacity": dict(ledger.delivery_capacity),
    }
    coordination = run_delivery_coordination(
        competition, ledger, quantity=quantity, expected_retail_price=resale_price,
    )
    after = {
        "seller_stock": dict(ledger.seller_stock),
        "retailer_demand": dict(ledger.retailer_demand),
        "retailer_budget": dict(ledger.retailer_budget),
        "delivery_capacity": dict(ledger.delivery_capacity),
    }
    return {
        "competition": competition,
        "coordination": coordination,
        "events": _recorded_events(competition, coordination),
        "before": before, "after": after,
        "params": {
            "retailer_id": retailer_id, "seller_ids": seller_ids,
            "quantity": quantity, "initial_price": initial_price,
            "target": target, "rounds": rounds, "resale_price": resale_price,
        },
    }


def _stage_html(event: dict, index: int, count: int) -> str:
    sender, receiver = _safe(event["sender"]), _safe(event["receiver"])
    action, phase = _safe(event["action"]), _safe(event["phase"])
    text = _safe(event["description"])
    arrow = "→" if receiver != "—" else "◆"
    note = _safe(event["note"])
    badge = (
        f"<div class='wf-message'><b>{action}</b>"
        + (f" · Rs. {float(event['price']):,.2f}" if event.get("price") is not None else "")
        + f"<div>{text}</div></div>"
    )
    pills = "".join(
        f"<span class={'active' if i <= index else 'inactive'}></span>"
        for i in range(count)
    )
    return (
        "<div class='wf-stage'>"
        f"<div class='wf-stage-head'>RECORDED EVENT {index + 1} / {count} · {phase}</div>"
        f"<div class='wf-stage-title'>{sender} · {action}</div>"
        "<div class='wf-route'>"
        f"<div class='wf-person'>🤖 {sender}<small>Current actor</small></div>"
        f"<div class='wf-arrow'>{arrow}</div>"
        f"<div class='wf-person'>🤖 {receiver}<small>Target or outcome</small></div>"
        "</div>" + badge +
        f"<p class='wf-note'>{note}</p>"
        f"<div class='wf-pills'>{pills}</div></div>"
    )


def _show_final(run: dict):
    comp, out = run["competition"], run["coordination"]
    choice = comp["selection"]
    st.markdown("### Final multi-agent decision")
    status = out["status"]
    if status == "RESERVED_SIMULATED":
        st.success("Synthetic reservation completed successfully.")
    else:
        st.warning(f"Simulation ended: {status} — {out['reason']}")
    a, b, c, d = st.columns(4)
    a.metric("Chosen seller", choice["selected_seller_id"] or "None")
    b.metric("Agreed packet price", f"Rs. {choice['selected_price']:,.2f}"
             if choice["selected_price"] is not None else "No agreement")
    c.metric("Delivery quote", f"Rs. {out['delivery_fee']:,.2f}"
             if out["delivery_fee"] is not None else "Not quoted")
    d.metric("Reservation status", status)
    if out["reservation"]:
        st.dataframe([out["reservation"]], hide_index=True, use_container_width=True)
    st.write("**Why this supplier?** " + choice["reasoning"])
    st.write("**Why this final status?** " + out["reason"])
    with st.expander("Resource changes in this isolated simulated run"):
        rows = []
        for key, label in (
            ("seller_stock", "Seller stock"), ("retailer_demand", "Retailer demand"),
            ("retailer_budget", "Retailer budget (Rs.)"),
            ("delivery_capacity", "Delivery capacity"),
        ):
            for agent, start in run["before"][key].items():
                rows.append({
                    "Resource": label, "Agent": agent, "Before": start,
                    "After": run["after"][key][agent],
                })
        st.dataframe(rows, use_container_width=True, hide_index=True)


def _show_recorded_trace(run: dict):
    with st.expander("Technical evidence · full recorded trace"):
        st.dataframe(run["events"], hide_index=True, use_container_width=True)
        with st.expander("Validated negotiation and delivery messages"):
            messages = []
            for seller in run["competition"]["evaluated_seller_ids"]:
                messages.extend(run["competition"]["negotiations"][seller]["messages"])
            messages.extend(run["coordination"]["messages"])
            st.json([msg.model_dump(mode="json") for msg in messages])


def _display_step(run: dict, index: int):
    events = run["events"]
    index = max(0, min(index, len(events) - 1))
    event = events[index]
    if event["phase"] == "Negotiation":
        negotiation = run["competition"]["negotiations"][event["seller"]]
        timeline = negotiation["timeline"]
        # Match this particular event, even when dict values happen to duplicate.
        # Event identity is resolved by ordinal within this seller's message trace.
        same_seller_events = [e for e in events[:index+1]
                              if e["phase"] == "Negotiation" and e["seller"] == event["seller"]]
        local_index = len(same_seller_events) - 1
        st.markdown(neon_scene(
            timeline, local_index, run["params"]["retailer_id"], event["seller"],
        ), unsafe_allow_html=True)
    else:
        st.markdown(_stage_html(event, index, len(events)), unsafe_allow_html=True)
    st.caption(f"Event {index + 1}/{len(events)} · {event['phase']}")
    if index == len(events) - 1:
        _show_final(run)


def render_workflow_simulator():
    st.markdown(WORKFLOW_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="wf-top"><strong>⚡ Interactive Agent Workflow Simulator</strong>'
        '<p>Configure a synthetic order, run autonomous agents, then watch '
        'their real decisions unfold from discovery to the final outcome.</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### 1 · Configure the scenario")
    agents = {a.agent_id: a for a in build_agents()}
    listings = {x.seller_id: x for x in public_listings()}
    with st.form("wf_configuration"):
        one, two, three = st.columns(3)
        retailer_id = one.selectbox("Retailer agent", ["R1", "R2"])
        selected_sellers = two.multiselect("Competing seller agents", ["S1", "S2"],
                                           default=["S1", "S2"])
        quantity = three.number_input("Required quantity (packets)", min_value=1,
                                      max_value=300, value=150, step=10)
        a, b, c, d = st.columns(4)
        opening = a.number_input("Initial buying offer (Rs.)", min_value=100.0,
                                 max_value=190.0, value=150.0, step=5.0)
        target = b.number_input("Retailer target (Rs.)", min_value=100.0,
                                max_value=190.0, value=150.0, step=5.0)
        rounds = c.slider("Maximum negotiation rounds", 1, 10, 5)
        resale = d.number_input("Assumed resale price (Rs.)", min_value=100.0,
                                max_value=350.0, value=200.0, step=5.0)
        speed = st.selectbox("Animation speed", ("Slow", "Normal", "Fast"), index=1)
        run_button = st.form_submit_button("▶ Run complete MAS workflow",
                                           type="primary", use_container_width=True)
    st.caption(
        "Run computes the complete result with real LangGraph policies and an isolated "
        "in-memory ledger. The animated replay then reveals the already-recorded evidence. "
        "No real orders or transactions occur."
    )
    st.markdown("### Agent profiles and public prices")
    cards = ['<div class="wf-cards">']
    buyer = agents[retailer_id]
    cards.append(
        f"<div class='wf-card retailer'><div class='name'>🛒 Retailer {retailer_id}</div>"
        f"<div class='details'>Goal: {_safe(buyer.goal)}<br>"
        f"Demand: {buyer.demand} packets<br>Budget: Rs. {buyer.budget:,.2f}</div></div>"
    )
    for sid in selected_sellers:
        a = agents[sid]
        listing = listings[sid]
        cards.append(
            f"<div class='wf-card'><div class='name'>🏪 Seller {sid}</div>"
            f"<div class='details'>Goal: {_safe(a.goal)}<br>"
            f"Public asking price: Rs. {listing.listed_price:,.2f}<br>"
            f"Advertised stock: {listing.advertised_stock} packets</div></div>"
        )
    cards.append("</div>")
    st.markdown("".join(cards), unsafe_allow_html=True)
    if run_button:
        if not selected_sellers:
            st.error("Select at least one registered seller before running.")
        elif quantity > buyer.demand:
            st.error(f"{retailer_id} demand is {buyer.demand} packets; reduce the quantity.")
        else:
            try:
                run = _run_session(
                    retailer_id=retailer_id, seller_ids=selected_sellers,
                    quantity=int(quantity), initial_price=float(opening),
                    target=float(target), rounds=int(rounds), resale_price=float(resale),
                )
                st.session_state["wf_run"] = run
                st.session_state["wf_index"] = 0
                st.session_state["wf_speed"] = speed
            except (ValueError, RuntimeError, KeyError) as exc:
                st.error(f"Workflow failed: {exc}")
    run = st.session_state.get("wf_run")
    if not run:
        st.info("Configure the inputs and press Run to create a replayable synthetic workflow.")
        return
    if run["params"] != dict(
        retailer_id=retailer_id, seller_ids=selected_sellers,
        quantity=int(quantity), initial_price=float(opening),
        target=float(target), rounds=int(rounds), resale_price=float(resale),
    ):
        st.warning("The current controls differ from the last recorded run. "
                   "Press Run again to apply the new configuration.")
    st.markdown("### 2 · Watch the agents communicate")
    events = run["events"]
    current = min(int(st.session_state.get("wf_index", 0)), len(events)-1)
    stage = st.empty()
    with stage.container():
        _display_step(run, current)
    back, forward, play, restart = st.columns([1,1,1.6,1])
    if back.button("← Previous", disabled=current==0, use_container_width=True):
        st.session_state["wf_index"] = current-1
        st.rerun()
    if forward.button("Next event →", disabled=current==len(events)-1,
                      use_container_width=True):
        st.session_state["wf_index"] = current+1
        st.rerun()
    if play.button("▶ Play to final outcome", type="primary", use_container_width=True):
        pause = {"Slow":1.1,"Normal":0.6,"Fast":0.25}[st.session_state.get("wf_speed","Normal")]
        for i in range(current, len(events)):
            with stage.container():
                _display_step(run, i)
            time.sleep(pause)
        st.session_state["wf_index"] = len(events)-1
        st.rerun()
    if restart.button("↺ Replay from start", use_container_width=True):
        st.session_state["wf_index"] = 0
        st.rerun()
    st.markdown("### 3 · Examine the MAS evidence")
    st.markdown(
        "**Autonomy:** Independent seller and retailer graphs. "
        "**Communication:** Typed, validated messages. "
        "**Competition:** Multiple seller negotiations. "
        "**Cooperation:** Delivery quotation and retailer approval. "
        "**Coordination:** Simulated all-or-none reservation."
    )
    _show_recorded_trace(run)
