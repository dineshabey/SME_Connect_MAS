from smeconnect.communication.message_bus import InMemoryMessageBus
from smeconnect.communication.message_schema import AgentMessage, Performative
from smeconnect.environment.marketplace import build_agents
from smeconnect.graphs.seller_graph import build_seller_graph

def run_one_offer():
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
