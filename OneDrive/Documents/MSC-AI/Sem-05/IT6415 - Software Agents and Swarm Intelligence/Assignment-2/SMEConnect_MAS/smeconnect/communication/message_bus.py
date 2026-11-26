"""In-memory bus with bounded volume and actor-context checks."""
from collections import defaultdict
from .message_schema import AgentMessage

class InMemoryMessageBus:
    def __init__(self, registered_agents: set[str] | None = None, max_messages: int = 200):
        self._inboxes: dict[str, list[AgentMessage]] = defaultdict(list)
        self.history: list[AgentMessage] = []
        self.registered_agents = registered_agents
        self.max_messages = max_messages

    def send(self, message: AgentMessage, *, actor_id: str | None = None) -> None:
        if actor_id is not None and actor_id != message.sender:
            raise PermissionError("Sender does not match invoking actor.")
        if self.registered_agents is not None:
            if message.sender not in self.registered_agents or message.receiver not in self.registered_agents:
                raise PermissionError("Unknown registered agent identity.")
        if len(self.history) >= self.max_messages:
            raise RuntimeError("Message limit reached for this simulation.")
        self._inboxes[message.receiver].append(message)
        self.history.append(message)

    def receive(self, agent_id: str) -> list[AgentMessage]:
        messages = list(self._inboxes[agent_id])
        self._inboxes[agent_id].clear()
        return messages
