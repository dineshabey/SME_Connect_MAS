from dataclasses import dataclass
from .base_agent import BaseAgent

@dataclass(frozen=True)
class SellerAgent(BaseAgent):
    minimum_price: float
    target_price: float
    available_stock: int
