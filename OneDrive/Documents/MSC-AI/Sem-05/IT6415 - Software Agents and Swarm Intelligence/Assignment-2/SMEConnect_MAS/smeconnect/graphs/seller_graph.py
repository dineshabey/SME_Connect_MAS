from langgraph.graph import END, START, StateGraph
from .state import SellerGraphState

def evaluate_offer(state: SellerGraphState) -> dict:
    quantity = state["requested_quantity"]
    price = state["offered_price"]
    if quantity <= 0 or quantity > state["stock"] or price < state["minimum_price"]:
        return {"decision": "REJECT"}
    if price >= state["target_price"]:
        return {"decision": "ACCEPT"}
    return {"decision": "COUNTER_OFFER"}

def build_seller_graph():
    builder = StateGraph(SellerGraphState)
    builder.add_node("evaluate_offer", evaluate_offer)
    builder.add_edge(START, "evaluate_offer")
    builder.add_edge("evaluate_offer", END)
    return builder.compile()
