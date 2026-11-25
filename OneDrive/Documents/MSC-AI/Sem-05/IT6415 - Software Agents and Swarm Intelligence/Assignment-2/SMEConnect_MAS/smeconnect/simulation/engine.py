from smeconnect.communication.message_bus import InMemoryMessageBus
from smeconnect.communication.message_schema import AgentMessage, Performative
from smeconnect.environment.marketplace import build_agents
from smeconnect.graphs.seller_graph import build_seller_graph
from smeconnect.graphs.retailer_graph import build_retailer_graph


def run_one_offer():
    """Phase 01: a one-way proposal followed by a seller decision."""
    agents = build_agents()
    seller = agents[0]
    bus = InMemoryMessageBus()
    offer = AgentMessage(
        sender="R1", receiver=seller.agent_id, performative=Performative.PROPOSE,
        conversation_id="NEG-001", product="roasted_peanuts_100g",
        quantity=200, unit_price=160,
    )
    bus.send(offer)
    inbox = bus.receive(seller.agent_id)
    result = build_seller_graph().invoke({
        "minimum_price": seller.minimum_price,
        "target_price": seller.target_price,
        "stock": seller.available_stock,
        "offered_price": inbox[0].unit_price,
        "requested_quantity": inbox[0].quantity,
        "decision": "",
    })
    return {"agents": agents, "messages": bus.history, "decision": result["decision"]}


def run_retailer_offer(
    offered_price: float = 165.0,
    requested_quantity: int = 200,
    target_price: float = 150.0,
    expected_retail_price: float = 200.0,
    retailer_id: str = "R1",
):
    """Phase 02/Step 1: independent retailer evaluation, NOT yet a dialogue.

    The quoted offer is an external scenario input, not a message from the seller.
    """
    agents = build_agents()
    retailer = next(a for a in agents if a.agent_id == retailer_id and a.role == "retailer")
    state = {
        "budget": retailer.budget,
        "demand": retailer.demand,
        "maximum_price": retailer.maximum_price,
        "target_price": target_price,
        "expected_retail_price": expected_retail_price,
        "offered_price": offered_price,
        "requested_quantity": requested_quantity,
        "purchase_cost": 0.0,
        "expected_gross_profit": 0.0,
        "counter_price": None,
        "decision": "",
        "reason": "",
    }
    return {"retailer": retailer, "result": build_retailer_graph().invoke(state)}
