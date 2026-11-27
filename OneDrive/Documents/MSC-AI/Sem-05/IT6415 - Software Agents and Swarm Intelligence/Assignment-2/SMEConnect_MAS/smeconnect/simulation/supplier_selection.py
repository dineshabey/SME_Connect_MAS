"""Phase 03: discover, negotiate separately, then let RETAILER select supplier.

No physical stock/budget reservations or real payments are made.
"""
from smeconnect.environment.marketplace import build_agents
from smeconnect.environment.market_state import MarketSnapshot
from smeconnect.graphs.supplier_selection_graph import build_supplier_selection_graph
from smeconnect.simulation.negotiation import run_negotiation


def run_supplier_competition(
    *, retailer_id: str = "R1", seller_ids: list[str] | None = None,
    initial_price: float = 150.0, quantity: int = 200,
    retailer_target: float = 150.0, expected_retail_price: float = 200.0,
    max_rounds: int = 5, market_state: MarketSnapshot | None = None
) -> dict:
    agents = build_agents(market_state)
    coordinator = next(a for a in agents if a.role == "coordinator")
    available = coordinator.discover_sellers(agents)
    if seller_ids is None:
        candidates = available
    else:
        if len(seller_ids) != len(set(seller_ids)):
            raise ValueError("Duplicate seller IDs are not allowed.")
        if not seller_ids or any(s not in available for s in seller_ids):
            raise ValueError("All selected sellers must be discovered and registered.")
        candidates = sorted(seller_ids)
    retailer = next((a for a in agents if a.agent_id == retailer_id and a.role == "retailer"), None)
    if retailer is None:
        raise ValueError("Unknown retailer.")
    if quantity <= 0 or quantity > retailer.demand:
        raise ValueError("Requested quantity must be positive and within retailer demand.")
    # Every candidate gets its own seller/retailer LangGraph invocation and conversation.
    runs = {}
    for sid in candidates:
        runs[sid] = run_negotiation(
            seller_id=sid, retailer_id=retailer_id,
            initial_price=initial_price, quantity=quantity,
            retailer_target=retailer_target,
            expected_retail_price=expected_retail_price,
            max_rounds=max_rounds, market_state=market_state,
        )
    offers = [
        {"seller_id": sid, "status": run["status"],
         "agreed_price": run["agreed_price"], "rounds": run["rounds"]}
        for sid, run in runs.items()
    ]
    choice = build_supplier_selection_graph().invoke({
        "offers": offers, "requested_quantity": quantity,
        "budget": retailer.budget, "maximum_price": retailer.maximum_price,
        "expected_retail_price": expected_retail_price,
        "selected_seller_id": None, "selected_price": None,
        "expected_gross_profit": 0.0, "reasoning": "", "evaluations": [],
    })
    return {
        "retailer": retailer, "discovered_seller_ids": available,
        "evaluated_seller_ids": candidates, "negotiations": runs,
        "selection": choice, "offers": offers,
        "note": "Competitive negotiations and supplier choice are provisional. "
                "No inventory or budget is reserved; no delivery or payment is performed.",
    }
