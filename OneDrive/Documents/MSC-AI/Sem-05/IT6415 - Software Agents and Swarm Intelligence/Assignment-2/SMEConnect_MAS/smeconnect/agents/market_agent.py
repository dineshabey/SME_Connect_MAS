from dataclasses import dataclass
from .base_agent import BaseAgent

@dataclass(frozen=True)
class MarketAgent(BaseAgent):
    demand_multiplier: float = 1.0
