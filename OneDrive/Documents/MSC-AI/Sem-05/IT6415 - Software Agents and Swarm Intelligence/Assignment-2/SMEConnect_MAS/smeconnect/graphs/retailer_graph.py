"""Retailer decision graph with bounded, explainable price concessions."""
from langgraph.graph import END, START, StateGraph
from .state import RetailerGraphState

def validate_offer(state: RetailerGraphState) -> dict:
    quantity, price = state["requested_quantity"], state["offered_price"]
    if quantity <= 0:
        return {"decision": "REJECT", "reason": "Requested quantity must be positive."}
    if quantity > state["demand"]:
        return {"decision": "REJECT", "reason": "Offer exceeds remaining retailer demand."}
    if price < 0:
        return {"decision": "REJECT", "reason": "Offered price cannot be negative."}
    if state["budget"] < 0 or state["maximum_price"] < 0 or state["target_price"] < 0:
        return {"decision": "REJECT", "reason": "Retailer financial constraints are invalid."}
    if state["expected_retail_price"] <= 0:
        return {"decision": "REJECT", "reason": "Expected retail price must be positive."}
    return {"decision": "", "reason": ""}

def evaluate_finances(state: RetailerGraphState) -> dict:
    quantity, price = state["requested_quantity"], state["offered_price"]
    return {"purchase_cost": round(price * quantity, 2),
            "expected_gross_profit": round((state["expected_retail_price"] - price) * quantity, 2)}

def decide_offer(state: RetailerGraphState) -> dict:
    if state["decision"] == "REJECT":
        return {"counter_price": None}
    if state["purchase_cost"] > state["budget"]:
        return {"decision": "REJECT", "counter_price": None, "reason": "Purchase exceeds available budget."}
    if state["offered_price"] > state["maximum_price"]:
        return {"decision": "REJECT", "counter_price": None, "reason": "Offer exceeds maximum buying price."}
    if state["expected_gross_profit"] <= 0:
        return {"decision": "REJECT", "counter_price": None, "reason": "Expected gross profit is not positive."}
    round_number = max(0, min(int(state.get("negotiation_round", 0)), 20))
    target = min(state["target_price"] + 5.0 * round_number,
                 state["maximum_price"], state["budget"] / state["requested_quantity"])
    if state["offered_price"] <= target:
        return {"decision": "ACCEPT", "counter_price": None,
                "reason": "Offer meets this round's acceptable target and hard constraints."}
    return {"decision": "COUNTER_OFFER", "counter_price": round(target, 2),
            "reason": "Offer is feasible but above preferred price; retailer counter-proposes."}

def build_retailer_graph():
    builder = StateGraph(RetailerGraphState)
    builder.add_node("validate_offer", validate_offer)
    builder.add_node("evaluate_finances", evaluate_finances)
    builder.add_node("decide_offer", decide_offer)
    builder.add_edge(START, "validate_offer")
    builder.add_edge("validate_offer", "evaluate_finances")
    builder.add_edge("evaluate_finances", "decide_offer")
    builder.add_edge("decide_offer", END)
    return builder.compile()
