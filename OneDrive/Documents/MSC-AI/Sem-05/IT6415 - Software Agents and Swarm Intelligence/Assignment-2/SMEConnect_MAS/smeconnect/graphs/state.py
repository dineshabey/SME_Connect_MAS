"""Typed state passed through independent LangGraph agent workflows."""
from typing import TypedDict


class SellerGraphState(TypedDict):
    minimum_price: float
    target_price: float
    stock: int
    offered_price: float
    requested_quantity: int
    decision: str


class RetailerGraphState(TypedDict):
    # The retailer knows only its own constraints and the received offer.
    budget: float
    demand: int
    maximum_price: float
    target_price: float
    expected_retail_price: float
    offered_price: float
    requested_quantity: int

    # Populated by the LangGraph nodes.
    purchase_cost: float
    expected_gross_profit: float
    counter_price: float | None
    decision: str
    reason: str
