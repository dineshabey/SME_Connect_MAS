"""Phase 02 tests: retailer decisions, constraints, and private goals."""
from smeconnect.graphs.retailer_graph import build_retailer_graph


def evaluate(**overrides):
    state = {
        "budget": 35000.0, "demand": 200,
        "maximum_price": 170.0, "target_price": 150.0,
        "expected_retail_price": 200.0, "offered_price": 165.0,
        "requested_quantity": 200,
        "purchase_cost": 0.0, "expected_gross_profit": 0.0,
        "counter_price": None, "decision": "", "reason": "",
    }
    state.update(overrides)
    return build_retailer_graph().invoke(state)


def test_counter_offer_and_utility():
    result = evaluate()
    assert result["decision"] == "COUNTER_OFFER"
    assert result["counter_price"] == 150.0
    assert result["purchase_cost"] == 33000.0
    assert result["expected_gross_profit"] == 7000.0


def test_accept_target_price():
    result = evaluate(offered_price=145.0)
    assert result["decision"] == "ACCEPT"
    assert result["counter_price"] is None


def test_reject_over_budget():
    result = evaluate(budget=30000.0)
    assert result["decision"] == "REJECT"
    assert "budget" in result["reason"]


def test_reject_above_maximum_price():
    assert evaluate(offered_price=180.0)["decision"] == "REJECT"


def test_reject_over_demand():
    assert evaluate(requested_quantity=250)["decision"] == "REJECT"


def test_reject_zero_quantity_without_division_error():
    assert evaluate(requested_quantity=0)["decision"] == "REJECT"


def test_reject_nonprofitable_offer():
    result = evaluate(expected_retail_price=165.0)
    assert result["decision"] == "REJECT"


def test_different_retailer_goals_change_decisions():
    assert evaluate(target_price=170.0)["decision"] == "ACCEPT"
    assert evaluate(target_price=150.0)["decision"] == "COUNTER_OFFER"
