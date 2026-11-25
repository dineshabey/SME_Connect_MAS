from dataclasses import dataclass
from .base_agent import BaseAgent

@dataclass(frozen=True)
class DeliveryAgent(BaseAgent):
    capacity: int
    cost_per_trip: float
