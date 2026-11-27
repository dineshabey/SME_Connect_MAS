"""Market Agent M1 monitors public scenario changes and reports a bounded signal."""
from dataclasses import dataclass
from .base_agent import BaseAgent


@dataclass(frozen=True)
class MarketAgent(BaseAgent):
    demand_multiplier: float = 1.0

    def observe_public_change(self, *, scenario: str, seller_stock: dict,
                              retailer_demand: dict) -> dict:
        """Report public market changes; never access private reservation prices."""
        if scenario == "s2_shortage":
            return {
                "signal": "STOCK_SHORTAGE",
                "summary": "In this synthetic scenario, Seller S2 can supply only 100 packets.",
                "product": "market_s2_stock",
                "quantity": seller_stock["S2"],
            }
        if scenario == "price_pressure":
            return {
                "signal": "INPUT_COST_PRESSURE",
                "summary": "A simulated input-cost shock changes S2's own internal pricing policy.",
                "product": "market_input_cost_pressure",
                "quantity": 1,
            }
        if scenario == "demand_surge":
            return {
                "signal": "DEMAND_SURGE",
                "summary": "Retailer R1's simulated demand rises to 240 packets.",
                "product": "market_r1_demand",
                "quantity": retailer_demand["R1"],
            }
        return {
            "signal": "STABLE",
            "summary": "No synthetic market shock is active.",
            "product": "market_stable",
            "quantity": 1,
        }
