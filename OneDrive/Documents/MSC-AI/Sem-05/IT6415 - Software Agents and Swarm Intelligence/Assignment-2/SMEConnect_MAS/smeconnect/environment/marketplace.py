from smeconnect.agents.seller_agent import SellerAgent
from smeconnect.agents.retailer_agent import RetailerAgent
from smeconnect.agents.delivery_agent import DeliveryAgent
from smeconnect.agents.market_agent import MarketAgent
from smeconnect.agents.coordinator_agent import CoordinatorAgent
from dataclasses import replace
from smeconnect.environment.market_state import MarketSnapshot

def build_agents(market_state: MarketSnapshot | None = None):
    """Seven synthetic instances; numbers are only simulation examples."""
    agents = [
        SellerAgent("S1", "seller", "Maximize margin", "firm", 150, 170, 500),
        SellerAgent("S2", "seller", "Maximize volume", "flexible", 140, 160, 300),
        RetailerAgent("R1", "retailer", "Reduce purchasing cost", "bargain", 165, 200, 35000),
        RetailerAgent("R2", "retailer", "Meet demand", "availability", 175, 150, 30000),
        DeliveryAgent("D1", "delivery", "Optimize trips", "combine", 400, 1000),
        MarketAgent("M1", "market", "Find opportunities", "monitor"),
        CoordinatorAgent("C1", "coordinator", "Route messages", "facilitate"),
    ]
    if market_state is None:
        return agents
    adjusted = []
    for agent in agents:
        if agent.role == "seller":
            new_stock = market_state.seller_stock.get(agent.agent_id, agent.available_stock)
            minimum = agent.minimum_price + market_state.seller_minimum_adjustment.get(agent.agent_id, 0.0)
            target = agent.target_price + market_state.seller_target_adjustment.get(agent.agent_id, 0.0)
            if minimum < 0 or target < minimum:
                raise ValueError("Market scenario violates seller pricing constraints.")
            agent = replace(agent, available_stock=new_stock, minimum_price=minimum, target_price=target)
        elif agent.role == "retailer":
            agent = replace(agent, demand=market_state.retailer_demand.get(agent.agent_id, agent.demand))
        adjusted.append(agent)
    return adjusted
