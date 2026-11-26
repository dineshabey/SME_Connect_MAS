"""Phase 04 end-to-end resource coordination, failure and safety regression tests."""
import pytest
from smeconnect.graphs.delivery_graph import build_delivery_graph
from smeconnect.graphs.retailer_order_graph import build_retailer_order_graph
from smeconnect.simulation.fulfillment import run_delivery_coordination
from smeconnect.simulation.reservation_ledger import ReservationLedger
from smeconnect.simulation.supplier_selection import run_supplier_competition


def competition(quantity=100, initial_price=150):
    return run_supplier_competition(
        retailer_id="R1", quantity=quantity, initial_price=initial_price,
    )


def test_delivery_agent_independent_capacity_decision():
    graph = build_delivery_graph()
    state = dict(requested_quantity=200, remaining_capacity=400,
                 cost_per_trip=1000.0, decision="", quoted_fee=None, reason="")
    accepted = graph.invoke(state)
    assert accepted["decision"] == "AVAILABLE"
    assert accepted["quoted_fee"] == 1000
    state["remaining_capacity"] = 100
    rejected = graph.invoke(state)
    assert rejected["decision"] == "REJECT"
    assert rejected["quoted_fee"] is None


def test_retailer_includes_delivery_fee_before_accepting():
    graph = build_retailer_order_graph()
    state = dict(unit_price=150.0, quantity=200, delivery_fee=1000.0,
                 remaining_budget=35000.0, remaining_demand=200,
                 maximum_price=165.0, expected_retail_price=200.0,
                 total_commitment=0.0, expected_net_margin=0.0,
                 decision="", reason="")
    accepted = graph.invoke(state)
    assert accepted["decision"] == "ACCEPT"
    assert accepted["total_commitment"] == 31000
    assert accepted["expected_net_margin"] == 9000
    state["remaining_budget"] = 30000.0
    assert graph.invoke(state)["decision"] == "REJECT"


def test_success_reserves_all_resources_and_records_agent_messages():
    ledger = ReservationLedger.from_marketplace()
    outcome = run_delivery_coordination(competition(200), ledger, quantity=200)
    assert outcome["status"] == "RESERVED_SIMULATED"
    assert outcome["selected_seller_id"] == "S2"
    assert outcome["reservation"]["reserved_total"] == 31000
    assert ledger.seller_stock["S2"] == 100
    assert ledger.retailer_budget["R1"] == 4000
    assert ledger.retailer_demand["R1"] == 0
    assert ledger.delivery_capacity["D1"] == 200
    assert len(ledger.reservations) == 1
    assert any(msg.sender == "D1" and msg.receiver == "C1" for msg in outcome["messages"])
    assert any(msg.sender == "R1" and msg.receiver == "C1" for msg in outcome["messages"])
    assert len({msg.conversation_id for msg in outcome["messages"]}) == 1


def test_no_agreement_leaves_ledger_unchanged():
    ledger = ReservationLedger.from_marketplace()
    before = ledger.seller_stock.copy()
    result = run_delivery_coordination(competition(initial_price=100), ledger, quantity=100)
    assert result["status"] == "NO_AGREEMENT"
    assert ledger.seller_stock == before
    assert ledger.reservations == []


def test_delivery_capacity_failure_does_not_mutate_resources():
    ledger = ReservationLedger.from_marketplace()
    ledger.delivery_capacity["D1"] = 50
    original_stock = ledger.seller_stock.copy()
    original_budget = ledger.retailer_budget.copy()
    result = run_delivery_coordination(competition(100), ledger, quantity=100)
    assert result["status"] == "DELIVERY_UNAVAILABLE"
    assert ledger.seller_stock == original_stock
    assert ledger.retailer_budget == original_budget
    assert ledger.reservations == []


def test_retailer_rejects_when_delivery_exceeds_budget():
    ledger = ReservationLedger.from_marketplace()
    ledger.retailer_budget["R1"] = 15000
    result = run_delivery_coordination(competition(100), ledger, quantity=100)
    assert result["status"] == "RETAILER_DECLINED"
    assert ledger.reservations == []
    assert ledger.retailer_budget["R1"] == 15000


def test_stock_unavailable_after_selection_rejects_without_booking():
    ledger = ReservationLedger.from_marketplace()
    ledger.seller_stock["S2"] = 5
    result = run_delivery_coordination(competition(100), ledger, quantity=100)
    assert result["status"] == "STOCK_UNAVAILABLE"
    assert ledger.reservations == []


def test_repeated_booking_cannot_over_allocate_retailer_demand():
    ledger = ReservationLedger.from_marketplace()
    first = run_delivery_coordination(competition(200), ledger, quantity=200)
    second = run_delivery_coordination(competition(200), ledger, quantity=200)
    assert first["status"] == "RESERVED_SIMULATED"
    assert second["status"] == "DEMAND_EXHAUSTED"
    assert len(ledger.reservations) == 1
    assert ledger.retailer_budget["R1"] == 4000


def test_ledger_duplicate_ids_and_invalid_quantity_never_mutate():
    ledger = ReservationLedger.from_marketplace()
    params = dict(order_id="SIM-ONE", seller_id="S2", retailer_id="R1",
                  delivery_id="D1", quantity=100, unit_price=150.0, delivery_fee=1000.0)
    ledger.reserve(**params)
    before = ledger.seller_stock.copy()
    with pytest.raises(ValueError, match="Duplicate"):
        ledger.reserve(**params)
    with pytest.raises(ValueError):
        ledger.reserve(**{**params, "order_id": "SIM-TWO", "quantity": 0})
    with pytest.raises(ValueError):
        ledger.reserve(**{**params, "order_id": "SIM-THREE", "unit_price": float("nan")})
    assert ledger.seller_stock == before


def test_reject_fabricated_negotiation_price_and_quantity():
    ledger = ReservationLedger.from_marketplace()
    candidate = competition(100)
    candidate["selection"]["selected_price"] = 1.0
    with pytest.raises(ValueError, match="authentic negotiation"):
        run_delivery_coordination(candidate, ledger, quantity=100)
    assert ledger.reservations == []
    with pytest.raises(ValueError, match="authentic negotiation"):
        run_delivery_coordination(competition(100), ledger, quantity=101)
    assert ledger.reservations == []
