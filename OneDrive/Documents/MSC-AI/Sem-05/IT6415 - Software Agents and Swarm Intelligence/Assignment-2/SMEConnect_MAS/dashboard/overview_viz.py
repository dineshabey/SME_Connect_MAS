"""Modern, explainable landing experience for the SMEConnect AI academic demo.

Only confirmed agent registry information and actual experiment outputs appear.
"""
import html

import streamlit as st

from dashboard.ui_design import PAGES, navigate_to
from smeconnect.environment.marketplace import build_agents
from smeconnect.environment.market_state import SCENARIO_NAMES
from smeconnect.simulation.market_experiment import run_market_experiment


AGENT_DESCRIPTIONS = (
    ("S1", "🏪", "Margin-focused seller", "Protects its own pricing and stock limits", "Seller"),
    ("S2", "📦", "Volume-focused seller", "Accepts eligible bulk orders under its rules", "Seller"),
    ("R1", "🛒", "Cost-focused retailer", "Negotiates offers and evaluates gross profit", "Retailer"),
    ("R2", "🛍️", "Availability-focused retailer", "Buys within its budget and demand limits", "Retailer"),
    ("D1", "🚚", "Delivery service", "Checks delivery capacity and quotes a trip fee", "Delivery"),
    ("M1", "📡", "Market observer", "Shares changes through validated messages", "Market"),
    ("C1", "🧭", "Coordinator", "Discovers suppliers and coordinates reservations", "Coordinator"),
)


NETWORK_CSS = """
<style>
.smc-network{
    background:linear-gradient(125deg,#14243a,#113448);
    border:1px solid #375b71;
    border-radius:17px;
    padding:22px clamp(16px,2vw,35px);
}
.smc-network .group{
    display:grid;gap:18px;
    grid-template-columns:repeat(2,minmax(0,1fr));
}
.smc-network .group.three{
    grid-template-columns:repeat(3,minmax(0,1fr));
}
.smc-network .node{
    background:rgba(31,82,105,.68);
    border:1px solid #4f96aa;
    border-radius:13px;
    padding:17px 14px;
    text-align:center;
    min-width:0;
}
.smc-network .node b{display:block;font-size:22px;color:#f4faff}
.smc-network .node span{font-size:16px;color:#bcd8e4}
.smc-network .connector{
    display:flex;gap:12px;justify-content:center;align-items:center;
    padding:12px 8px;color:#82d8df;font-size:16px;font-weight:700;
}
.smc-network .connector::before,
.smc-network .connector::after{
    content:"";display:block;height:1px;background:#40768a;flex:1;
}
.smc-network .foot{
    margin-top:15px;text-align:center;color:#aac3d2;
    font-size:14px;
}
@media(max-width:700px){
  .smc-network .group.three{grid-template-columns:1fr}
  .smc-network .node b{font-size:18px}
  .smc-network .node span{font-size:14px}
  .smc-network .connector{font-size:13px}
}
</style>
"""


def _network():
    """A conceptual network, clearly distinguished from runtime messages."""
    st.markdown(NETWORK_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="smc-network">'
        '<div class="group">'
        '<div class="node"><b>🏪 S1 · Margin seller</b><span>Independent seller negotiation</span></div>'
        '<div class="node"><b>📦 S2 · Volume seller</b><span>Independent bulk-order policy</span></div>'
        '</div>'
        '<div class="connector">PROPOSE · ACCEPT · REJECT</div>'
        '<div class="group">'
        '<div class="node"><b>🛒 R1 · Cost retailer</b><span>Negotiates and selects supplier</span></div>'
        '<div class="node"><b>🛍️ R2 · Demand retailer</b><span>Independent financial constraints</span></div>'
        '</div>'
        '<div class="connector">DELIVERY QUOTES · MARKET SIGNALS</div>'
        '<div class="group three">'
        '<div class="node"><b>🚚 D1 · Delivery</b><span>Trip capacity and fee</span></div>'
        '<div class="node"><b>📡 M1 · Market</b><span>Scenario notifications</span></div>'
        '<div class="node"><b>🧭 C1 · Coordinator</b><span>Discovery and reservations</span></div>'
        '</div>'
        '<div class="foot">Conceptual agent roles; view recorded messages inside the relevant workspace.</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _workspace_card(title, description, page, button_text):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.caption(description)
        st.button(
            button_text,
            key="overview_open_" + str(PAGES.index(page)),
            use_container_width=True,
            on_click=navigate_to,
            args=(page,),
        )


def _result_card(title: str, data: dict):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        left, right = st.columns(2)
        left.metric("Selected supplier", data["selected_seller"] or "None")
        right.metric(
            "Agreed unit price",
            f"Rs. {data['agreed_price']:,.2f}"
            if data["agreed_price"] is not None else "No agreement",
        )
        st.metric("Expected gross profit", f"Rs. {data['expected_gross_profit']:,.2f}")
        st.caption("Provisional agreement · no order committed")


def render_overview() -> None:
    agents = build_agents()
    sellers = [a for a in agents if a.role == "seller"]
    retailers = [a for a in agents if a.role == "retailer"]

    st.markdown("### Marketplace at a glance")
    a, b, c, d = st.columns(4)
    for col, title, value, help_text in (
        (a, "Registered agents", len(agents), "Synthetic registered agents from the Python registry"),
        (b, "Independent sellers", len(sellers), "S1 and S2 negotiate separately"),
        (c, "Retailer agents", len(retailers), "Independent budget and demand constraints"),
        (d, "Market shocks", len(SCENARIO_NAMES) - 1, "Controlled synthetic market events"),
    ):
        with col:
            with st.container(border=True):
                st.metric(title, value, help=help_text)

    main, helper = st.columns([1.75, 1], gap="large")
    with main:
        st.markdown("### How the agents collaborate")
        _network()
    with helper:
        st.markdown("### Quick start")
        with st.container(border=True):
            st.markdown("**01 · Explore marketplace**")
            st.caption("See public listing prices and supplier availability.")
            st.button("Open Marketplace", use_container_width=True,
                      key="quick_market", on_click=navigate_to, args=(PAGES[1],))
            st.divider()
            st.markdown("**02 · Watch autonomous negotiation**")
            st.caption("Compare seller offers and the retailer's selected supplier.")
            st.button("Open Competition", use_container_width=True,
                      key="quick_compete", on_click=navigate_to, args=(PAGES[2],))
            st.divider()
            st.markdown("**03 · Evaluate the market**")
            st.caption("Compare controlled market shocks and measured responses.")
            st.button("Open Analytics", use_container_width=True,
                      key="quick_experiment", on_click=navigate_to, args=(PAGES[5],))
        st.caption("You can reach all nine workspaces through the sidebar.")

    st.markdown("### Meet the agents")
    for i in range(0, len(AGENT_DESCRIPTIONS), 4):
        cols = st.columns(4)
        for col, (agent_id, emoji, title, detail, role) in zip(cols, AGENT_DESCRIPTIONS[i:i+4]):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{emoji} {agent_id} · {title}**")
                    st.caption(detail)
                    st.markdown(f'<span class="smc-tag">{html.escape(role.upper())}</span>',
                                unsafe_allow_html=True)

    st.markdown("### Interactive demo · What happens during a stock shortage?")
    with st.container(border=True):
        st.write(
            "Run an **actual supplier-selection experiment** with the existing "
            "LangGraph rules. Both conditions use R1, 200 packets, a Rs.150 opening "
            "offer and five maximum rounds."
        )
        if st.button("▶ Run stock-shortage scenario", type="primary",
                     key="professor_demo_run", use_container_width=True):
            try:
                st.session_state["professor_demo_outcome"] = run_market_experiment(
                    scenario="s2_shortage", retailer_id="R1",
                    quantity=200, initial_price=150.0,
                    retailer_target=150.0, max_rounds=5,
                )
            except (ValueError, RuntimeError, PermissionError) as exc:
                st.session_state.pop("professor_demo_outcome", None)
                st.error(f"Simulation stopped: {exc}")
        outcome = st.session_state.get("professor_demo_outcome")
        if outcome:
            c1, c2 = st.columns(2, gap="large")
            with c1:
                _result_card("Normal market", outcome["before"])
            with c2:
                _result_card("After S2 stock shortage", outcome["after"])
            if outcome["before"]["selected_seller"] != outcome["after"]["selected_seller"]:
                st.success("Supplier selection changed because the agents evaluated new market constraints.")
            else:
                st.info("Supplier selection remained unchanged for these inputs.")
            with st.expander("🔎 Inspect real agent messages and decisions"):
                st.markdown(f"**Market M1:** {outcome['market_signal']['summary']}")
                for label, key in (("Before", "baseline"), ("After", "changed")):
                    st.markdown(f"**{label} market — recorded seller negotiations**")
                    for sid, run in outcome[key]["negotiations"].items():
                        st.markdown(f"**{sid}** · {run['status']} · {len(run['messages'])} messages")
                        st.dataframe(run["timeline"], hide_index=True,
                                     use_container_width=True)
            st.caption("Rule-based adaptation only. No payments, bookings, learned policy or real market feeds.")

    st.markdown("### Explore other workflows")
    one, two, three = st.columns(3)
    with one:
        _workspace_card("🚚 Delivery coordination", "Validate stock, delivery capacity and budget.",
                        PAGES[3], "Explore delivery")
    with two:
        _workspace_card("📈 Market adaptation", "Compare the before/after state of simulated markets.",
                        PAGES[4], "Explore market changes")
    with three:
        _workspace_card("💬 Guided negotiation", "Step through actual proposals, replies and decisions.",
                        PAGES[6], "Replay a negotiation")
    st.caption(
        "SMEConnect AI is an offline teaching prototype with sequential in-memory agents. "
        "It does not execute real SME transactions or prove machine-learned adaptation."
    )
