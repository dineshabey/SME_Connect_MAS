"""Controlled, immutable synthetic market snapshots for reproducible experiments.

These are scenario assumptions, not observations of real agricultural markets.
Private seller price constraints stay inside their SellerAgent state.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MarketSnapshot:
    scenario: str = "normal"
    seller_stock: dict[str, int] = field(default_factory=dict)
    retailer_demand: dict[str, int] = field(default_factory=dict)
    seller_minimum_adjustment: dict[str, float] = field(default_factory=dict)
    seller_target_adjustment: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if self.scenario not in SCENARIO_NAMES:
            raise ValueError("Unsupported market scenario.")
        for key, mapping in (("seller_stock", self.seller_stock),
                             ("retailer_demand", self.retailer_demand)):
            allowed = {"S1", "S2"} if key == "seller_stock" else {"R1", "R2"}
            if any(agent_id not in allowed or isinstance(value, bool)
                   or not isinstance(value, int) or value < 0 or value > 100000
                   for agent_id, value in mapping.items()):
                raise ValueError("Invalid stock or demand in market snapshot.")
        for mapping in (self.seller_minimum_adjustment, self.seller_target_adjustment):
            if any(agent_id not in {"S1", "S2"} or not isinstance(delta, (int, float))
                   or isinstance(delta, bool) or not -50 <= delta <= 100
                   for agent_id, delta in mapping.items()):
                raise ValueError("Invalid seller price adjustment.")

SCENARIO_NAMES = {
    "normal": "Normal Market",
    "s2_shortage": "S2 Stock Shortage",
    "price_pressure": "S2 Price Pressure",
    "demand_surge": "Retailer Demand Surge",
}

def market_snapshot(name: str = "normal") -> MarketSnapshot:
    if name == "normal":
        return MarketSnapshot(scenario=name)
    if name == "s2_shortage":
        return MarketSnapshot(scenario=name, seller_stock={"S2": 100})
    if name == "price_pressure":
        # Private constraints respond to a synthetic input cost shock.
        # No retailer or market signal receives the numerical private limits.
        return MarketSnapshot(scenario=name, seller_minimum_adjustment={"S2": 20.0},
                              seller_target_adjustment={"S2": 20.0})
    if name == "demand_surge":
        return MarketSnapshot(scenario=name, retailer_demand={"R1": 240})
    raise ValueError("Unsupported market scenario.")
