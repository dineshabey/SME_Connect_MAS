from collections import defaultdict
from .message_schema import AgentMessage

class InMemoryMessageBus:
    def __init__(self):
        self._inboxes: dict[str, list[AgentMessage]] = defaultdict(list)
        self.history: list[AgentMessage] = []

    def send(self, message: AgentMessage) -> None:
        self._inboxes[message.receiver].append(message)
        self.history.append(message)

    def receive(self, agent_id: str) -> list[AgentMessage]:
        messages = list(self._inboxes[agent_id])
        self._inboxes[agent_id].clear()
        return messages
