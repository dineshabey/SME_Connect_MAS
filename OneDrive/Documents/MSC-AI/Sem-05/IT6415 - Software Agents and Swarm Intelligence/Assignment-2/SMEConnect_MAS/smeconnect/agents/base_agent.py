from dataclasses import dataclass

@dataclass(frozen=True)
class BaseAgent:
    agent_id: str
    role: str
    goal: str
    strategy: str
