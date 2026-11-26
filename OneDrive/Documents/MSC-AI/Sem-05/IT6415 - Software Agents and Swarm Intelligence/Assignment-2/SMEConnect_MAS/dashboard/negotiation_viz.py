"""Visual-only neon negotiation scene for Streamlit.

Render recorded simulation events, NOT fabricated AI thinking or a separate engine.
No external CSS/JS/CDN dependencies; agent "thinking" is a rule explanation.
"""
from __future__ import annotations

from html import escape


def _safe(value: object) -> str:
    return escape(str(value), quote=True)


def _thinking(event: dict, is_initial: bool) -> tuple[str, str, str, str]:
    """Describe the CURRENT agent's documented rule checks, not private chain of thought."""
    sender = str(event["sender"])
    act = str(event["performative"])
    if is_initial:
        return (
            "Operator-configured first proposal",
            "Input: chosen unit price and quantity",
            "The retailer sends this starting offer to the seller.",
            "Seller evaluates this message next.",
        )
    if sender.startswith("S"):
        if act == "PROPOSE":
            return (
                "Check requested quantity vs. stock",
                "Compare offered price with seller's minimum",
                "Compare offered price with target",
                "Result: propose a higher unit price",
            )
        if act == "ACCEPT-PROPOSAL":
            return (
                "Check requested quantity vs. stock",
                "Compare offered price with seller's minimum",
                "Compare offered price with target",
                "Result: accept the retailer offer",
            )
        return (
            "Check requested quantity vs. stock",
            "Check seller's minimum acceptable price",
            "Constraint not satisfied",
            "Result: reject offer",
        )
    if act == "ACCEPT-PROPOSAL":
        return (
            "Check quantity against demand",
            "Check available budget and maximum price",
            "Evaluate expected gross profit",
            "Result: accept seller's offer",
        )
    if act == "REJECT-PROPOSAL":
        return (
            "Check quantity against demand",
            "Check available budget and maximum price",
            "Evaluate expected gross profit",
            "Result: reject infeasible offer",
        )
    return (
        "Check quantity against demand",
        "Check available budget and maximum price",
        "Compare price with this round's target",
        "Result: propose a lower price",
    )


def neon_scene(timeline: list[dict], index: int, buyer: str, seller: str) -> str:
    """An animated, data-driven message visualization; no script execution."""
    if not timeline:
        return '<div class="neon-scene">No recorded negotiation events.</div>'
    index = max(0, min(index, len(timeline) - 1))
    current = timeline[index]
    sender = str(current["sender"])
    buyer_active = sender == buyer
    initial = index == 0
    action = str(current["performative"])
    price = float(current["price"])
    thinking = _thinking(current, initial)
    reason = _safe(current.get("reason", ""))
    action_label = (
        "ACCEPT" if action == "ACCEPT-PROPOSAL"
        else "REJECT" if action == "REJECT-PROPOSAL"
        else "COUNTER-OFFER" if index > 0
        else "PROPOSE"
    )
    steps = "".join(
        '<span class="neon-pill{active}"><span>{number}</span> {sender} · {action} · Rs.{price}</span>'.format(
            active=" on" if k == index else "",
            number=k + 1,
            sender=_safe(item["sender"]),
            action=_safe(
                "ACCEPT" if item["performative"] == "ACCEPT-PROPOSAL"
                else "REJECT" if item["performative"] == "REJECT-PROPOSAL"
                else "COUNTER" if k > 0 else "PROPOSE"
            ),
            price=_safe(item["price"]),
        )
        for k, item in enumerate(timeline)
    )

    # SVG paths communicate direction accurately. Only the selected path animates.
    # The other two arcs are visual context, not claims that there are always 3 events.
    forward = buyer_active
    path = "M 248 112 Q 500 5 752 112" if forward else "M 752 196 Q 500 304 248 196"
    arrow_x = "752" if forward else "248"
    arrow_y = "112" if forward else "196"
    panel_buyer = " thinking-live" if buyer_active else ""
    panel_seller = " thinking-live" if not buyer_active else ""
    buyer_thoughts = thinking if buyer_active else (
        "Private budget and demand",
        "Target price and maximum price",
        "Expected gross profit",
        "Independent retailer decisions",
    )
    seller_thoughts = thinking if not buyer_active else (
        "Private stock and minimum price",
        "Target unit price",
        "Own seller decision graph",
        "Independent seller decisions",
    )
    def thoughts(rows: tuple[str, ...]) -> str:
        return "".join('<li><span class="thought-dot"></span>{}</li>'.format(_safe(t)) for t in rows)

    return f"""
<div class="neon-scene" role="group" aria-label="Agent negotiation event {index + 1} of {len(timeline)}">
  <style>
  .neon-scene{{background:radial-gradient(ellipse at 50% 58%,#153f73 0%,#0b1937 55%,#070f22 100%);color:#e9f7ff;
    border:1px solid #21618d;border-radius:22px;padding:22px;overflow:hidden;position:relative;isolation:isolate;
    box-shadow:inset 0 0 80px #0285cc22,0 16px 35px #0003}}
  .neon-scene:before{{content:"";position:absolute;inset:0;z-index:-1;opacity:.18;
    background-image:linear-gradient(#35baff22 1px,transparent 1px),linear-gradient(90deg,#35baff22 1px,transparent 1px);
    background-size:34px 34px;transform:perspective(380px) rotateX(13deg) scale(1.1)}}
  .neon-head{{text-align:center;font-size:18px;font-weight:850;letter-spacing:.035em;text-shadow:0 0 15px #36cdff60}}
  .neon-sub{{text-align:center;font-size:12px;color:#9ad5ef;margin:6px 0 14px}}
  .neon-layout{{display:grid;grid-template-columns:minmax(0,1fr) 1.65fr minmax(0,1fr);gap:12px;align-items:center}}
  .neon-column{{display:flex;flex-direction:column;gap:13px;min-width:0}}
  .think-panel{{border:1px solid #3378a2;background:linear-gradient(155deg,#122b54de,#09223dcc);
    border-radius:15px;padding:14px;min-height:171px;box-shadow:inset 0 0 18px #2b9cef24}}
  .think-panel.thinking-live{{border-color:#35e6f6;box-shadow:0 0 24px #00d6ff52,inset 0 0 20px #00d6ff20}}
  .think-title{{font-size:13px;font-weight:750;color:#7ce7ff;margin-bottom:10px}}
  .think-panel ul{{list-style:none;margin:0;padding:0}}
  .think-panel li{{font-size:11px;line-height:1.4;display:flex;gap:7px;align-items:flex-start;margin:6px 0;color:#d7eaf9}}
  .thought-dot{{display:inline-block;width:6px;height:6px;border-radius:50%;background:#55e9fe;flex:0 0 6px;margin-top:5px;box-shadow:0 0 8px #33edff}}
  .robot-card{{border:1px solid #347bb0;border-radius:16px;text-align:center;padding:15px 9px;
    background:linear-gradient(155deg,#173e6b,#111b44);box-shadow:inset 0 0 20px #36bdfc2b}}
  .robot-card.live{{box-shadow:0 0 24px #21bdfc42,inset 0 0 22px #36bdfc3d}}
  .robot{{width:76px;height:72px;margin:0 auto 11px;position:relative}}
  .robot-head{{width:66px;height:51px;position:absolute;left:5px;top:3px;border-radius:27px 27px 20px 20px;
    background:linear-gradient(140deg,#f9fdff,#97d1ff);box-shadow:0 0 17px #64ccff9c}}
  .robot-face{{position:absolute;left:12px;top:16px;width:42px;height:23px;background:#0b1e40;border-radius:15px}}
  .robot-eye{{width:6px;height:7px;border-radius:50%;background:#33f6ff;position:absolute;top:8px;box-shadow:0 0 10px cyan}}
  .robot-eye.left{{left:11px}}.robot-eye.right{{right:11px}}
  .robot-base{{position:absolute;left:11px;bottom:0;width:54px;height:16px;border-radius:7px;background:#3c91e7;
    box-shadow:0 0 15px #35bfff}}
  .robot-card strong{{font-size:14px;display:block;word-break:break-word}}
  .robot-card small{{color:#9bd6ed;font-size:10px}}
  .neon-center{{text-align:center;min-width:0;position:relative}}
  .neon-bubble{{font-size:12px;font-weight:850;background:#0e4b78;border:1px solid #48cffe;padding:9px 13px;
    display:inline-block;border-radius:20px;box-shadow:0 0 18px #00bbff44;margin-bottom:8px}}
  .neon-center svg{{width:100%;height:auto;max-height:220px;display:block;margin:0 auto}}
  .neon-center .path-active{{stroke-dasharray:13 9;animation:neon-flow 1.2s linear infinite;
    filter:drop-shadow(0 0 7px #40e6ff)}}
  @keyframes neon-flow{{to{{stroke-dashoffset:-44}}}}
  .neon-price{{color:#85edff;font-size:11px}}
  .neon-reason{{border:1px solid #326a91;background:#0a2747bc;border-radius:12px;
    margin-top:18px;padding:13px 16px;font-size:12px;line-height:1.6}}
  .neon-label{{color:#6ee6f6;font-weight:800}}
  .neon-pills{{display:flex;flex-wrap:wrap;gap:7px;margin-top:13px}}
  .neon-pill{{border:1px solid #265678;background:#133956;color:#badbea;border-radius:18px;font-size:10px;
    padding:7px 10px;white-space:normal}}
  .neon-pill.on{{background:#146d80;border-color:#55eaf9;color:white;box-shadow:0 0 12px #08ddf955}}
  .neon-pill span{{font-weight:800;margin-right:4px}}
  @media(max-width:730px){{.neon-layout{{grid-template-columns:1fr 1fr}}.neon-center{{grid-column:1/-1;grid-row:2}}
    .think-panel{{min-height:165px}}.neon-column{{grid-row:1}}}}
  @media(prefers-reduced-motion:reduce){{.neon-center .path-active{{animation:none}}}}
  </style>
  <div class="neon-head">🤖 Two-Agent Negotiation System</div>
  <div class="neon-sub">LangGraph decisions · Structured messages · Explanations, not hidden LLM thoughts</div>
  <div class="neon-layout">
    <div class="neon-column">
      <div class="think-panel{panel_buyer}">
        <div class="think-title">🧠 Retailer Thinking</div><ul>{thoughts(buyer_thoughts)}</ul>
      </div>
      <div class="robot-card{' live' if buyer_active else ''}">
        <div class="robot"><div class="robot-head"><div class="robot-face">
          <span class="robot-eye left"></span><span class="robot-eye right"></span>
        </div></div><div class="robot-base"></div></div>
        <strong>🛒 Retailer {_safe(buyer)}</strong><small>Independent purchasing goals</small>
      </div>
    </div>
    <div class="neon-center">
      <span class="neon-bubble">Step {index + 1}: {_safe(action_label)} · Rs.{price:,.2f}</span>
      <svg viewBox="0 0 1000 310" xmlns="http://www.w3.org/2000/svg" aria-label="Message direction">
        <defs><marker id="neon-arrow-{index}" markerWidth="13" markerHeight="13" refX="10" refY="5" orient="auto">
          <path d="M0 0 L10 5 L0 10 Z" fill="#69e9ff"/></marker></defs>
        <path d="M 248 112 Q 500 5 752 112" stroke="#1595bd" stroke-width="6" fill="none" opacity=".18"/>
        <path d="M 752 196 Q 500 304 248 196" stroke="#8b6ffa" stroke-width="6" fill="none" opacity=".18"/>
        <path d="{path}" stroke="#56e7ff" stroke-width="8" fill="none"
           class="path-active" marker-end="url(#neon-arrow-{index})"/>
        <circle cx="{arrow_x}" cy="{arrow_y}" r="12" fill="#9cf5ff" opacity=".85"/>
        <g font-family="Arial,sans-serif" fill="#b8e8ff" font-size="36" text-anchor="middle">
          <text x="500" y="142">MESSAGE BUS</text>
        </g>
      </svg>
      <div class="neon-price">{_safe(sender)} → {_safe(current['receiver'])} · Round {_safe(current['round'])}</div>
    </div>
    <div class="neon-column">
      <div class="think-panel{panel_seller}">
        <div class="think-title">🧠 Seller Thinking</div><ul>{thoughts(seller_thoughts)}</ul>
      </div>
      <div class="robot-card{' live' if not buyer_active else ''}">
        <div class="robot"><div class="robot-head"><div class="robot-face">
          <span class="robot-eye left"></span><span class="robot-eye right"></span>
        </div></div><div class="robot-base"></div></div>
        <strong>🏪 Seller {_safe(seller)}</strong><small>Independent sales goals</small>
      </div>
    </div>
  </div>
  <div class="neon-reason">
    <span class="neon-label">Decision explanation · </span>{reason}<br/>
    <span class="neon-label">What happened · </span>{_safe(sender)} sent {_safe(action_label)} at Rs.{price:,.2f}.
  </div>
  <div class="neon-pills">{steps}</div>
</div>
