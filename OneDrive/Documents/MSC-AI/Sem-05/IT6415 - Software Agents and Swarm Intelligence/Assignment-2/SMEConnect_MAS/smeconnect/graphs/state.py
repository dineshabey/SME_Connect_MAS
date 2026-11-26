"""Private per-agent LangGraph state."""
from typing import TypedDict
from typing_extensions import NotRequired

class SellerGraphState(TypedDict):
    minimum_price: float
    target_price: float
    stock: int
    strategy: NotRequired[str]
    offered_price: float
    requested_quantity: int
    decision: str
    counter_price: NotRequired[float | None]
    reason: NotRequired[str]

class RetailerGraphState(TypedDict):
    budget: float
    demand: int
    maximum_price: float
    target_price: float
    expected_retail_price: float
    offered_price: float
    requested_quantity: int
    purchase_cost: float
    expected_gross_profit: float
    counter_price: float | None
    decision: str
    reason: str
    negotiation_round: NotRequired[int]
