"""Bounded, real message exchange between independent LangGraph seller and retailer."""
from uuid import uuid4
from smeconnect.communication.message_bus import InMemoryMessageBus
from smeconnect.communication.message_schema import AgentMessage, Performative
from smeconnect.environment.marketplace import build_agents
from smeconnect.graphs.seller_graph import build_seller_graph
from smeconnect.graphs.retailer_graph import build_retailer_graph

PRODUCT = "roasted_peanuts_100g"

def run_negotiation(*, seller_id: str = "S1", retailer_id: str = "R1",
                    initial_price: float = 150.0, quantity: int = 200,
                    retailer_target: float = 150.0, expected_retail_price: float = 200.0,
                    max_rounds: int = 5) -> dict:
    """A round contains one seller graph invocation and at most one retailer response.

    An AGREED price is provisional: there is NO inventory, payment or delivery commit.
    """
    if not 1 <= max_rounds <= 10:
        raise ValueError("max_rounds must be between 1 and 10")
    agents = build_agents()
    seller = next(a for a in agents if a.agent_id == seller_id and a.role == "seller")
    retailer = next(a for a in agents if a.agent_id == retailer_id and a.role == "retailer")
    bus = InMemoryMessageBus({a.agent_id for a in agents}, max_messages=4 * max_rounds + 3)
    seller_graph = build_seller_graph()
    retailer_graph = build_retailer_graph()
    conversation_id = "NEG-" + uuid4().hex[:10].upper()
    events = []
    status, agreed_price = "MAX_ROUNDS", None

    def emit(sender, receiver, performative, price, round_number, reason):
        message = AgentMessage(sender=sender, receiver=receiver, performative=performative,
            conversation_id=conversation_id, product=PRODUCT, quantity=quantity, unit_price=price)
        bus.send(message, actor_id=sender)
        events.append({"round": round_number, "sender": sender, "receiver": receiver,
                       "performative": performative.value, "price": price, "reason": reason})

    emit(retailer_id, seller_id, Performative.PROPOSE, initial_price, 1,
         "Retailer initiates negotiation with an autonomous offer.")

    for round_number in range(1, max_rounds + 1):
        inbox = bus.receive(seller_id)
        if len(inbox) != 1 or inbox[0].performative != Performative.PROPOSE:
            raise RuntimeError("Unexpected seller inbox / invalid transition.")
        offer = inbox[0]
        s = seller_graph.invoke({"minimum_price": seller.minimum_price,
            "target_price": seller.target_price, "stock": seller.available_stock,
            "offered_price": offer.unit_price, "requested_quantity": offer.quantity,
            "decision": ""})
        if s["decision"] == "REJECT":
            emit(seller_id, retailer_id, Performative.REJECT, offer.unit_price,
                 round_number, s.get("reason", "Seller rejected proposal."))
            status = "REJECTED"
            break
        if s["decision"] == "ACCEPT":
            emit(seller_id, retailer_id, Performative.ACCEPT, offer.unit_price,
                 round_number, s.get("reason", "Seller accepted proposal."))
            status, agreed_price = "AGREED", offer.unit_price
            break
        counter = s["counter_price"]
        emit(seller_id, retailer_id, Performative.PROPOSE, counter,
             round_number, s.get("reason", "Seller counter-offer."))
        inbox = bus.receive(retailer_id)
        if len(inbox) != 1 or inbox[0].performative != Performative.PROPOSE:
            raise RuntimeError("Unexpected retailer inbox / invalid transition.")
        r = retailer_graph.invoke({
            "budget": retailer.budget, "demand": retailer.demand,
            "maximum_price": retailer.maximum_price, "target_price": retailer_target,
            "expected_retail_price": expected_retail_price,
            "offered_price": inbox[0].unit_price,
            "requested_quantity": quantity, "purchase_cost": 0.0,
            "expected_gross_profit": 0.0, "counter_price": None,
            "decision": "", "reason": "", "negotiation_round": round_number,
        })
        if r["decision"] == "REJECT":
            emit(retailer_id, seller_id, Performative.REJECT, counter,
                 round_number, r["reason"])
            status = "REJECTED"
            break
        if r["decision"] == "ACCEPT":
            emit(retailer_id, seller_id, Performative.ACCEPT, counter,
                 round_number, r["reason"])
            status, agreed_price = "AGREED", counter
            break
        if round_number == max_rounds:
            break
        emit(retailer_id, seller_id, Performative.PROPOSE, r["counter_price"],
             round_number + 1, r["reason"])
    return {"status": status, "agreed_price": agreed_price, "rounds": round_number,
            "messages": bus.history, "timeline": events, "seller": seller,
            "retailer": retailer, "conversation_id": conversation_id,
            "note": "Provisional negotiation only; no inventory, payment, or delivery reservation."}
