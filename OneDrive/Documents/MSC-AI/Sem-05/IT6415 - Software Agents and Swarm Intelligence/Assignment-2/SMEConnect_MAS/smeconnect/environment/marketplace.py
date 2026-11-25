from smeconnect.agents.seller_agent import SellerAgent
from smeconnect.agents.retailer_agent import RetailerAgent
from smeconnect.agents.delivery_agent import DeliveryAgent
from smeconnect.agents.market_agent import MarketAgent
from smeconnect.agents.coordinator_agent import CoordinatorAgent

def build_agents():
    """Seven synthetic instances; numbers are only simulation examples."""
    return [
        SellerAgent("S1", "seller", "Maximize margin", "firm", 150, 170, 500),
        SellerAgent("S2", "seller", "Maximize volume", "flexible", 140, 160, 300),
        RetailerAgent("R1", "retailer", "Reduce purchasing cost", "bargain", 165, 200, 35000),
        RetailerAgent("R2", "retailer", "Meet demand", "availability", 175, 150, 30000),
        DeliveryAgent("D1", "delivery", "Optimize trips", "combine", 400, 1000),
        MarketAgent("M1", "market", "Find opportunities", "monitor"),
        CoordinatorAgent("C1", "coordinator", "Route messages", "facilitate"),
    ]
