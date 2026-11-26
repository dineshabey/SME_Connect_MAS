"""Session-scoped all-or-nothing simulated stock, budget and capacity reservations."""
from dataclasses import dataclass, field
from math import isfinite
from smeconnect.environment.marketplace import build_agents

@dataclass
class ReservationLedger:
    seller_stock: dict[str, int]
    retailer_budget: dict[str, float]
    retailer_demand: dict[str, int]
    delivery_capacity: dict[str, int]
    reservations: list[dict] = field(default_factory=list)

    @classmethod
    def from_marketplace(cls) -> "ReservationLedger":
        agents = build_agents()
        return cls(
            seller_stock={a.agent_id: a.available_stock for a in agents if a.role == "seller"},
            retailer_budget={a.agent_id: a.budget for a in agents if a.role == "retailer"},
            retailer_demand={a.agent_id: a.demand for a in agents if a.role == "retailer"},
            delivery_capacity={a.agent_id: a.capacity for a in agents if a.role == "delivery"},
        )

    def reserve(self, *, order_id: str, seller_id: str, retailer_id: str,
                delivery_id: str, quantity: int, unit_price: float, delivery_fee: float) -> dict:
        """Validate every constraint before any mutation; caller manages sequential access."""
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        if not (isfinite(unit_price) and isfinite(delivery_fee)
                and unit_price >= 0 and delivery_fee >= 0):
            raise ValueError("Prices and delivery fee must be finite and nonnegative.")
        if any(x["order_id"] == order_id for x in self.reservations):
            raise ValueError("Duplicate order ID.")
        if seller_id not in self.seller_stock or retailer_id not in self.retailer_budget:
            raise ValueError("Unknown seller or retailer.")
        if delivery_id not in self.delivery_capacity:
            raise ValueError("Unknown delivery agent.")
        total = round(unit_price * quantity + delivery_fee, 2)
        if self.seller_stock[seller_id] < quantity:
            raise ValueError("Seller has insufficient unreserved stock.")
        if self.retailer_demand[retailer_id] < quantity:
            raise ValueError("Retailer has insufficient remaining demand.")
        if self.delivery_capacity[delivery_id] < quantity:
            raise ValueError("Delivery capacity already allocated.")
        if self.retailer_budget[retailer_id] + 1e-9 < total:
            raise ValueError("Retailer has insufficient unreserved budget.")
        record = {"order_id": order_id, "seller_id": seller_id, "retailer_id": retailer_id,
                  "delivery_id": delivery_id, "quantity": quantity,
                  "unit_price": unit_price, "delivery_fee": delivery_fee,
                  "reserved_total": total, "status": "RESERVED_SIMULATED"}
        self.seller_stock[seller_id] -= quantity
        self.retailer_demand[retailer_id] -= quantity
        self.retailer_budget[retailer_id] = round(self.retailer_budget[retailer_id] - total, 2)
        self.delivery_capacity[delivery_id] -= quantity
        self.reservations.append(record)
        return dict(record)
