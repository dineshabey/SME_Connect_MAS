"""Phase 04: coordinate a provisional agreement with delivery, budget and stock.

All messages are Pydantic-validated and remain inside this synthetic simulation.
This module does NOT initiate real deliveries, charges or inventory changes.
"""
from uuid import uuid4
from smeconnect.communication.message_schema import AgentMessage, Performative
from smeconnect.communication.message_bus import InMemoryMessageBus
from smeconnect.environment.marketplace import build_agents
from smeconnect.graphs.delivery_graph import build_delivery_graph
from smeconnect.graphs.retailer_order_graph import build_retailer_order_graph
from smeconnect.simulation.reservation_ledger import ReservationLedger


def run_delivery_coordination(competition: dict, ledger: ReservationLedger, *,
                              quantity: int, delivery_id: str = "D1",
                              expected_retail_price: float = 200.0) -> dict:
    """One bounded attempt to reserve synthetic resources for selected agreement."""
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Quantity must be a positive integer.")
    agents = {agent.agent_id: agent for agent in build_agents()}
    coordinator_id = next(a.agent_id for a in agents.values() if a.role == "coordinator")
    retailer = competition["retailer"]
    selected = competition["selection"]
    seller_id = selected.get("selected_seller_id")
    price = selected.get("selected_price")
    events: list[dict] = []
    bus = InMemoryMessageBus(set(agents), max_messages=12)
    conversation_id = "FUL-" + uuid4().hex[:10].upper()
    order_id = "SIM-" + uuid4().hex[:10].upper()

    def record(actor, action, explanation):
        events.append({"step": len(events) + 1, "actor": actor,
                       "action": action, "explanation": explanation})

    def send(sender, receiver, action, product, amount, offered_price):
        msg = AgentMessage(
            sender=sender, receiver=receiver, performative=action,
            conversation_id=conversation_id, product=product,
            quantity=amount, unit_price=offered_price,
        )
        bus.send(msg, actor_id=sender)
        record(sender, action.value, f"{sender} → {receiver}: {product}, Rs.{offered_price:,.2f}")
        return msg

    def finish(status, reason, reservation=None, fee=None, margin=None):
        return {
            "status": status, "reason": reason, "reservation": reservation,
            "delivery_fee": fee, "expected_margin_after_delivery": margin,
            "events": events, "messages": bus.history,
            "conversation_id": conversation_id, "order_id": order_id,
            "selected_seller_id": seller_id, "retailer_id": retailer.agent_id,
            "delivery_id": delivery_id,
            "note": "All reservations are simulated, in-memory and session-scoped. "
                    "No physical shipment, payment or external inventory update.",
        }

    if seller_id is None or price is None:
        record(coordinator_id, "STOP", "No negotiated supplier was selected.")
        return finish("NO_AGREEMENT", "No feasible negotiated supplier agreement.")
    negotiation = competition.get("negotiations", {}).get(seller_id)
    if (negotiation is None or negotiation["status"] != "AGREED"
            or negotiation["agreed_price"] != price
            or not negotiation["messages"]
            or negotiation["messages"][0].quantity != quantity
            or negotiation["retailer"].agent_id != retailer.agent_id):
        raise ValueError("Selected offer must match an authentic negotiation in this simulation.")
    if seller_id not in agents or agents[seller_id].role != "seller":
        raise ValueError("Selected seller is not registered.")
    if delivery_id not in agents or agents[delivery_id].role != "delivery":
        raise ValueError("Delivery Agent is not registered.")
    delivery = agents[delivery_id]
    record(coordinator_id, "VERIFY", f"Selected {seller_id} at Rs.{price:,.2f} for {quantity} packets.")
    if ledger.seller_stock[seller_id] < quantity:
        record(coordinator_id, "STOP", "Seller's remaining stock is insufficient.")
        return finish("STOCK_UNAVAILABLE", "Not enough unreserved seller stock.")
    if ledger.retailer_demand[retailer.agent_id] < quantity:
        record(coordinator_id, "STOP", "Retailer has insufficient remaining demand.")
        return finish("DEMAND_EXHAUSTED", "Retailer demand is already allocated.")

    # The delivery agent receives a request and runs its own decision graph.
    send(coordinator_id, delivery_id, Performative.CFP, "delivery_trip", 1, 0.0)
    bus.receive(delivery_id)
    delivery_state = build_delivery_graph().invoke({
        "requested_quantity": quantity,
        "remaining_capacity": ledger.delivery_capacity[delivery_id],
        "cost_per_trip": delivery.cost_per_trip,
        "decision": "", "quoted_fee": None, "reason": "",
    })
    record(delivery_id, "THINK", delivery_state["reason"])
    if delivery_state["decision"] != "AVAILABLE":
        send(delivery_id, coordinator_id, Performative.REJECT, "delivery_trip", 1, 0.0)
        return finish("DELIVERY_UNAVAILABLE", delivery_state["reason"])
    fee = delivery_state["quoted_fee"]
    send(delivery_id, coordinator_id, Performative.PROPOSE, "delivery_trip", 1, fee)
    bus.receive(coordinator_id)

    # Retailer independently approves TOTAL cost rather than only unit price.
    send(coordinator_id, retailer.agent_id, Performative.INFORM, "delivery_trip", 1, fee)
    bus.receive(retailer.agent_id)
    approval = build_retailer_order_graph().invoke({
        "unit_price": price, "quantity": quantity, "delivery_fee": fee,
        "remaining_budget": ledger.retailer_budget[retailer.agent_id],
        "remaining_demand": ledger.retailer_demand[retailer.agent_id],
        "maximum_price": retailer.maximum_price,
        "expected_retail_price": expected_retail_price,
        "total_commitment": 0.0, "expected_net_margin": 0.0,
        "decision": "", "reason": "",
    })
    record(retailer.agent_id, "THINK", approval["reason"])
    if approval["decision"] != "ACCEPT":
        send(retailer.agent_id, coordinator_id, Performative.REJECT, "delivery_trip", 1, fee)
        return finish("RETAILER_DECLINED", approval["reason"], fee=fee,
                      margin=approval["expected_net_margin"])
    send(retailer.agent_id, coordinator_id, Performative.ACCEPT, "delivery_trip", 1, fee)
    bus.receive(coordinator_id)

    # A single all-or-nothing change to this in-memory, sequential simulation ledger.
    try:
        reservation = ledger.reserve(
            order_id=order_id, seller_id=seller_id,
            retailer_id=retailer.agent_id, delivery_id=delivery_id,
            quantity=quantity, unit_price=price, delivery_fee=fee,
        )
    except ValueError as error:
        record(coordinator_id, "STOP", str(error))
        return finish("RESERVATION_FAILED", str(error), fee=fee,
                      margin=approval["expected_net_margin"])
    record(coordinator_id, "RESERVED", "Stock, retailer budget, demand and delivery capacity reserved together.")
    send(coordinator_id, seller_id, Performative.INFORM, "roasted_peanuts_100g", quantity, price)
    send(coordinator_id, retailer.agent_id, Performative.INFORM, "roasted_peanuts_100g", quantity, price)
    return finish("RESERVED_SIMULATED", "Simulated resources reserved; no shipment or payment was executed.",
                  reservation=reservation, fee=fee,
                  margin=approval["expected_net_margin"])
