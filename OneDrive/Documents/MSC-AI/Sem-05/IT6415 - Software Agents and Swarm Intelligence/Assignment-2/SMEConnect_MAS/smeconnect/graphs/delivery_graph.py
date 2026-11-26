"""Delivery Agent LangGraph for capacity and fee quotation."""
from typing import TypedDict
from langgraph.graph import START, END, StateGraph

class DeliveryState(TypedDict):
    requested_quantity: int
    remaining_capacity: int
    cost_per_trip: float
    decision: str
    quoted_fee: float | None
    reason: str

def validate_delivery(state: DeliveryState) -> dict:
    if state["requested_quantity"] <= 0:
        return {"decision": "REJECT", "quoted_fee": None, "reason": "Quantity must be positive."}
    if state["remaining_capacity"] < state["requested_quantity"]:
        return {"decision": "REJECT", "quoted_fee": None,
                "reason": "Delivery capacity is insufficient for this order."}
    if state["cost_per_trip"] < 0:
        return {"decision": "REJECT", "quoted_fee": None, "reason": "Invalid delivery fee."}
    return {"decision": "AVAILABLE", "quoted_fee": round(state["cost_per_trip"], 2),
            "reason": "Delivery agent has capacity and quotes one simulated trip."}

def build_delivery_graph():
    graph = StateGraph(DeliveryState)
    graph.add_node("evaluate_capacity_and_fee", validate_delivery)
    graph.add_edge(START, "evaluate_capacity_and_fee")
    graph.add_edge("evaluate_capacity_and_fee", END)
    return graph.compile()
