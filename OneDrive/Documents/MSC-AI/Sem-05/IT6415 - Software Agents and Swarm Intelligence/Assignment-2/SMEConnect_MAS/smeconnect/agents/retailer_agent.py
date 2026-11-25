from dataclasses import dataclass
from .base_agent import BaseAgent

@dataclass(frozen=True)
class RetailerAgent(BaseAgent):
    maximum_price: float
    demand: int
    budget: float
