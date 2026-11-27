"""Phase 06: a readable academic landing dashboard backed by genuine agent state.

The overview is a navigation and teaching aid; no business decisions happen here.
"""
import streamlit as st

from smeconnect.environment.marketplace import build_agents
from smeconnect.simulation.market_experiment import run_market_experiment

AGENT_DESCRIPTIONS = [
    ("S1", "🏪", "Margin-focused seller", "Protects its target price and available stock"),
    ("S2", "📦", "Volume-focused seller", "Can accept eligible bulk negotiations"),
    ("R1", "🛒", "Cost-focused retailer", "Negotiates and chooses financially feasible offers"),
    ("R2", "🛍️", "Availability-focused retailer", "Has independent budget and demand constraints"),
    ("D1", "🚚", "Delivery agent", "Checks trip capacity and quotes a simulated fee"),
    ("M1", "📈", "Market observer", "Reports controlled market changes via typed messages"),
    ("C1", "🧭", "Coordinator", "Discovers sellers and facilitates resource reservations"),
]


def _agent_network():
    """Explanatory topology, not a live packet trace."""
    st.markdown(
        """
        <style>
        .mas-network{
            border-radius:20px;background:linear-gradient(125deg,#11243d,#12384a);
            padding:36px clamp(20px,4vw,72px);color:#e8f3ff;
            border:1px solid #3b7188;margin:12px 0 28px;
        }
        .mas-network .net-row{
            display:flex;gap:clamp(18px,3vw,52px);align-items:stretch;
            justify-content:space-evenly;flex-wrap:wrap;margin:18px 0;
            width:100%;
        }
        .mas-network .net-node{
            flex:1 1 240px;max-width:390px;min-width:210px;
            border:2px solid #518da8;background:#1c4561;border-radius:16px;
            padding:27px 24px;text-align:center;color:#f5fafc;
            font-size:25px !important;line-height:1.35;font-weight:750;
        }
        .mas-network .net-node small{
            display:block;font-weight:450;font-size:19px !important;
            line-height:1.5;color:#c9e1ec;margin-top:7px;
        }
        .mas-network .net-line{
            font-size:22px !important;font-weight:650;color:#71d5e5;
            text-align:center;margin:15px auto;
        }
        .mas-network .net-note{
            text-align:center;color:#c3dbe6;font-size:18px !important;
            line-height:1.5;margin-top:22px;
        }
        @media(max-width:750px){
          .mas-network{padding:22px 12px}
          .mas-network .net-node{min-width:145px;font-size:19px !important;padding:16px 10px}
          .mas-network .net-node small{font-size:15px !important}
          .mas-network .net-line{font-size:16px !important}
        }
        </style>
        <div class="mas-network">
          <div class="net-row">
            <div class="net-node">🏪 Seller S1<small>Margin strategy</small></div>
            <div class="net-node">📦 Seller S2<small>Volume strategy</small></div>
          </div>
          <div class="net-line">↕ proposals · accept · reject ↕</div>
          <div class="net-row">
            <div class="net-node">🛒 Retailer R1<small>Cost strategy</small></div>
            <div class="net-node">🛍️ Retailer R2<small>Demand strategy</small></div>
          </div>
          <div class="net-line">↕ coordination and public signals ↕</div>
          <div class="net-row">
            <div class="net-node">🚚 Delivery D1<small>Capacity / trip fee</small></div>
            <div class="net-node">📈 Market M1<small>Scenario signals</small></div>
            <div class="net-node">🧭 Coordinator C1<small>Discovery / reservation</small></div>
          </div>
          <div class="net-note">Conceptual roles and message paths · communication traces appear inside each lab</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview() -> None:
    st.subheader("🎓 Professor Demo · Multi-Agent Control Center")
    st.caption("A guided overview of the real simulation. All businesses, quantities and prices are synthetic.")

    agents = build_agents()
    sellers = sum(a.role == "seller" for a in agents)
    retailers = sum(a.role == "retailer" for a in agents)
    top = st.columns(4)
    top[0].metric("Registered agents", len(agents))
    top[1].metric("Competing sellers", sellers)
    top[2].metric("Independent retailers", retailers)
    top[3].metric("Market scenarios", 3)
    st.info(
        "**සිංහලෙන්:** එකම system එකේ වෙන වෙනම goals තියෙන agents 7ක් ක්‍රියාකරනවා. "
        "Seller සහ Retailer මිල ගැන සාකච්ඡා කරලා, Delivery සහ Coordinator "
        "resources සකස් කරනවා; Market Agent වෙනස්කම් report කරනවා."
    )

    st.markdown("### Understand the agent network")
    _agent_network()

    st.markdown("### Meet the seven agents")
    for i in range(0, len(AGENT_DESCRIPTIONS), 3):
        cols = st.columns(3)
        for col, (agent_id, emoji, title, description) in zip(
            cols, AGENT_DESCRIPTIONS[i:i + 3]
        ):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{emoji} {agent_id} · {title}**")
                    st.caption(description)

    st.markdown("### Guided demonstration path")
    steps = [
        ("01", "🏬 Marketplace", "Inspect synthetic public seller listings."),
        ("02", "🏆 Supplier competition", "See independent S1/S2 negotiations and R1 choice."),
        ("03", "🚚 Delivery coordination", "Observe simulated resource checks and reservation."),
        ("04", "📈 Market adaptation", "Change stock or pricing and see agents re-evaluate."),
        ("05", "🧪 Experiments", "Measure selection rates, prices and communication volume."),
    ]
    for number, title, description in steps:
        st.markdown(f"**{number} · {title}** — {description}")
    st.caption("Select the named tab above to run each step. This overview never fabricates a transaction.")

    st.markdown("### One-click live market demonstration")
    st.write(
        "Compare a normal market to an S2 stock shortage using **the actual existing "
        "LangGraph seller and retailer decisions**. Both trials use R1, 200 packets, "
        "Rs.150 initial offer and five negotiation rounds."
    )
    run = st.button(
        "▶ Demonstrate how a stock shortage changes the supplier",
        type="primary", use_container_width=True, key="professor_demo_run",
    )
    if run:
        try:
            st.session_state["professor_demo_outcome"] = run_market_experiment(
                scenario="s2_shortage", retailer_id="R1",
                quantity=200, initial_price=150.0,
                retailer_target=150.0, max_rounds=5,
            )
        except (RuntimeError, ValueError, PermissionError) as error:
            st.session_state.pop("professor_demo_outcome", None)
            st.error(f"Demonstration stopped: {error}")
    outcome = st.session_state.get("professor_demo_outcome")
    if outcome:
        cols = st.columns(2)
        for col, title, key in (
            (cols[0], "Normal marketplace", "before"),
            (cols[1], "After S2 stock shortage", "after"),
        ):
            data = outcome[key]
            with col:
                with st.container(border=True):
                    st.markdown(f"**{title}**")
                    st.metric("Selected supplier", data["selected_seller"] or "None")
                    if data["agreed_price"] is not None:
                        st.metric("Negotiated packet price", f"Rs. {data['agreed_price']:,.2f}")
                    else:
                        st.metric("Negotiated packet price", "No agreement")
                    st.metric(
                        "Expected gross profit",
                        f"Rs. {data['expected_gross_profit']:,.2f}",
                    )
        if outcome["before"]["selected_seller"] != outcome["after"]["selected_seller"]:
            st.success("Actual simulation result: the selected supplier changed.")
        else:
            st.info("Actual simulation result: supplier selection did not change.")
        with st.expander("🔍 Why did agents make these decisions?"):
            st.write(outcome["market_signal"]["summary"])
            for label, key in (("Normal market", "baseline"), ("Changed market", "changed")):
                st.markdown(f"**{label}**")
                for seller_id, negotiation in outcome[key]["negotiations"].items():
                    st.write(
                        f"{seller_id}: {negotiation['status']}; "
                        f"{len(negotiation['messages'])} recorded messages."
                    )
                    st.dataframe(negotiation["timeline"], hide_index=True,
                                 use_container_width=True)
        st.caption(
            "The supplier change (if any) is a rule-based response to different stock inputs, "
            "not proof of online learning. No inventory is reserved by this experiment."
        )

    st.markdown("### Academic evidence and scope")
    st.caption(
        "Implemented: independent decisions, typed messages, competition, negotiation, "
        "session-scoped coordination and reproducible market evaluations. "
        "Not implemented: real commerce, payments, distributed deployment or autonomous learning."
    )
