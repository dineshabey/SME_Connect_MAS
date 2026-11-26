"""Visualization must render recorded events without fabricating business actions."""
from dashboard.negotiation_viz import neon_scene


def test_neon_scene_renders_real_event():
    timeline = [
        {"round": 1, "sender": "R1", "receiver": "S1",
         "performative": "PROPOSE", "price": 150, "reason": "Initial offer"},
        {"round": 1, "sender": "S1", "receiver": "R1",
         "performative": "PROPOSE", "price": 155, "reason": "Seller counter"},
        {"round": 1, "sender": "R1", "receiver": "S1",
         "performative": "ACCEPT-PROPOSAL", "price": 155, "reason": "Retailer accepts"},
    ]
    html = neon_scene(timeline, 1, "R1", "S1")
    assert "Seller Thinking" in html
    assert "Retailer Thinking" in html
    assert "COUNTER-OFFER" in html
    assert "155.00" in html
    assert "Seller counter" in html
    assert "AGREEMENT REACHED" not in html  # Not a committed sale


def test_neon_scene_escapes_untrusted_reason():
    timeline = [{"round": 1, "sender": "R1", "receiver": "S1",
                 "performative": "PROPOSE", "price": 150,
                 "reason": "<script>alert(1)</script>"}]
    output = neon_scene(timeline, 0, "R1", "S1")
    assert "&lt;script&gt;" in output
    assert "<script>alert(1)</script>" not in output
    assert "Operator-configured first proposal" in output


def test_empty_scene():
    assert "No recorded negotiation events" in neon_scene([], 0, "R1", "S1")
