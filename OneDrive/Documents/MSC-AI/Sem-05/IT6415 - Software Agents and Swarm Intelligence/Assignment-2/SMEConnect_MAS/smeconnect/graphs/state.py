from typing import TypedDict

class SellerGraphState(TypedDict):
    minimum_price: float
    target_price: float
    stock: int
    offered_price: float
    requested_quantity: int
    decision: str
