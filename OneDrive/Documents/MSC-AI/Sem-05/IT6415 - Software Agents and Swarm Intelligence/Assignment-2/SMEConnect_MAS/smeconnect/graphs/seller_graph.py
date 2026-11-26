"""Seller decision graph; uses seller's private goals only."""
from langgraph.graph import END, START, StateGraph
from .state import SellerGraphState

def evaluate_offer(state: SellerGraphState) -> dict:
    quantity = state["requested_quantity"]
    price = state["offered_price"]
    if quantity <= 0 or quantity > state["stock"] or price < state["minimum_price"]:
        return {"decision": "REJECT", "counter_price": None,
                "reason": "Quantity unavailable or price below private minimum."}
    if price >= state["target_price"]:
        return {"decision": "ACCEPT", "counter_price": None,
                "reason": "Offer meets seller target price and stock constraints."}
    next_price = round(min(state["target_price"], price + 5.0), 2)
    return {"decision": "COUNTER_OFFER", "counter_price": next_price,
            "reason": "Price is a viable starting point; seller requests a higher price."}

def build_seller_graph():
    builder = StateGraph(SellerGraphState)
    builder.add_node("evaluate_offer", evaluate_offer)
    builder.add_edge(START, "evaluate_offer")
    builder.add_edge("evaluate_offer", END)
    return builder.compile()
