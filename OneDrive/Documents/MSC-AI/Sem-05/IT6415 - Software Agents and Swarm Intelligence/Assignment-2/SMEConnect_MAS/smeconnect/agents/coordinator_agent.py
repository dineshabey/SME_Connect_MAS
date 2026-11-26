"""Coordinator supplies public agent discovery, not negotiation decisions."""
from .base_agent import BaseAgent


class CoordinatorAgent(BaseAgent):
    """Discover participating sellers by public role; commercial choices remain local."""

    def discover_sellers(self, agents, *, exclude_ids=()):
        excluded = set(exclude_ids)
        return sorted(
            (agent.agent_id for agent in agents
             if agent.role == "seller" and agent.agent_id not in excluded)
        )
