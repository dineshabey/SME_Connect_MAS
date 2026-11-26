"""Retailer financial approval for provisional order including delivery."""
from typing import TypedDict
from langgraph.graph import START, END, StateGraph

class RetailerOrderState(TypedDict):
    unit_price: float
    quantity: int
    delivery_fee: float
    remaining_budget: float
    remaining_demand: int
    maximum_price: float
    expected_retail_price: float
    total_commitment: float
    expected_net_margin: float
    decision: str
    reason: str

def assess_order(state: RetailerOrderState) -> dict:
    quantity, price, fee = state["quantity"], state["unit_price"], state["delivery_fee"]
    if quantity <= 0 or price < 0 or fee < 0:
        return {"decision": "REJECT", "reason": "Invalid order inputs.",
                "total_commitment": 0.0, "expected_net_margin": 0.0}
    total = round(price * quantity + fee, 2)
    margin = round((state["expected_retail_price"] - price) * quantity - fee, 2)
    if quantity > state["remaining_demand"]:
        decision, reason = "REJECT", "Quantity exceeds remaining retailer demand."
    elif price > state["maximum_price"]:
        decision, reason = "REJECT", "Agreed price exceeds retailer maximum."
    elif total > state["remaining_budget"]:
        decision, reason = "REJECT", "Purchase plus delivery exceeds remaining retailer budget."
    elif margin <= 0:
        decision, reason = "REJECT", "Expected margin after delivery fee is not positive."
    else:
        decision, reason = "ACCEPT", "Retailer approves total cost including delivery."
    return {"decision": decision, "reason": reason,
            "total_commitment": total, "expected_net_margin": margin}

def build_retailer_order_graph():
    graph = StateGraph(RetailerOrderState)
    graph.add_node("assess_total_cost", assess_order)
    graph.add_edge(START, "assess_total_cost")
    graph.add_edge("assess_total_cost", END)
    return graph.compile()
