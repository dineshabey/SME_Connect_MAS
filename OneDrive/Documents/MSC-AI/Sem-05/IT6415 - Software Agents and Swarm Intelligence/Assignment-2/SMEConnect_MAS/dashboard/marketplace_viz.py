"""Streamlit public seller catalogue and marketplace-to-negotiation flow."""
import streamlit as st

from smeconnect.environment.catalogue import (
    SUPPORTED_PRODUCT, public_listings, discover_eligible_listings,
)
from smeconnect.simulation.supplier_selection import run_supplier_competition
from dashboard.negotiation_viz import neon_scene

def render_marketplace() -> None:
    st.subheader("🏬 Seller Marketplace & Product Catalogue")
    st.caption("Phase 03.1 · Synthetic public asking prices, not private seller reservation prices.")
    st.write("**Browse public listings → Choose sellers → Negotiate → Compare agreed offers.**")
    search = st.text_input("🔎 Search sellers or products", placeholder="S1, S2 or Peanuts", key="catalogue_search")
    items = public_listings(search=search)
    if not items:
        st.warning("No listings matched. Try 'Peanuts' or clear the search.")
    else:
        cols = st.columns(2)
        for index, item in enumerate(items):
            with cols[index % 2]:
                with st.container(border=True):
                    st.markdown(f"### 🏪 Seller {item.seller_id}")
                    st.caption(item.seller_strategy + " · Synthetic listing")
                    st.write("**📦 " + item.product_name + "**")
                    st.metric("Public asking price", f"Rs. {item.listed_price:,.2f} / packet")
                    st.write(f"**Advertised stock:** {item.advertised_stock:,} packets")
                    st.caption("Negotiated price can differ from the public price.")
    with st.expander("What information is public vs. private?"):
        st.write("**Public:** seller ID, product, asking price, advertised stock and broad strategy.")
        st.write("**Private:** seller minimum and target prices; never published to buyers.")

    st.markdown("### Start negotiation from Marketplace")
    st.caption("Currently supported: Roasted Peanuts 100g only. Other products require product-aware agent rules.")
    options = [item.seller_id for item in public_listings()]
    first, second = st.columns(2)
    retailer = first.selectbox("Retailer Agent", ["R1", "R2"], key="market_retailer")
    sellers = second.multiselect("Sellers", options, default=options, key="market_sellers")
    a, b, c = st.columns(3)
    quantity = a.number_input("Packets", min_value=1, max_value=300, value=200, step=10, key="market_qty")
    offered = b.slider("Initial offer (Rs.)", 100, 190, 150, 5, key="market_offer")
    target = c.slider("Retailer target (Rs.)", 100, 190, 150, 5, key="market_target")
    max_rounds = st.slider("Maximum rounds", 1, 10, 5, key="market_rounds")
    eligible = {
        listing.seller_id for listing in discover_eligible_listings(
            product_id=SUPPORTED_PRODUCT, quantity=int(quantity)
        )
    }
    unavailable = sorted(set(sellers) - eligible)
    if unavailable:
        st.warning("Insufficient advertised stock: " + ", ".join(unavailable))
    if st.button("🤖 Discover & negotiate with selected sellers",
                 type="primary", use_container_width=True, key="market_launch"):
        st.session_state.pop("market_result", None)
        if not sellers:
            st.error("Choose at least one seller.")
        elif unavailable:
            st.error("Reduce the quantity or remove sellers without sufficient stock.")
        else:
            try:
                result = run_supplier_competition(
                    retailer_id=retailer, seller_ids=list(sellers),
                    initial_price=float(offered), quantity=int(quantity),
                    retailer_target=float(target), max_rounds=max_rounds,
                )
                st.session_state["market_result"] = result
            except (ValueError, RuntimeError, PermissionError) as error:
                st.error(f"Negotiation could not start: {error}")
    result = st.session_state.get("market_result")
    if result:
        st.markdown("### Negotiated results")
        lookup = {item.seller_id: item for item in public_listings()}
        table = []
        for entry in result["selection"]["evaluations"]:
            table.append({
                "Seller": entry["seller_id"],
                "Public Price (Rs.)": lookup[entry["seller_id"]].listed_price,
                "Negotiation": entry["negotiation_status"],
                "Agreed Price (Rs.)": entry["price"],
                "Expected Gross Profit (Rs.)": entry["expected_gross_profit"],
                "Eligible": entry["eligible"],
            })
        st.dataframe(table, hide_index=True, use_container_width=True)
        selection = result["selection"]
        if selection["selected_seller_id"]:
            st.success(
                f"Retailer provisionally selected **{selection['selected_seller_id']}** "
                f"at **Rs. {selection['selected_price']:,.2f} / packet**."
            )
        else:
            st.warning("No feasible supplier was selected.")
        st.write("**Retailer decision:** " + selection["reasoning"])
        st.caption("Public asking prices and actual simulation agreements are distinct. No real orders or stock reservations.")
        with st.expander("🔍 Actual negotiation traces and Agent Thinking"):
            for seller_id, negotiation in result["negotiations"].items():
                st.markdown(f"#### Seller {seller_id} · {negotiation['status']}")
                st.markdown(
                    neon_scene(
                        negotiation["timeline"],
                        len(negotiation["timeline"]) - 1,
                        result["retailer"].agent_id, seller_id,
                    ),
                    unsafe_allow_html=True,
                )
                st.dataframe(negotiation["timeline"], hide_index=True, use_container_width=True)
