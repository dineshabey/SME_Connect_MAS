"""Retailer's independent supplier-choice graph.

Only PUBLIC negotiation outcomes enter this graph. It cannot see sellers'
minimum prices or target prices.
"""
from typing import TypedDict
from langgraph.graph import START, END, StateGraph


class SupplierSelectionState(TypedDict):
    offers: list[dict]
    requested_quantity: int
    budget: float
    maximum_price: float
    expected_retail_price: float
    selected_seller_id: str | None
    selected_price: float | None
    expected_gross_profit: float
    reasoning: str
    evaluations: list[dict]


def evaluate_suppliers(state: SupplierSelectionState) -> dict:
    evaluations = []
    quantity = state["requested_quantity"]
    for offer in state["offers"]:
        seller_id = offer["seller_id"]
        price = offer["agreed_price"]
        accepted = offer["status"] == "AGREED" and price is not None
        cost = round(price * quantity, 2) if accepted else None
        gross_profit = round(
            (state["expected_retail_price"] - price) * quantity, 2
        ) if accepted else None
        eligible = bool(
            accepted and quantity > 0
            and price <= state["maximum_price"]
            and cost <= state["budget"]
            and gross_profit > 0
        )
        evaluations.append({
            "seller_id": seller_id,
            "negotiation_status": offer["status"],
            "price": price,
            "purchase_cost": cost,
            "expected_gross_profit": gross_profit,
            "rounds": offer["rounds"],
            "eligible": eligible,
            "explanation": (
                "Negotiated price satisfies retailer constraints."
                if eligible else "No viable agreement for retailer."
            ),
        })
    return {"evaluations": evaluations}


def select_best_supplier(state: SupplierSelectionState) -> dict:
    valid = [offer for offer in state["evaluations"] if offer["eligible"]]
    if not valid:
        return {
            "selected_seller_id": None,
            "selected_price": None,
            "expected_gross_profit": 0.0,
            "reasoning": "No seller has a profitable, affordable negotiated agreement.",
        }
    # Highest retailer gross profit; fewer negotiation rounds; stable ID tie-break.
    choice = sorted(valid, key=lambda x: (
        -x["expected_gross_profit"], x["rounds"], x["seller_id"]
    ))[0]
    return {
        "selected_seller_id": choice["seller_id"],
        "selected_price": choice["price"],
        "expected_gross_profit": choice["expected_gross_profit"],
        "reasoning": (
            f"Retailer selected {choice['seller_id']} based on highest expected "
            f"gross profit (Rs. {choice['expected_gross_profit']:,.2f}) among "
            "feasible negotiated agreements; ties use fewer rounds and seller ID."
        ),
    }


def build_supplier_selection_graph():
    graph = StateGraph(SupplierSelectionState)
    graph.add_node("evaluate_suppliers", evaluate_suppliers)
    graph.add_node("select_best_supplier", select_best_supplier)
    graph.add_edge(START, "evaluate_suppliers")
    graph.add_edge("evaluate_suppliers", "select_best_supplier")
    graph.add_edge("select_best_supplier", END)
    return graph.compile()
