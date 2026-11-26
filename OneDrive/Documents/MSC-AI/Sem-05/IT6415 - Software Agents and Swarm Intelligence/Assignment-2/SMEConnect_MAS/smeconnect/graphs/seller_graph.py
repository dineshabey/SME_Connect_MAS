"""Seller decision graph: firm margin and volume-oriented bulk strategies."""
from langgraph.graph import END, START, StateGraph
from .state import SellerGraphState


def evaluate_offer(state: SellerGraphState) -> dict:
    quantity = state["requested_quantity"]
    price = state["offered_price"]
    minimum = state["minimum_price"]
    if quantity <= 0 or quantity > state["stock"] or price < minimum:
        return {"decision": "REJECT", "counter_price": None,
                "reason": "Quantity unavailable or price below seller minimum."}
    # A volume-oriented seller accepts sufficiently large orders at a lower
    # threshold. This is the SELLER'S own policy, never a coordinator override.
    if (state.get("strategy") == "flexible" and quantity >= 100
            and price >= minimum + 10):
        return {"decision": "ACCEPT", "counter_price": None,
                "reason": "Volume seller accepts this bulk offer under its own pricing rule."}
    if price >= state["target_price"]:
        return {"decision": "ACCEPT", "counter_price": None,
                "reason": "Offer meets seller target price and stock constraints."}
    next_price = round(min(state["target_price"], price + 5.0), 2)
    return {"decision": "COUNTER_OFFER", "counter_price": next_price,
            "reason": "Offer is feasible; seller requests a higher price."}


def build_seller_graph():
    builder = StateGraph(SellerGraphState)
    builder.add_node("evaluate_offer", evaluate_offer)
    builder.add_edge(START, "evaluate_offer")
    builder.add_edge("evaluate_offer", END)
    return builder.compile()
