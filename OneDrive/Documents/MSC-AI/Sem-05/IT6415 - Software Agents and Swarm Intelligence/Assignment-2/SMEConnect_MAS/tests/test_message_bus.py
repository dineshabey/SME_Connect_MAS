from smeconnect.communication.message_bus import InMemoryMessageBus
from smeconnect.communication.message_schema import AgentMessage, Performative

def test_send_receive():
    bus = InMemoryMessageBus()
    bus.send(AgentMessage(sender="R1",receiver="S1",performative=Performative.PROPOSE,conversation_id="N1",product="peanuts",quantity=5,unit_price=160))
    assert len(bus.receive("S1")) == 1
    assert bus.receive("S1") == []
