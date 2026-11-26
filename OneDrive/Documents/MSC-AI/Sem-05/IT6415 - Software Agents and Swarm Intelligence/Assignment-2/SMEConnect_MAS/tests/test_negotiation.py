"""Phase 02 peer-to-peer message and negotiation tests."""
import pytest
from pydantic import ValidationError
from smeconnect.communication.message_bus import InMemoryMessageBus
from smeconnect.communication.message_schema import AgentMessage, Performative
from smeconnect.simulation.negotiation import run_negotiation

def test_two_way_agreement():
    r = run_negotiation(initial_price=150)
    assert r["status"] == "AGREED"
    assert r["agreed_price"] == 155
    assert [m.sender for m in r["messages"]] == ["R1", "S1", "R1"]
    assert r["messages"][-1].performative == Performative.ACCEPT
    assert len({m.conversation_id for m in r["messages"]}) == 1

def test_reject_below_seller_minimum():
    r = run_negotiation(initial_price=140)
    assert r["status"] == "REJECTED"
    assert r["messages"][-1].performative == Performative.REJECT

def test_reject_above_retailer_maximum():
    assert run_negotiation(initial_price=165)["status"] == "REJECTED"

def test_bounded_negotiation():
    r = run_negotiation(initial_price=160, max_rounds=1)
    assert r["status"] == "MAX_ROUNDS"
    assert r["rounds"] == 1
    assert len(r["messages"]) <= 3

def test_reject_nan_infinite_price():
    for bad in [float("nan"), float("inf"), float("-inf")]:
        with pytest.raises(ValidationError):
            AgentMessage(sender="R1", receiver="S1", performative=Performative.PROPOSE,
                conversation_id="X", product="peanuts", quantity=20, unit_price=bad)

def test_reject_sender_impersonation():
    bus = InMemoryMessageBus({"S1", "R1"})
    m = AgentMessage(sender="S1", receiver="R1", performative=Performative.PROPOSE,
        conversation_id="X", product="peanuts", quantity=20, unit_price=150)
    with pytest.raises(PermissionError):
        bus.send(m, actor_id="R1")
