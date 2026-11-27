"""Animated, English-only multi-agent sequence replay.

Runs existing MAS policies once through the workflow simulator and presents
recorded events in a client-side, pauseable SVG sequence diagram. Rendering and
replay do not make additional bookings or change agent state.
"""
from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components

from dashboard.workflow_simulator import _run_session
from smeconnect.environment.marketplace import build_agents
from smeconnect.environment.catalogue import public_listings


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
    }, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    page = r'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{color-scheme:dark;--ink:#eaf6fc;--muted:#acc5d6;--teal:#69ebd8;--line:#4d7490}
*{box-sizing:border-box}
body{margin:0;background:#0e1a2c;color:var(--ink);font:21px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}
.shell{background:linear-gradient(140deg,#11243b,#12364b);border:1px solid #3c7591;border-radius:20px;padding:20px;min-height:840px}
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
.diagram{height:488px;overflow:auto;border:1px solid #44687f;border-radius:16px;background:
radial-gradient(circle at 50% 20%,#163a54,#0d1e34);scroll-behavior:smooth}
svg{display:block;width:100%;min-width:720px}
.detail{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.45fr);gap:18px;margin-top:20px;align-items:stretch}
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
.final{margin-top:14px;padding:18px 21px;border:1px solid #5dbaaa;border-radius:15px;
background:linear-gradient(110deg,#174f4d,#173c52)}
.final h2{margin:0 0 10px;font-size:31px}
.stats{display:flex;gap:18px;flex-wrap:wrap}
.stat{min-width:150px;flex:1;padding:10px;background:#ffffff10;border-radius:10px}
.stat span{display:block;color:#c6e2ec;font-size:20px}.stat b{display:block;font-size:30px}
.small{font-size:18px!important;color:#c3dce7!important;line-height:1.5!important}
@media(max-width:850px){.detail{grid-template-columns:1fr}.shell{padding:13px}h1{font-size:22px}
.diagram{height:450px}button{font-size:18px;padding:10px 13px}.panel p{font-size:20px}.panel h2{font-size:24px}}
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
<button id="end">Show final result</button></div>
<div class="diagram" id="viewport"><svg id="sequence" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sequence of recorded agent interactions"></svg></div>
<div class="detail">
<section class="panel"><div class="kicker">CURRENT EVENT</div><h2 id="title"></h2>
<p id="message"></p><p id="round"></p></section>
<section class="panel" id="decision-panel" aria-live="polite">
<div class="kicker">AGENT DECISION EXPLAINED</div><h2 id="why-title">Why did it happen?</h2>
<p id="reason"></p><div class="explain-extra"><strong id="impact-label">What happened next?</strong>
<p id="impact"></p></div><p class="small" id="provenance"></p></section>
</div><section id="final" class="final" hidden></section></main>
<script>
const model=__DATA__;
const ev=model.events,actors=model.actors;
const svg=document.getElementById("sequence"),viewport=document.getElementById("viewport");
const ns="http://www.w3.org/2000/svg",left=105,right=1120;
const x=i=>left+i*(right-left)/Math.max(actors.length-1,1);
const H=166+ev.length*94;
const chosen=new Map(actors.map((v,i)=>[v,i]));
let index=0,timer=null;
const timings={Slow:1400,Normal:850,Fast:400};
const reduced=window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
function element(tag,attrs={},text=""){
 const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));
 if(text)e.textContent=String(text);return e;
}
function append(parent,tag,attrs,text){const el=element(tag,attrs,text);parent.appendChild(el);return el}
function isMsg(item){return item.kind==="message" && chosen.has(item.sender)&&chosen.has(item.receiver)}
function draw(){
 svg.replaceChildren();svg.setAttribute("viewBox",`0 0 1220 ${H}`);
 svg.setAttribute("height",String(H));
 const defs=append(svg,"defs");
 const marker=append(defs,"marker",{id:"arrow",markerWidth:10,markerHeight:9,refX:9,refY:4,orient:"auto",markerUnits:"strokeWidth"});
 append(marker,"path",{d:"M0,0 L9,4 L0,8 Z",fill:"#60c8d0"});
 const activeMarker=append(defs,"marker",{id:"arrow-active",markerWidth:11,markerHeight:10,refX:9,refY:5,orient:"auto",markerUnits:"strokeWidth"});
 append(activeMarker,"path",{d:"M0,0 L10,5 L0,10 Z",fill:"#94fff0"});
 actors.forEach((agent,j)=>{
   const cx=x(j);
   append(svg,"rect",{x:cx-91,y:20,width:182,height:61,rx:12,fill:"#24526c",stroke:"#6db3cb","stroke-width":1.5});
   append(svg,"text",{x:cx,y:58,"font-size":22,"font-weight":750,"text-anchor":"middle",fill:"#fff"},agent);
   append(svg,"line",{x1:cx,y1:82,x2:cx,y2:H-28,stroke:"#567d96","stroke-dasharray":"7 7","stroke-width":1.5});
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
 const focusY=135+index*94;
 if(reduced){viewport.scrollTop=Math.max(0,focusY-240)}
 else viewport.scrollTo({top:Math.max(0,focusY-240),behavior:"smooth"});
}
function show(){
 const item=ev[index];
 document.getElementById("counter").textContent=`Event ${index+1} of ${ev.length}`;
 document.getElementById("title").textContent=`${item.phase} · ${item.action}`;
 document.getElementById("message").textContent=item.kind==="message"
   ? `${item.sender} → ${item.receiver}${item.price!==undefined?" · Rs."+Number(item.price).toFixed(2):""}`
   : `${item.sender} performed an internal decision`;
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
   ?"Why did "+item.sender+" send this message?"
   :"Why did "+item.sender+" make this decision?";
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
      const value=document.createElement("b");value.textContent=String(val);
      box.append(label,value);container.appendChild(box);
   }
   final.appendChild(container);
   const note=document.createElement("p");note.textContent=s.reason+" · No physical dispatch or payment occurs.";
   final.appendChild(note);
 }else{final.hidden=true;final.replaceChildren()}
 draw();
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
if(!reduced)start();
</script></body></html>'''
    return page.replace("__DATA__", payload)


def render_sequence_replay():
    st.markdown("### Configure and run a real sequence")
    st.caption(
        "A sequential synthetic simulation runs once. Only the recorded messages and "
        "decision log are replayed; playback cannot reserve resources again."
    )
    agents = {a.agent_id: a for a in build_agents()}
    listings = {item.seller_id: item for item in public_listings()}
    with st.form("sequence_config"):
        a, b, c = st.columns(3)
        retailer_id = a.selectbox("Retailer", ["R1", "R2"], key="seq_retailer")
        seller_ids = b.multiselect("Competing sellers", ["S1", "S2"],
                                   default=["S1", "S2"], key="seq_sellers")
        quantity = c.number_input("Quantity (packets)", min_value=1,
                                  max_value=300, value=200, step=10)
        d, e, f, g = st.columns(4)
        offer = d.number_input("Initial offer (Rs.)", 100., 190., 150., 5.)
        target = e.number_input("Retailer target (Rs.)", 100., 190., 150., 5.)
        rounds = f.slider("Maximum rounds", 1, 10, 5)
        resale = g.number_input("Assumed resale price (Rs.)", 100., 350., 200., 5.)
        speed = st.selectbox("Animation speed", ["Slow", "Normal", "Fast"], index=1)
        run = st.form_submit_button("▶ Run and animate agent sequence",
                                    type="primary", use_container_width=True)
    st.markdown("#### Selected agents")
    columns = st.columns(max(1, len(seller_ids)+1))
    buyer = agents[retailer_id]
    with columns[0]:
        with st.container(border=True):
            st.markdown(f"### 🛒 {retailer_id}")
            st.write(f"Budget: Rs.{buyer.budget:,.2f} · Demand: {buyer.demand} packets")
    for column, seller_id in zip(columns[1:], seller_ids):
        listing = listings[seller_id]
        with column:
            with st.container(border=True):
                st.markdown(f"### 🏪 {seller_id}")
                st.write(f"Public price: Rs.{listing.listed_price:,.2f}")
                st.write(f"Advertised stock: {listing.advertised_stock} packets")
    if run:
        if not seller_ids:
            st.error("Select at least one seller.")
        elif quantity > buyer.demand:
            st.error(f"Quantity exceeds {retailer_id}'s demand of {buyer.demand}.")
        else:
            try:
                run_result = _run_session(
                    retailer_id=retailer_id, seller_ids=seller_ids,
                    quantity=int(quantity), initial_price=float(offer),
                    target=float(target), rounds=rounds, resale_price=float(resale),
                )
                run_result["sequence_events"] = _sequence_events(run_result)
                run_result["sequence_speed"] = speed
                st.session_state["sequence_run"] = run_result
            except (ValueError, RuntimeError, KeyError) as exc:
                st.error(f"Sequence execution failed: {exc}")
    result = st.session_state.get("sequence_run")
    if result is None:
        st.info("Select agents and press Run to generate the full recorded sequence.")
        return
    saved = result["params"]
    if (saved["retailer_id"] != retailer_id or saved["seller_ids"] != seller_ids
            or saved["quantity"] != int(quantity)
            or saved["initial_price"] != float(offer)
            or saved["target"] != float(target) or saved["rounds"] != rounds
            or saved["resale_price"] != float(resale)):
        st.warning("Configuration changed. The diagram still shows the last completed run. Press Run to update.")
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
    components.html(
        _sequence_html(result["sequence_events"], lifelines, summary,
                       result["sequence_speed"]),
        height=905, scrolling=False,
    )
    with st.expander("Technical evidence — actual messages and decision logs"):
        st.dataframe(result["sequence_events"], use_container_width=True, hide_index=True)
        st.write("**Computed supplier evaluation:**")
        st.dataframe(result["competition"]["selection"]["evaluations"],
                     use_container_width=True, hide_index=True)
        messages = []
        for sid in selected:
            messages.extend(result["competition"]["negotiations"][sid]["messages"])
        messages.extend(outcome["messages"])
        st.json([m.model_dump(mode="json") for m in messages])
    st.caption(
        "The sequence reveals genuine recorded interactions. Summary/decision cards are "
        "not messages. Agents run sequentially; no real payments or shipments occur."
    )
