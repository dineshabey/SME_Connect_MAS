"""Animated, English-only multi-agent sequence replay.

Runs existing MAS policies once through the workflow simulator and presents
recorded events in a client-side, pauseable SVG sequence diagram. Rendering and
replay do not make additional bookings or change agent state.
"""
from __future__ import annotations

import json
from html import escape

import streamlit as st
import streamlit.components.v1 as components

from dashboard.workflow_simulator import _run_session
from smeconnect.environment.marketplace import build_agents
from smeconnect.environment.catalogue import public_listings
from smeconnect.environment.market_state import MarketSnapshot


AGENT_DISPLAY_NAMES = {
    "R1": "Retailer Agent R1",
    "R2": "Retailer Agent R2",
    "S1": "Seller Agent S1",
    "S2": "Seller Agent S2",
    "D1": "Delivery Agent D1",
    "C1": "Coordinator Agent C1",
    "M1": "Market Agent M1",
}


def _agent_label(agent_id: str) -> str:
    """Human-readable label; internal message and graph IDs stay unchanged."""
    return AGENT_DISPLAY_NAMES.get(agent_id, agent_id)


def _sequence_events(run: dict) -> list[dict]:
    """Reconcile real messages with decision log events, retaining provenance."""
    comp, coordination = run["competition"], run["coordination"]
    retailer_id = comp["retailer"].agent_id
    result = [{
        "phase": "Discovery", "kind": "decision", "sender": "C1",
        "receiver": "", "action": "DISCOVER",
        "description": "Registered sellers discovered: " +
        ", ".join(comp["discovered_seller_ids"]),
        "label": "Seller discovery",
    }]
    for seller_id in comp["evaluated_seller_ids"]:
        negotiation = comp["negotiations"][seller_id]
        timeline, messages = negotiation["timeline"], negotiation["messages"]
        if len(timeline) != len(messages):
            raise ValueError("Negotiation message and event counts differ.")
        for event, msg in zip(timeline, messages):
            if (msg.sender != event["sender"] or msg.receiver != event["receiver"]
                    or msg.performative.value != event["performative"]):
                raise ValueError("Negotiation event does not match validated message.")
            result.append({
                "phase": "Negotiation · " + seller_id,
                "kind": "message", "sender": msg.sender, "receiver": msg.receiver,
                "action": msg.performative.value,
                "description": event["reason"], "round": event["round"],
                "price": msg.unit_price, "quantity": msg.quantity,
                "label": msg.performative.value + " · Rs." + f"{msg.unit_price:,.2f}",
            })

    choice = comp["selection"]
    result.append({
        "phase": "Supplier selection", "kind": "decision", "sender": retailer_id,
        "receiver": "", "action": "SELECT" if choice["selected_seller_id"] else "NO_SELECTION",
        "description": choice["reasoning"],
        "label": ("Selected " + choice["selected_seller_id"]
                  if choice["selected_seller_id"] else "No feasible supplier"),
    })

    messages = coordination["messages"]
    msg_index = 0
    for event in coordination["events"]:
        if msg_index < len(messages):
            msg = messages[msg_index]
            if event["actor"] == msg.sender and event["action"] == msg.performative.value:
                # The fulfillment event log records exactly one event per send().
                result.append({
                    "phase": "Delivery & coordination", "kind": "message",
                    "sender": msg.sender, "receiver": msg.receiver,
                    "action": msg.performative.value, "description": event["explanation"],
                    "price": msg.unit_price, "quantity": msg.quantity,
                    "label": msg.performative.value +
                             (f" · Rs.{msg.unit_price:,.2f}" if msg.unit_price else ""),
                })
                msg_index += 1
                continue
        result.append({
            "phase": "Delivery & coordination", "kind": "decision",
            "sender": event["actor"], "receiver": "",
            "action": event["action"], "description": event["explanation"],
            "label": event["actor"] + " · " + event["action"],
        })
    if msg_index != len(messages):
        raise ValueError("Some validated delivery messages were not matched to events.")

    # The final explanation includes only recorded reservation evidence.
    reservation = coordination.get("reservation")
    final_description = coordination["reason"]
    if reservation is not None:
        final_description = (
            f"Coordinator C1 reserved {reservation['quantity']} packets from "
            f"{reservation['seller_id']} for {reservation['retailer_id']} "
            f"at Rs.{reservation['unit_price']:,.2f} per packet. "
            f"The delivery fee was Rs.{reservation['delivery_fee']:,.2f}, "
            f"making the total simulated commitment Rs.{reservation['reserved_total']:,.2f}. "
            "The reservation ledger allocated seller stock, retailer demand, "
            "buyer budget and delivery capacity together. "
            "No real payment or shipment occurred."
        )
    result.append({
        "phase": "Final result", "kind": "decision", "sender": "C1",
        "receiver": "", "action": coordination["status"],
        "description": final_description,
        "label": "Final · " + coordination["status"],
    })
    return result


def _sequence_html(events: list[dict], actors: list[str], summary: dict,
                   speed: str = "Normal") -> str:
    """Build one self-contained iframe with replay controls (no remote assets)."""
    if not events or not actors:
        raise ValueError("Events and actor lifelines are required.")
    payload = json.dumps({
        "events": events, "actors": actors, "summary": summary, "speed": speed,
        "actor_labels": {agent_id: _agent_label(agent_id) for agent_id in actors},
    }, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    page = r'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap-grid.min.css" rel="stylesheet">
<style>
:root{color-scheme:dark;--ink:#eaf6fc;--muted:#acc5d6;--teal:#69ebd8;--line:#4d7490}
*{box-sizing:border-box}
body{margin:0;background:#0e1a2c;color:var(--ink);font:21px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}
.shell{background:linear-gradient(140deg,#11243b,#12364b);border:1px solid #3c7591;border-radius:20px;padding:22px;min-height:0;overflow:visible}
.top{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap}
h1{margin:0;font-size:36px;letter-spacing:-.02em}
.sub{color:#c7dce8;font-size:22px}
.legend{display:flex;gap:20px;flex-wrap:wrap;color:#b9d6e3;font-size:19px;padding:16px 0}
.legend b{color:#80edd7}
.controls{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 14px}
button{border:1px solid #4d89a0;background:#1b4259;color:#eefaff;padding:12px 19px;border-radius:12px;
cursor:pointer;font:750 21px system-ui;min-height:58px}
button.primary{background:#1b746f;border-color:#74dcd2}
button:disabled{opacity:.4;cursor:not-allowed}
button:focus-visible{outline:3px solid #d6fff0;outline-offset:2px}
.counter{font-size:23px;color:#aef9e9;font-weight:800;margin:3px 0}
.diagram{height:400px;overflow:auto;border:1px solid #44687f;border-radius:16px;background:
radial-gradient(circle at 50% 20%,#163a54,#0d1e34);scroll-behavior:smooth}
.diagram.overview-active{overflow:hidden}
.sequence-overview{display:none;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-rows:repeat(6,minmax(0,1fr));
gap:7px;padding:9px;height:100%;width:100%;min-height:0}
.diagram.overview-active .sequence-overview{display:grid}
.diagram.overview-active #sequence{display:none}
/* Desktop replay is a single viewport: only messages scroll vertically.
   This avoids Streamlit's 1600px outer iframe/page scroll hiding agent names. */
@media (min-width:1051px){
  html,body{height:100%;overflow:hidden}
  .shell:not(:fullscreen){
    height:100dvh;max-height:100dvh;display:flex;flex-direction:column;
    overflow:hidden
  }
  .shell:not(:fullscreen) .top,
  .shell:not(:fullscreen) .legend,
  .shell:not(:fullscreen) .controls{flex:0 0 auto}
  .shell:not(:fullscreen) .presentation-layout{
    flex:1 1 0;min-height:0;height:auto;max-height:100%;
    overflow:hidden
  }
  .shell:not(:fullscreen) .presentation-stage{
    height:100%;min-height:0;overflow:hidden
  }
  .shell:not(:fullscreen) .presentation-stage .diagram{
    flex:1 1 0;min-height:0;height:auto;overflow:auto
  }
  .shell:not(:fullscreen) .presentation-side{
    height:100%;max-height:100%;min-height:0;overflow-y:auto
  }
}
/* Remains visible when either inner event scroller or outer presentation scrolls. */
.agent-header-viewport{position:sticky;top:0;z-index:30}
/* Header is OUTSIDE the scrollable diagram; vertical scrolling cannot move it. */
.agent-header-viewport{height:85px;position:relative;overflow:hidden;
 border:1px solid #446f86;border-bottom:0;border-radius:14px 14px 0 0;
 background:#10263e;flex-shrink:0}
.agent-header-track{height:100%;position:relative;min-width:720px}
.agent-header-label{position:absolute;top:9px;transform:translateX(-50%);
 width:clamp(108px,12vw,190px);min-height:62px;padding:8px 7px;
 display:flex;align-items:center;justify-content:center;text-align:center;
 border:1px solid #75bfd2;border-radius:11px;background:#23536d;
 color:#fff;font-size:clamp(12px,1vw,18px);font-weight:800;line-height:1.2;
 box-shadow:0 5px 14px #061829a8}
.presentation-stage:has(.diagram.overview-active) .agent-header-viewport{display:none}
.presentation-stage .diagram{border-radius:0 0 14px 14px}
.presentation-stage:has(.diagram.overview-active) .diagram{border-radius:14px}
.shell:fullscreen .agent-header-viewport{height:73px}
.shell:fullscreen .agent-header-label{min-height:56px;font-size:clamp(11px,.94vw,17px)}

.overview-event{position:relative;min-height:0;min-width:0;border:1px solid #497a94;
border-radius:9px;padding:7px 10px;text-align:left;background:#173650;color:#e1eff9;
display:flex;flex-direction:column;justify-content:center;gap:2px;
overflow:hidden;cursor:pointer;transition:background .15s ease,border-color .15s ease}
.overview-event:focus-visible{outline:3px solid #b4fff3;outline-offset:-2px}
.overview-event.current{border:2px solid #9dfff0;background:#17666b;
box-shadow:0 0 13px #29cfc655}
.overview-event.future{opacity:.55}
.overview-event.decision{border-left:4px solid #bda7fd}
.overview-event .stepno{font-size:12px;font-weight:850;color:#93fff1;line-height:1.1}
.overview-event .route{font-size:15px;font-weight:800;color:#fff;line-height:1.2;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.overview-event .msg{font-size:14px;font-weight:650;color:#c7e5ef;line-height:1.2;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.overview-event:not(:nth-child(3n)):after{content:'→';position:absolute;right:1px;top:45%;
font-weight:850;color:#82edda;font-size:16px}
.overview-caption{display:none;font-size:15px;font-weight:750;color:#a7fbe8;
padding:0 10px 5px}
.diagram.overview-active .overview-caption{display:block}
@media(min-width:1200px){.overview-event .route{font-size:18px}.overview-event .msg{font-size:17px}
.overview-event .stepno{font-size:14px}.sequence-overview{gap:10px;padding:14px}}
@media(max-width:800px){.sequence-overview{gap:4px;padding:5px}
.overview-event{padding:4px 5px}.overview-event .stepno{font-size:11px}
.overview-event .route{font-size:15px}.overview-event .msg{font-size:14px}}

svg{display:block;width:100%;min-width:720px}
.detail{display:flex;flex-wrap:wrap;gap:0;margin-top:20px;align-items:stretch;margin-left:-9px;margin-right:-9px}
.detail > .col-12{box-sizing:border-box;padding:0 9px;margin-bottom:18px;min-width:0;flex:0 0 100%;width:100%}
@media(min-width:1200px){.detail>.col-xl-5{flex:0 0 41.666667%;width:41.666667%}.detail>.col-xl-7{flex:0 0 58.333333%;width:58.333333%}}
.panel{padding:27px 29px;border:2px solid #4b8ca4;background:linear-gradient(145deg,#183a55,#1a4760);border-radius:18px;min-height:245px}
.panel h2{font-size:29px;margin:7px 0 14px;line-height:1.35}
.panel p{margin:9px 0;font-size:24px;line-height:1.65;color:#f0f9ff}
.kicker{font-size:19px;color:#96ffdf;font-weight:850;letter-spacing:.08em}
#decision-panel{border-color:#64d8c7;background:linear-gradient(145deg,#153c49,#205263);
box-shadow:0 10px 26px #06182777}
#reason{font-size:26px!important;font-weight:650;line-height:1.65;color:#fff}
.explain-extra{border-top:1px solid #4d8795;margin-top:18px;padding-top:16px}
.explain-extra strong{font-size:19px;color:#a0f6e6}
#impact{font-size:22px!important;color:#e0f2f4;line-height:1.6}
.final{margin-top:20px;padding:23px 26px;border:2px solid #5dbaaa;border-radius:17px;
background:linear-gradient(110deg,#174f4d,#173c52)}
.final h2{margin:0 0 10px;font-size:31px}
.stats{display:flex;gap:18px;flex-wrap:wrap}
.stat{min-width:150px;flex:1;padding:10px;background:#ffffff10;border-radius:10px}
.stat span{display:block;color:#c6e2ec;font-size:20px}.stat b{display:block;font-size:30px}
.small{font-size:18px!important;color:#c3dce7!important;line-height:1.5!important}
/* The explanation must stay fully visible inside Streamlit's fixed iframe. */
.detail .panel{height:100%;min-height:270px;overflow:visible;overflow-wrap:anywhere}
#decision-panel #reason{overflow-wrap:anywhere;white-space:normal}
.final p{font-size:21px;line-height:1.6}
/* Presenter cockpit: event explanations on the left, diagrams on the right. */
.presentation-layout{display:grid;grid-template-columns:minmax(280px,30%) minmax(0,1fr);
  gap:16px;min-height:590px;margin-top:12px;align-items:stretch}
.presentation-side{min-width:0;display:flex;flex-direction:column;gap:12px;max-height:690px}
.presentation-stage{min-width:0;min-height:0;display:flex;flex-direction:column}
.presentation-stage .diagram{height:650px;min-height:400px;flex:1}
.presentation-side .detail{display:flex;flex-direction:column;gap:12px;
  margin:0;flex:none;min-height:0}
.presentation-side .detail>.col-12,.presentation-side .detail>.col-xl-5,
.presentation-side .detail>.col-xl-7{width:100%!important;flex:0 0 auto!important;
  max-width:none!important;padding:0!important;margin:0}
.presentation-side .panel{padding:17px 19px;min-height:0;height:auto}
.presentation-side .panel h2{font-size:22px;line-height:1.35}
.presentation-side .panel p{font-size:18px;line-height:1.45}
.presentation-side #reason{font-size:20px!important;line-height:1.45}
.presentation-side #impact{font-size:17px!important;line-height:1.35}
.presentation-side .kicker{font-size:15px}
.presentation-side .explain-extra{margin-top:10px;padding-top:9px}
.presentation-side .small{font-size:14px!important}
.presentation-side .final{margin-top:0;padding:12px 15px}
.presentation-side .final h2{font-size:20px}
.presentation-side .stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}
.presentation-side .stat{min-width:0;padding:9px}
.presentation-side .stat span{font-size:13px}
.presentation-side .stat b{font-size:18px;overflow-wrap:anywhere}
.presentation-side .final p{font-size:14px}
@media(max-width:1050px){
  .presentation-layout{grid-template-columns:1fr;display:flex;flex-direction:column}
  .presentation-stage{order:0}.presentation-side{order:1;max-height:none}
  .presentation-stage .diagram{height:450px;flex:auto}
}
.shell:fullscreen,.shell:-webkit-full-screen{height:100dvh;overflow:hidden}
.shell:fullscreen .presentation-layout,.shell:-webkit-full-screen .presentation-layout{
 flex:1 1 0;min-height:0;max-height:100%;display:grid;
 grid-template-columns:clamp(295px,29vw,440px) minmax(0,1fr);gap:14px;
 margin-top:4px;overflow:hidden
}
.shell:fullscreen .presentation-stage{height:100%;min-height:0}
.shell:fullscreen .presentation-stage .diagram{flex:1 1 0;min-height:0;height:auto;overflow:hidden}
.shell:fullscreen .presentation-side{max-height:100%;min-height:0;overflow:hidden;
 display:flex;flex-direction:column;gap:8px}
.shell:fullscreen .presentation-side .detail{display:flex!important;flex-direction:column;gap:7px}
.shell:fullscreen .presentation-side .detail>.col-12{flex:0 0 auto!important}
.shell:fullscreen .presentation-side .panel{min-height:0;height:auto;padding:10px 13px}
.shell:fullscreen .presentation-side .panel h2{font-size:clamp(14px,1.4vw,19px)}
.shell:fullscreen .presentation-side .panel p{font-size:clamp(12px,1.1vw,16px);line-height:1.25}
.shell:fullscreen .presentation-side #reason{font-size:clamp(13px,1.1vw,16px)!important;line-height:1.25}
.shell:fullscreen .presentation-side #impact{font-size:clamp(12px,1vw,15px)!important;line-height:1.25}
.shell:fullscreen .presentation-side .kicker{font-size:12px}
.shell:fullscreen .presentation-side .explain-extra{margin-top:5px;padding-top:5px}
.shell:fullscreen .presentation-side .explain-extra strong{font-size:12px}
.shell:fullscreen .presentation-side .small{font-size:11px!important}
.shell:fullscreen .presentation-side .final{display:block!important;margin-top:0;
 padding:8px 10px;flex:0 1 auto;min-height:0;overflow:hidden}
.shell:fullscreen .presentation-side .final[hidden]{display:none!important}
.shell:fullscreen .presentation-side .final h2{font-size:15px}
.shell:fullscreen .presentation-side .stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:5px}
.shell:fullscreen .presentation-side .stat{min-width:0;padding:4px 6px}
.shell:fullscreen .presentation-side .stat span{font-size:11px}
.shell:fullscreen .presentation-side .stat b{font-size:15px}
.shell:fullscreen .presentation-side .final p{font-size:11px;margin:3px 0}
.shell:fullscreen .overview-event .route{font-size:clamp(13px,1.1vw,19px)}
.shell:fullscreen .overview-event .msg{font-size:clamp(12px,1vw,17px)}
.shell:fullscreen:has(.diagram.overview-active) .presentation-side .detail{display:flex!important}
.shell:fullscreen:has(.diagram.overview-active) .presentation-side .final{max-height:none;overflow:hidden}
.shell:fullscreen:has(.diagram.overview-active) .presentation-side .final p{display:block}
@media(max-height:760px){
 .shell:fullscreen .presentation-side .small,.shell:fullscreen .presentation-side #provenance{display:none}
 .shell:fullscreen .presentation-side .final p{display:none}
 .shell:fullscreen .presentation-side .panel{padding:7px 10px}
 .shell:fullscreen .presentation-side .explain-extra{margin-top:3px;padding-top:3px}
 .shell:fullscreen .presentation-side{gap:5px}
 .shell:fullscreen .top .sub{display:none}
}

/* Full-screen presentation: all lifelines and events fit the visible screen. */
.shell:fullscreen,.shell:-webkit-full-screen{
 width:100vw;height:100vh;max-width:none;margin:0;border-radius:0;
 padding:16px 24px;display:flex;flex-direction:column;background:#0b1b2e;
 overflow:hidden
}
.shell:fullscreen .top,.shell:fullscreen .legend,.shell:fullscreen .controls,
.shell:fullscreen .detail,.shell:fullscreen .final{flex-shrink:0}
.shell:fullscreen .diagram,.shell:-webkit-full-screen .diagram{
 flex:1 1 0;min-height:0;height:auto;overflow:hidden
}
.shell:fullscreen .diagram.overview-active{height:auto}
.shell:fullscreen:has(.diagram.overview-active) .detail{display:flex}
.shell:fullscreen:has(.diagram.overview-active) .legend{display:none}
.shell:fullscreen:has(.diagram.overview-active) .final{margin-top:0;max-height:none;overflow:hidden}
.shell:fullscreen:has(.diagram.overview-active) .final p{display:block}
.shell:fullscreen:has(.diagram.overview-active) .final .stats{gap:6px}
.shell:fullscreen:has(.diagram.overview-active) .final .stat{min-width:0}

.shell:fullscreen .detail{margin-top:10px}
.shell:fullscreen .panel{min-height:110px;padding:12px 18px}
.shell:fullscreen .panel h2{font-size:20px;margin:3px 0}
.shell:fullscreen .panel p{font-size:17px;line-height:1.35;margin:3px 0}
.shell:fullscreen #reason{font-size:18px!important;line-height:1.35}
.shell:fullscreen #impact{font-size:16px!important;line-height:1.3}
.shell:fullscreen .explain-extra{margin-top:6px;padding-top:6px}
.shell:fullscreen .small{font-size:13px!important}
.shell:fullscreen .final{margin-top:6px;padding:9px 15px}
.shell:fullscreen .final h2{font-size:20px;margin:0 0 4px}
.shell:fullscreen .stat{padding:5px;min-width:110px}
.shell:fullscreen .stat b{font-size:20px}
.shell:fullscreen .stat span{font-size:13px}
.shell:fullscreen .final p{font-size:13px;margin:5px 0}
.shell:fullscreen h1{font-size:26px}
.shell:fullscreen .sub,.shell:fullscreen .legend{font-size:14px}
.shell:fullscreen .legend{padding:4px 0}
.shell:fullscreen .controls{margin:3px 0 7px}
.shell:fullscreen button{min-height:38px;padding:6px 13px;font-size:16px}
.shell:fullscreen .counter{font-size:18px}
button[aria-pressed="true"]{background:#166b63;border-color:#8cebd9}
#fullscreen-notice{font-size:15px;color:#ffdfb3;margin-left:6px;align-self:center}
@media(max-height:720px){.shell:fullscreen .legend{display:none}.shell:fullscreen .detail .panel{min-height:80px}}


@media(max-width:850px){.shell{padding:13px}h1{font-size:24px}
.diagram{height:360px}button{font-size:18px;padding:10px 13px}.panel p{font-size:20px}.panel h2{font-size:24px}}
@media(prefers-reduced-motion:reduce){.diagram{scroll-behavior:auto}}
</style></head>
<body><main class="shell">
<div class="top"><div><h1>Multi-Agent Sequence Replay</h1>
<div class="sub">Real agent messages and labelled decision events · synthetic marketplace</div></div>
<div class="counter" aria-live="polite" id="counter"></div></div>
<div class="legend"><span><b>Solid arrow</b> · validated message</span>
<span><b>Decision card</b> · internal computation, not a transmitted message</span>
<span><b>Bright teal</b> · current event</span></div>
<div class="controls">
<button id="previous">← Previous</button><button class="primary" id="toggle">▶ Play</button>
<button id="next">Next →</button><button id="restart">↺ Restart</button>
<button id="end">Show final result</button>
<button id="fullscreen" aria-pressed="false" title="Use Escape to exit">⛶ Full Screen</button>
<button id="present" class="primary" title="Start animation in full screen">▶ Start Presentation Full Screen</button>
<button id="fit" aria-pressed="false" title="Fit all recorded events without scrolling">⊞ Fit Entire Sequence</button>
<span id="fullscreen-notice" role="status" aria-live="polite"></span></div>
<div class="presentation-layout">
<aside class="presentation-side" aria-label="Current agent decision and final result">
<div class="row g-3 detail">
<div class="col-12 col-xl-5"><section class="panel"><div class="kicker">CURRENT EVENT</div><h2 id="title"></h2>
<p id="message"></p><p id="round"></p></section></div>
<div class="col-12 col-xl-7"><section class="panel" id="decision-panel" aria-live="polite">
<div class="kicker">AGENT DECISION EXPLAINED</div><h2 id="why-title">Why did it happen?</h2>
<p id="reason"></p><div class="explain-extra"><strong id="impact-label">What happened next?</strong>
<p id="impact"></p></div><p class="small" id="provenance"></p></section></div>
</div><section id="final" class="final" hidden></section>
</aside>
<div class="presentation-stage">
<div class="agent-header-viewport" id="agent-header-viewport" aria-label="Agent names stay fixed while messages scroll"><div class="agent-header-track" id="agent-header-track"></div></div>
<div class="diagram" id="viewport"><svg id="sequence" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sequence of recorded agent interactions"></svg><div id="sequence-overview" class="sequence-overview" role="group" aria-label="All recorded events in reading order, left to right and top to bottom"></div></div>
<div class="overview-caption" id="overview-caption">Reading order: left → right, then next row ↓ · Select an event to inspect its explanation.</div>
</div></div></main>
<script>
const model=__DATA__;
const ev=model.events,actors=model.actors;
const actorLabel=id=>model.actor_labels[id]||id;
// Streamlit's HTML iframe has a fixed fallback height. Report measured content
// size so its parent can expand the frame when supported by the runtime.
let lastHeight=0;
function resizeFrame(){
  const height=Math.ceil(Math.max(
    document.documentElement.scrollHeight,document.body.scrollHeight,
    document.querySelector(".shell").getBoundingClientRect().bottom
  ))+28;
  if(Math.abs(height-lastHeight)>3){
    lastHeight=height;
    window.parent.postMessage({
      isStreamlitMessage:true,type:"streamlit:setFrameHeight",height:height
    },"*");
  }
}
if(window.ResizeObserver){
  new ResizeObserver(resizeFrame).observe(document.querySelector(".shell"));
}
window.addEventListener("resize",()=>{resizeFrame();requestAnimationFrame(draw)});
window.addEventListener("load",resizeFrame);
const svg=document.getElementById("sequence"),viewport=document.getElementById("viewport");
const ns="http://www.w3.org/2000/svg",left=105,right=1120;
const x=i=>left+i*(right-left)/Math.max(actors.length-1,1);
const H=166+ev.length*94;
const chosen=new Map(actors.map((v,i)=>[v,i]));
const headerViewport=document.getElementById("agent-header-viewport");
const headerTrack=document.getElementById("agent-header-track");
function renderAgentHeader(){
 headerTrack.replaceChildren();
 actors.forEach(agent=>{
   const label=document.createElement("div");
   label.className="agent-header-label";
   label.dataset.agentId=agent;
   label.textContent=actorLabel(agent);
   headerTrack.appendChild(label);
 });
}
function alignAgentHeader(){
 if(!svg.getScreenCTM())return;
 const rect=svg.getBoundingClientRect();
 const matrix=svg.getScreenCTM();
 headerTrack.style.width=rect.width+"px";
 actors.forEach((agent,j)=>{
   const label=headerTrack.children[j];
   // Convert SVG viewBox coordinates to precise rendered pixels.
   const px=matrix.a*x(j)+matrix.e-rect.left;
   label.style.left=px+"px";
 });
 headerTrack.style.transform="translateX("+(-viewport.scrollLeft)+"px)";
}
renderAgentHeader();
viewport.addEventListener("scroll",alignAgentHeader,{passive:true});
let index=0,timer=null,fitAll=false;
const shell=document.querySelector(".shell"),fullButton=document.getElementById("fullscreen");
const fitButton=document.getElementById("fit");
const presentButton=document.getElementById("present");
let fullscreenAttempted=false;
const overview=document.getElementById("sequence-overview");
function isFullscreen(){return document.fullscreenElement===shell||document.webkitFullscreenElement===shell}
function refreshFullscreen(){
 const full=isFullscreen();
 fullButton.textContent=full?"⛶ Exit Full Screen":"⛶ Full Screen";
 fullButton.setAttribute("aria-pressed",String(full));
 presentButton.hidden=full;
 if(full){fitAll=true;updateFitButton()}
 requestAnimationFrame(draw);
}
async function toggleFullscreen(){
 const notice=document.getElementById("fullscreen-notice");
 notice.textContent="";
 try{
   if(isFullscreen()){
     if(document.exitFullscreen)await document.exitFullscreen();
     else if(document.webkitExitFullscreen)document.webkitExitFullscreen();
   }else if(shell.requestFullscreen){
     await shell.requestFullscreen();
   }else if(shell.webkitRequestFullscreen){
     shell.webkitRequestFullscreen();
   }else{
     throw new Error("Full-screen API unavailable");
   }
 }catch(error){
   notice.textContent="Browser blocked full screen. Use Fit Entire Sequence, or open the standalone HTML.";
 }
}
async function tryAutomaticFullscreen(){
 // Streamlit's Python Run click normally cannot transfer browser user activation
 // through rerun into an iframe. Best-effort only, with a one-click fallback.
 if(fullscreenAttempted||isFullscreen())return;
 fullscreenAttempted=true;
 try{
   if(shell.requestFullscreen)await shell.requestFullscreen();
   else if(shell.webkitRequestFullscreen)shell.webkitRequestFullscreen();
   else throw new Error("Fullscreen unsupported");
 }catch(error){
   document.getElementById("fullscreen-notice").textContent=
     "Browser requires a direct click: use Start Presentation Full Screen.";
 }
}
function launchPresentation(){
 stop();index=0;show();start();
 if(!isFullscreen())toggleFullscreen();
}
presentButton.onclick=launchPresentation;
function updateFitButton(){
 fitButton.setAttribute("aria-pressed",String(fitAll));
 fitButton.textContent=fitAll?"◉ Detailed Sequence":"⊞ Fit Entire Sequence";
 viewport.classList.toggle("overview-active",fitAll);
 // The overview is a chronological 3-column storyboard, not a shrunken SVG.
 document.getElementById("overview-caption").style.display=fitAll?"block":"none";
}
function renderOverview(){
 overview.replaceChildren();
 // Default 18-event example is 3 × 6, but real scenarios can have more/fewer.
 overview.style.gridTemplateRows="repeat("+Math.ceil(ev.length/3)+",minmax(0,1fr))";
 ev.forEach((item,j)=>{
   const card=document.createElement("button");
   card.type="button";
   card.className="overview-event "+(item.kind==="decision"?"decision ":"")+
     (j===index?"current":j>index?"future":"");
   const row=document.createElement("span");row.className="stepno";
   row.textContent="EVENT "+String(j+1).padStart(2,"0")+" · "+item.phase;
   const route=document.createElement("span");route.className="route";
   route.textContent=item.kind==="message"
     ?item.sender+" → "+item.receiver
     :"◆ "+item.sender+" decision";
   const msg=document.createElement("span");msg.className="msg";
   msg.textContent=item.label||item.action;
   card.title=item.description||"";
   card.setAttribute("aria-label","Event "+(j+1)+": "+route.textContent+
       ". "+msg.textContent+". Select to view details.");
   card.append(row,route,msg);
   card.onclick=()=>{stop();step(j)};
   overview.appendChild(card);
 });
}
fullButton.onclick=toggleFullscreen;
fitButton.onclick=()=>{fitAll=!fitAll;updateFitButton();draw()};
document.addEventListener("fullscreenchange",refreshFullscreen);
document.addEventListener("webkitfullscreenchange",refreshFullscreen);

const timings={Slow:1400,Normal:850,Fast:400};
const reduced=window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
function element(tag,attrs={},text=""){
 const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));
 if(text)e.textContent=String(text);return e;
}
function append(parent,tag,attrs,text){const el=element(tag,attrs,text);parent.appendChild(el);return el}
function isMsg(item){return item.kind==="message" && chosen.has(item.sender)&&chosen.has(item.receiver)}
function draw(){
 viewport.classList.toggle("overview-active",fitAll);
 if(fitAll){
   renderOverview();
   viewport.scrollTop=0;viewport.scrollLeft=0;
   return;
 }
 svg.replaceChildren();svg.setAttribute("viewBox",`0 0 1220 ${H}`);
 svg.setAttribute("preserveAspectRatio","xMidYMin meet");
 svg.setAttribute("height",String(fitAll?Math.max(180,viewport.clientHeight):H));
 svg.style.minWidth=fitAll?"0":"720px";
 svg.style.width="100%";
 const defs=append(svg,"defs");
 const marker=append(defs,"marker",{id:"arrow",markerWidth:10,markerHeight:9,refX:9,refY:4,orient:"auto",markerUnits:"strokeWidth"});
 append(marker,"path",{d:"M0,0 L9,4 L0,8 Z",fill:"#60c8d0"});
 const activeMarker=append(defs,"marker",{id:"arrow-active",markerWidth:11,markerHeight:10,refX:9,refY:5,orient:"auto",markerUnits:"strokeWidth"});
 append(activeMarker,"path",{d:"M0,0 L10,5 L0,10 Z",fill:"#94fff0"});
 actors.forEach((agent,j)=>{
   const cx=x(j);
   // Agent names are rendered in the separate sticky HTML header above.
   append(svg,"line",{x1:cx,y1:89,x2:cx,y2:H-28,stroke:"#567d96","stroke-dasharray":"7 7","stroke-width":1.5});
 });
 ev.forEach((item,j)=>{
  if(j>index)return;
  const yy=135+j*94,active=j===index;
  const opacity=active?1:.48;
  const stroke=active?"#9effee":"#5fbdc6";
  if(isMsg(item)){
    const a=x(chosen.get(item.sender)),b=x(chosen.get(item.receiver));
    append(svg,"line",{x1:a,y1:yy,x2:b,y2:yy,stroke,"stroke-width":active?4:2.2,opacity,
      "marker-end":active?"url(#arrow-active)":"url(#arrow)"});
    const center=(a+b)/2;
    const label=String(item.label||item.action);
    const width=Math.min(450,Math.max(190,label.length*11+22));
    append(svg,"rect",{x:center-width/2,y:yy-45,width,height:34,rx:9,
      fill:active?"#18576a":"#1a354d",stroke:active?"#4ad4cf":"#476980",opacity:active?1:.94});
    append(svg,"text",{x:center,y:yy-22,"font-size":19,"font-weight":active?800:600,
      "text-anchor":"middle",fill:active?"#f8ffff":"#cce3ed"},label);
  }else{
    const cx=x(chosen.get(item.sender)??0),label=String(item.label||item.action);
    const width=Math.min(440,Math.max(170,label.length*10+24));
    append(svg,"rect",{x:Math.max(8,Math.min(1220-width-8,cx-width/2)),y:yy-28,width,height:54,rx:12,
      fill:active?"#19605e":"#1b3a4d",stroke:active?"#79ebd4":"#486e86",opacity});
    append(svg,"text",{x:Math.max(width/2+8,Math.min(1220-width/2-8,cx)),y:yy+6,
      "font-size":18,"font-weight":700,"text-anchor":"middle",fill:"#f1ffff"},label);
  }
 });
 requestAnimationFrame(alignAgentHeader);
 const focusY=135+index*94;
 if(fitAll){
   viewport.scrollTop=0;viewport.scrollLeft=0;
 }else if(reduced){viewport.scrollTop=Math.max(0,focusY-240)}
 else viewport.scrollTo({top:Math.max(0,focusY-240),behavior:"smooth"});
}
function show(){
 const item=ev[index];
 document.getElementById("counter").textContent=`Event ${index+1} of ${ev.length}`;
 document.getElementById("title").textContent=`${item.phase} · ${item.action}`;
 document.getElementById("message").textContent=item.kind==="message"
   ? `${actorLabel(item.sender)} → ${actorLabel(item.receiver)}${item.price!==undefined?" · Rs."+Number(item.price).toFixed(2):""}`
   : `${actorLabel(item.sender)} performed an internal decision`;
 document.getElementById("round").textContent=item.round?("Negotiation round "+item.round+" · Quantity "+item.quantity):"";
 document.getElementById("reason").textContent=item.description || "No rule explanation was recorded for this event.";
 const impact={
   DISCOVER:"The discovered sellers become eligible for separate retailer negotiations.",
   SELECT:"The retailer's selected agreement is passed to the delivery coordination stage.",
   NO_SELECTION:"No feasible negotiated supplier was found, so delivery cannot proceed.",
   VERIFY:"The coordinator checks the selected agreement against the recorded negotiation.",
   THINK:"The agent evaluates its own configured constraints. This is a recorded rule outcome, not private LLM reasoning.",
   CFP:"The delivery agent receives the coordinator's request and evaluates capacity.",
   PROPOSE:"The receiving agent evaluates this proposal using its own decision policy.",
   "ACCEPT-PROPOSAL":"This proposal has been accepted under the current agent's constraints.",
   REJECT:"The proposed action is rejected under the active constraints.",
   "REJECT-PROPOSAL":"The proposal has been rejected under the active constraints.",
   RESERVED:"The session-only ledger allocated all required resources together.",
   RESERVED_SIMULATED:"The synthetic order was reserved; no real payment, shipment or external inventory update occurred.",
   NO_AGREEMENT:"The requested order cannot advance to a successful reservation without an agreement.",
   DEMAND_EXHAUSTED:"The retailer's remaining demand is insufficient for another allocation.",
   STOCK_UNAVAILABLE:"The seller's available unreserved stock is insufficient.",
   DELIVERY_UNAVAILABLE:"The delivery agent cannot fulfill the requested simulated capacity.",
   RETAILER_DECLINED:"The retailer did not approve the total commitment.",
   RESERVATION_FAILED:"A resource validation failed, so the ledger did not create the requested reservation."
 };
 const label=item.action==="INFORM"?"The receiving agent gets the recorded information."
   :impact[item.action]||"The next recorded event determines how the workflow continues.";
 document.getElementById("impact").textContent=label;
 document.getElementById("why-title").textContent=item.kind==="message"
   ?"Why did "+actorLabel(item.sender)+" send this message?"
   :"Why did "+actorLabel(item.sender)+" make this decision?";
 document.getElementById("provenance").textContent=item.kind==="message"
    ?"Validated message from recorded simulation trace.":"Internal event derived from a recorded decision log; not a transmitted message.";
 document.getElementById("previous").disabled=index===0;
 document.getElementById("next").disabled=index===ev.length-1;
 const final=document.getElementById("final");
 if(index===ev.length-1){
   const s=model.summary;
   final.hidden=false;final.replaceChildren();
   const h=document.createElement("h2");h.textContent="Final simulated outcome · "+s.status;final.appendChild(h);
   const container=document.createElement("div");container.className="stats";
   for(const [name,val] of [["Selected supplier",s.seller],["Agreed price",s.price],
       ["Delivery quote",s.delivery],["Reserved total",s.total]]){
      const box=document.createElement("div");box.className="stat";
      const label=document.createElement("span");label.textContent=name;
      const value=document.createElement("b");value.textContent=String(name==="Selected supplier"?actorLabel(val):val);
      box.append(label,value);container.appendChild(box);
   }
   final.appendChild(container);
   const note=document.createElement("p");note.textContent=s.reason+" · No physical dispatch or payment occurs.";
   final.appendChild(note);
 }else{final.hidden=true;final.replaceChildren()}
 draw();
 requestAnimationFrame(resizeFrame);
}
function stop(){if(timer!==null){clearInterval(timer);timer=null}
 document.getElementById("toggle").textContent="▶ Play"}
function step(i){index=Math.max(0,Math.min(ev.length-1,i));show();
 if(index===ev.length-1)stop()}
function start(){stop();if(index===ev.length-1)index=0;
 show();document.getElementById("toggle").textContent="Ⅱ Pause";
 timer=setInterval(()=>step(index+1),timings[model.speed]||850)}
document.getElementById("previous").onclick=()=>{stop();step(index-1)};
document.getElementById("next").onclick=()=>{stop();step(index+1)};
document.getElementById("restart").onclick=()=>{stop();step(0)};
document.getElementById("end").onclick=()=>{stop();step(ev.length-1)};
document.getElementById("toggle").onclick=()=>timer===null?start():stop();
show();
updateFitButton();
requestAnimationFrame(resizeFrame);
// Run starts the recorded animation. Automatic full screen is attempted once,
// but browsers typically reject it without a click inside this iframe.
if(!reduced)start();
requestAnimationFrame(tryAutomaticFullscreen);
</script></body></html>'''
    return page.replace("__DATA__", payload)


def _large_evidence_table(rows: list[dict], *, columns: list[str]) -> None:
    """Readable, escaped trace table for viva projection instead of tiny canvas text."""
    if not rows:
        st.info("No evidence records available.")
        return
    st.markdown("""
    <style>
    .seq-table-wrap{overflow-x:auto;max-height:490px;overflow-y:auto;
      border:1px solid #49768f;border-radius:14px;margin:10px 0 20px}
    table.seq-table{width:100%;border-collapse:collapse;min-width:1040px;background:#122436}
    .seq-table th{position:sticky;top:0;background:#21465c;color:#bcfff1;
      font-size:20px!important;padding:16px 18px;text-align:left;z-index:1}
    .seq-table td{font-size:19px!important;padding:15px 18px;color:#f0f7fe;
      border-top:1px solid #34546c;line-height:1.5}
    .seq-table tr:nth-child(even){background:#1a3147}
    </style>
    """, unsafe_allow_html=True)
    headings = "".join("<th>" + escape(c) + "</th>" for c in columns)
    body = "".join(
        "<tr>" + "".join(
            "<td>" + escape(str(row.get(c, "") if row.get(c) is not None else "—")) + "</td>"
            for c in columns
        ) + "</tr>" for row in rows
    )
    st.markdown(
        '<div class="seq-table-wrap"><table class="seq-table">'
        "<thead><tr>" + headings + "</tr></thead><tbody>" + body +
        "</tbody></table></div>",
        unsafe_allow_html=True,
    )


def _sequence_preview_changed() -> None:
    """Mark current controls as a draft; never execute agent logic in callbacks."""
    st.session_state["seq_preview_revision"] = (
        st.session_state.get("seq_preview_revision", 0) + 1
    )


def _seller_market_snapshot(overrides: dict[str, dict] | None = None) -> MarketSnapshot:
    """A validated, isolated what-if market: seller policies are not persisted."""
    defaults = {agent.agent_id: agent for agent in build_agents() if agent.role == "seller"}
    overrides = overrides or {}
    if any(sid not in defaults for sid in overrides):
        raise ValueError("Unknown seller override.")
    stock, minimum, target = {}, {}, {}
    for sid, values in overrides.items():
        seller = defaults[sid]
        new_min = float(values["minimum_price"])
        new_target = float(values["target_price"])
        new_stock = int(values["available_stock"])
        if not (100 <= new_min <= 230 and 110 <= new_target <= 250
                and new_target >= new_min and 0 <= new_stock <= 100000):
            raise ValueError("Seller stock or prices are outside permitted demo limits.")
        stock[sid] = new_stock
        minimum[sid] = round(new_min - seller.minimum_price, 2)
        target[sid] = round(new_target - seller.target_price, 2)
    return MarketSnapshot(
        seller_stock=stock,
        seller_minimum_adjustment=minimum,
        seller_target_adjustment=target,
    )


@st.dialog("⚙ Configure Seller Agent", width="large")
def _edit_seller_popup(seller_id: str):
    """Edit isolated seller decision constraints, not public catalogue prices."""
    default = next(a for a in build_agents() if a.agent_id == seller_id)
    saved = st.session_state.get("seq_seller_overrides", {}).get(seller_id, {})
    st.markdown(f"### {_agent_label(seller_id)}")
    st.caption(
        "Viva sandbox · Changes affect the next negotiation and simulated "
        "reservation only. Existing runs and default agent definitions are unchanged."
    )
    with st.form(f"seq_seller_form_{seller_id}"):
        minimum = st.number_input(
            "Minimum acceptable price (Rs.) · private decision rule",
            min_value=100.0, max_value=230.0,
            value=float(saved.get("minimum_price", default.minimum_price)), step=5.0,
        )
        target = st.number_input(
            "Target selling price (Rs.) · private decision rule",
            min_value=110.0, max_value=250.0,
            value=float(saved.get("target_price", default.target_price)), step=5.0,
        )
        stock = st.number_input(
            "Available stock (packets)",
            min_value=0, max_value=100000,
            value=int(saved.get("available_stock", default.available_stock)), step=50,
        )
        submitted = st.form_submit_button("✓ Apply seller changes", type="primary")
    if submitted:
        current = dict(st.session_state.get("seq_seller_overrides", {}))
        current[seller_id] = {
            "minimum_price": float(minimum),
            "target_price": float(target),
            "available_stock": int(stock),
        }
        try:
            _seller_market_snapshot(current)
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.session_state["seq_seller_overrides"] = current
            _sequence_preview_changed()
            st.rerun()
    if st.button("↺ Reset seller to defaults", key=f"seq_reset_{seller_id}"):
        current = dict(st.session_state.get("seq_seller_overrides", {}))
        current.pop(seller_id, None)
        st.session_state["seq_seller_overrides"] = current
        _sequence_preview_changed()
        st.rerun()


def render_sequence_replay():
    presenting = bool(st.session_state.get("seq_presenting", False))
    if presenting and "sequence_run" not in st.session_state:
        presenting = False
        st.session_state["seq_presenting"] = False
    if not presenting:
        if st.session_state.pop("seq_restore_inputs", False):
            for key, value in st.session_state.get("seq_saved_controls", {}).items():
                st.session_state[key] = value
        st.markdown("### Configure and run a real sequence")
        st.caption(
            "A sequential synthetic simulation runs once. Only the recorded messages and "
            "decision log are replayed; playback cannot reserve resources again."
        )
        agents = {a.agent_id: a for a in build_agents()}
        listings = {item.seller_id: item for item in public_listings()}
        seller_overrides = st.session_state.get("seq_seller_overrides", {})
        market_state = _seller_market_snapshot(seller_overrides)
        scenario_sellers = {
            a.agent_id: a for a in build_agents(market_state) if a.role == "seller"
        }
        # These widgets are deliberately OUTSIDE st.form: every change reruns this
        # preview immediately. Only the explicit Run button calls _run_session().
        a, b, c = st.columns(3)
        retailer_id = a.selectbox("Retailer", ["R1", "R2"], key="seq_retailer", format_func=_agent_label, on_change=_sequence_preview_changed)
        seller_ids = b.multiselect(
            "Competing sellers", ["S1", "S2"], default=["S1", "S2"],
            key="seq_sellers", format_func=_agent_label, on_change=_sequence_preview_changed,
        )
        quantity = c.number_input(
            "Quantity (packets)", min_value=1, max_value=300,
            value=200, step=10, key="seq_quantity", on_change=_sequence_preview_changed,
        )
        d, e, f, g = st.columns(4)
        offer = d.number_input(
            "Initial offer (Rs.)", 100., 190., 150., 5., key="seq_offer", on_change=_sequence_preview_changed,
        )
        target = e.number_input(
            "Retailer target (Rs.)", 100., 190., 150., 5., key="seq_target", on_change=_sequence_preview_changed,
        )
        rounds = f.slider("Maximum rounds", 1, 10, 5, key="seq_rounds", on_change=_sequence_preview_changed)
        resale = g.number_input(
            "Assumed resale price (Rs.)", 100., 350., 200., 5.,
            key="seq_resale", on_change=_sequence_preview_changed,
        )
        speed = st.selectbox(
            "Animation speed", ["Slow", "Normal", "Fast"], index=1, key="seq_speed", on_change=_sequence_preview_changed,
        )

        buyer = agents[retailer_id]
        estimate = int(quantity) * float(offer)
        quantity_ok = quantity <= buyer.demand
        seller_ok = bool(seller_ids)
        budget_warning = estimate > buyer.budget
        estimated_margin = int(quantity) * (float(resale) - float(offer))
        can_run = seller_ok and quantity_ok

        st.markdown("""
        <style>
          .seq-profiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
            gap:18px;margin:16px 0 20px}
          .seq-profile{padding:24px 25px;min-height:250px;
            background:linear-gradient(145deg,#17364c,#225268);
            border:1px solid #4b91a6;border-radius:19px;
            box-shadow:0 12px 26px rgba(0,0,0,.25)}
          .seq-profile.buyer{background:linear-gradient(145deg,#223860,#295680)}
          .seq-profile h3{font-size:29px!important;color:white;margin:0 0 18px}
          .seq-profile p{font-size:22px!important;color:#e6f5fc;line-height:1.65;
            margin:6px 0}
          .seq-profile strong{color:#b3ffe8}
          .seq-profile.warn{border-color:#ffbd73}
          .seq-profile .status{display:inline-block;padding:6px 12px;border-radius:999px;
            font-size:17px;font-weight:750;margin-bottom:10px;
            color:#a8ffdf;background:#16483f;border:1px solid #367969}
          .seq-profile.warn .status{color:#ffe4b8;background:#604422;border-color:#c58a55}
          .seq-profile .small{font-size:17px!important;color:#bcd7e5!important}
          .seq-preview-hint{font-size:19px;color:#c0d9e7}
          @media(max-width:1000px){.seq-profiles{grid-template-columns:1fr}}
        </style>
        """, unsafe_allow_html=True)
        st.markdown("### Live scenario preview")
        profiles = ['<div class="seq-profiles">']
        profiles.append(
            '<article class="seq-profile buyer' +
            (' warn' if not quantity_ok else '') + '">'
            f'<h3>🛒 {escape(_agent_label(retailer_id))}</h3>'
            '<span class="status">' +
            ('Quantity exceeds demand' if not quantity_ok else 'Ready to evaluate') +
            '</span>'
            f'<p><strong>Current request:</strong> {int(quantity):,} packets</p>'
            f'<p><strong>Opening offer:</strong> Rs.{offer:,.2f} / packet</p>'
            f'<p><strong>Target:</strong> Rs.{target:,.2f} / packet</p>'
            f'<p><strong>Estimated opening cost:</strong> Rs.{estimate:,.2f}</p>'
            f'<p><strong>Expected gross margin at offer:</strong> Rs.{estimated_margin:,.2f}</p>'
            f'<p class="small">Agent baseline · Demand {buyer.demand:,} packets '
            f'· Budget Rs.{buyer.budget:,.2f}</p>'
            '</article>'
        )
        for sid in seller_ids:
            listing = listings[sid]
            agent = scenario_sellers[sid]
            stock_ok = int(quantity) <= agent.available_stock
            profiles.append(
                '<article class="seq-profile' + (' warn' if not stock_ok else '') + '">'
                f'<h3>🏪 {escape(_agent_label(sid))}</h3>'
                '<span class="status">' +
                ('Insufficient advertised stock' if not stock_ok else 'Stock sufficient for request') +
                '</span>'
                f'<p><strong>Current request:</strong> {int(quantity):,} packets</p>'
                f'<p><strong>Opening offer received:</strong> Rs.{offer:,.2f}</p>'
                f'<p><strong>Public asking price:</strong> Rs.{listing.listed_price:,.2f}</p>'
                f'<p><strong>Scenario stock:</strong> {agent.available_stock:,} packets</p>'
                f'<p><strong>Units after potential allocation:</strong> '
                f'{max(0, agent.available_stock - int(quantity)):,}</p>'
                f'<p class="small">Private demo policy: minimum Rs.{agent.minimum_price:,.2f}; '
                f'target Rs.{agent.target_price:,.2f}. Not exposed to other agents.</p>'
                '<p class="small">Preview only · No seller decision until Run</p>'
                '</article>'
            )
        profiles.append("</div>")
        st.markdown("".join(profiles), unsafe_allow_html=True)
        # Streamlit-native buttons open actual modal dialogs. The styled HTML
        # preview cards themselves contain no simulated/inert buttons.
        action_columns = st.columns(max(1, len(seller_ids) + 1))
        for position, sid in enumerate(seller_ids, start=1):
            with action_columns[position]:
                if st.button(
                    f"⚙ Edit {_agent_label(sid)}", key=f"seq_edit_{sid}",
                    use_container_width=True,
                ):
                    _edit_seller_popup(sid)
        if seller_overrides:
            st.info(
                "Agent policy overrides are active for this demo only. "
                "Run to see how the changed seller decisions affect negotiation."
            )
        st.caption(
            f"Scenario preview · {len(seller_ids)} selected sellers · "
            f"{rounds} maximum negotiation rounds · Rs.{resale:,.2f} "
            "assumed resale price. The preview updates when input changes are committed "
            "(use Enter or move focus after typing). Only Run executes agents."
        )
        if not seller_ok:
            st.error("Choose at least one seller to run the scenario.")
        if not quantity_ok:
            st.error(
                f"Invalid request: {retailer_id} has registered demand for only "
                f"{buyer.demand} packets, but you requested {int(quantity)}. "
                f"Reduce the requested quantity by {int(quantity)-buyer.demand} packets "
                "or choose another retailer."
            )
        if budget_warning:
            st.warning(
                f"Estimated purchase cost at the opening offer is Rs.{estimate:,.2f}, "
                f"above {retailer_id}'s Rs.{buyer.budget:,.2f} budget. "
                "A feasible negotiation may still be impossible."
            )
        run = st.button(
            "▶ Run and animate agent sequence", type="primary",
            disabled=not can_run, use_container_width=True,
            key="seq_run",
        )
        if run:
            try:
                run_result = _run_session(
                    retailer_id=retailer_id, seller_ids=seller_ids,
                    quantity=int(quantity), initial_price=float(offer),
                    target=float(target), rounds=rounds, resale_price=float(resale),
                    market_state=market_state,
                )
                run_result["sequence_events"] = _sequence_events(run_result)
                run_result["sequence_speed"] = speed
                st.session_state["sequence_run"] = run_result
                st.session_state["seq_last_run_revision"] = st.session_state.get("seq_preview_revision", 0)
                st.session_state["seq_saved_controls"] = {
                    "seq_retailer": retailer_id,
                    "seq_sellers": list(seller_ids),
                    "seq_quantity": int(quantity),
                    "seq_offer": float(offer),
                    "seq_target": float(target),
                    "seq_rounds": int(rounds),
                    "seq_resale": float(resale),
                    "seq_speed": speed,
                }
                st.session_state["seq_presenting"] = True
                st.rerun()
            except (ValueError, RuntimeError, KeyError) as exc:
                st.error(f"Sequence execution failed: {exc}")

    else:
        st.markdown("""
        <style>
          /* Presentation mode uses the area previously occupied by the config cards. */
          [data-testid="stAppViewBlockContainer"]{padding-top:.7rem!important}
          [data-testid="stVerticalBlock"]{gap:.65rem!important}
        </style>
        """, unsafe_allow_html=True)
        left, right = st.columns([3, 1])
        with left:
            st.markdown("### ▶ Recorded Multi-Agent Sequence")
            st.caption(
                "Presentation mode · configuration and preview hidden. "
                "Playback controls do not execute the agents again."
            )
        with right:
            if st.button(
                "✎ Edit Scenario", key="seq_edit_scenario",
                use_container_width=True,
            ):
                st.session_state["seq_presenting"] = False
                st.session_state["seq_restore_inputs"] = True
                st.rerun()
     result = st.session_state.get("sequence_run")
    if result is None:
        st.info("Select agents and press Run to generate the full recorded sequence.")
        return
    saved = result["params"]
    if not st.session_state.get("seq_presenting", False) and (
        saved["retailer_id"] != retailer_id or saved["seller_ids"] != seller_ids
        or saved["quantity"] != int(quantity)
        or saved["initial_price"] != float(offer)
        or saved["target"] != float(target) or saved["rounds"] != rounds
        or saved["resale_price"] != float(resale)
    ):
        st.warning(
            "Your live agent cards show the CURRENT draft configuration. "
            "The sequence diagram below still shows the LAST completed run. "
            "Click Run and animate agent sequence to update the recorded evidence."
        )
    st.markdown("### Animated message sequence")
    selected = result["competition"]["evaluated_seller_ids"]
    # Keep actor columns grounded in the selected scenario. The coordinator
    # and D1 remain visible to explain the subsequent delivery phase.
    lifelines = [result["params"]["retailer_id"], *selected, "C1", "D1"]
    selection = result["competition"]["selection"]
    outcome = result["coordination"]
    reservation = outcome["reservation"]
    summary = {
        "status": outcome["status"],
        "seller": selection["selected_seller_id"] or "None",
        "price": (f"Rs.{selection['selected_price']:,.2f}"
                  if selection["selected_price"] is not None else "No agreement"),
        "delivery": (f"Rs.{outcome['delivery_fee']:,.2f}"
                     if outcome["delivery_fee"] is not None else "Not quoted"),
        "total": (f"Rs.{reservation['reserved_total']:,.2f}"
                  if reservation else "Not reserved"),
        "reason": outcome["reason"],
    }
    sequence_document = _sequence_html(
        result["sequence_events"], lifelines, summary, result["sequence_speed"]
    )
    components.html(sequence_document, height=900, scrolling=True)
    st.download_button(
        "⬇ Download Standalone Full-Screen Replay (HTML)",
        data=sequence_document,
        file_name="SMEConnect_Sequence_Replay.html",
        mime="text/html",
        help="Open the downloaded HTML file in Chrome or Edge. "
             "It includes the recorded animation and Full Screen button without "
             "Streamlit iframe permissions. No external simulation is executed.",
        key="seq_download_fullscreen",
    )
    with st.expander("Technical evidence — actual messages and decision logs"):
        _large_evidence_table(
            result["sequence_events"],
            columns=["phase", "kind", "sender", "receiver", "action", "description",
                     "round", "price", "quantity"],
        )
        st.markdown("### Computed supplier evaluation")
        _large_evidence_table(
            result["competition"]["selection"]["evaluations"],
            columns=["seller_id", "negotiation_status", "price", "purchase_cost",
                     "expected_gross_profit", "eligible", "explanation"],
        )
        messages = []
        for sid in selected:
            messages.extend(result["competition"]["negotiations"][sid]["messages"])
        messages.extend(outcome["messages"])
        st.json([m.model_dump(mode="json") for m in messages])
    st.caption(
        "The sequence reveals genuine recorded interactions. Summary/decision cards are "
        "not messages. Agents run sequentially; no real payments or shipments occur."
    )
