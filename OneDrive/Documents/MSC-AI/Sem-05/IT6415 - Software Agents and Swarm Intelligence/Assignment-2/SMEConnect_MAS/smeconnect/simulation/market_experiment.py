"""Compare two real bounded MAS negotiations under synthetic market snapshots.

Market signals are FIPA-inspired, public and validated. They are observations;
each negotiation uses independently constructed agents from the given snapshot.
"""
from smeconnect.communication.message_bus import InMemoryMessageBus
from smeconnect.communication.message_schema import AgentMessage, Performative
from smeconnect.environment.market_state import market_snapshot, SCENARIO_NAMES
from smeconnect.environment.marketplace import build_agents
from smeconnect.simulation.supplier_selection import run_supplier_competition


def run_market_experiment(*, scenario: str = "s2_shortage",
                          retailer_id: str = "R1", quantity: int = 200,
                          initial_price: float = 150.0,
                          retailer_target: float = 150.0,
                          max_rounds: int = 5) -> dict:
    """Returns actual before/after outcomes, without inventory reservation."""
    if scenario not in SCENARIO_NAMES or scenario == "normal":
        raise ValueError("Choose a supported changed-market scenario.")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Quantity must be a positive integer.")
    normal = market_snapshot("normal")
    changed = market_snapshot(scenario)
    before_agents = {a.agent_id: a for a in build_agents(normal)}
    after_agents = {a.agent_id: a for a in build_agents(changed)}
    if retailer_id not in before_agents or before_agents[retailer_id].role != "retailer":
        raise ValueError("Unknown retailer.")
    if quantity > before_agents[retailer_id].demand or quantity > after_agents[retailer_id].demand:
        raise ValueError("Requested quantity must fit retailer demand in both snapshots.")

    marker = after_agents["M1"]
    signal = marker.observe_public_change(
        scenario=scenario,
        seller_stock={key: value.available_stock for key, value in after_agents.items()
                      if value.role == "seller"},
        retailer_demand={key: value.demand for key, value in after_agents.items()
                         if value.role == "retailer"},
    )
    bus = InMemoryMessageBus(set(after_agents), max_messages=4)
    message = AgentMessage(
        sender=marker.agent_id, receiver=retailer_id, performative=Performative.INFORM,
        conversation_id="MARKET-" + scenario.upper(),
        product=signal["product"], quantity=signal["quantity"], unit_price=0.0,
    )
    bus.send(message, actor_id=marker.agent_id)
    received = bus.receive(retailer_id)
    if len(received) != 1 or received[0] != message:
        raise RuntimeError("Market signal was not delivered to the retailer.")

    params = dict(retailer_id=retailer_id, quantity=quantity,
                  initial_price=initial_price, retailer_target=retailer_target,
                  max_rounds=max_rounds)
    baseline = run_supplier_competition(**params, market_state=normal)
    modified = run_supplier_competition(**params, market_state=changed)

    def summarize(comp):
        return {
            "selected_seller": comp["selection"]["selected_seller_id"],
            "agreed_price": comp["selection"]["selected_price"],
            "expected_gross_profit": comp["selection"]["expected_gross_profit"],
            "offers": [
                {"seller_id": item["seller_id"], "status": item["status"],
                 "price": item["agreed_price"], "rounds": item["rounds"]}
                for item in comp["offers"]
            ],
        }

    return {
        "scenario": scenario,
        "scenario_name": SCENARIO_NAMES[scenario],
        "market_signal": signal,
        "signal_messages": bus.history,
        "before": summarize(baseline),
        "after": summarize(modified),
        "baseline": baseline,
        "changed": modified,
        "observable_state": {
            "before": {
                "stock_S1": before_agents["S1"].available_stock,
                "stock_S2": before_agents["S2"].available_stock,
                "demand_R1": before_agents["R1"].demand,
            },
            "after": {
                "stock_S1": after_agents["S1"].available_stock,
                "stock_S2": after_agents["S2"].available_stock,
                "demand_R1": after_agents["R1"].demand,
            },
        },
        "note": "Controlled synthetic snapshots; no real-time sensing or learned adaptation. "
                "Agent decisions follow existing LangGraph rules with changed inputs. "
                "No payments, deliveries, stock reservations or external writes.",
    }
