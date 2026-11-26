"""Phase 03: discovery, independent competition and retailer-owned selection."""
import pytest
from smeconnect.agents.coordinator_agent import CoordinatorAgent
from smeconnect.environment.marketplace import build_agents
from smeconnect.graphs.supplier_selection_graph import build_supplier_selection_graph
from smeconnect.simulation.supplier_selection import run_supplier_competition


def test_coordinator_discovers_only_registered_sellers():
    agents = build_agents()
    coordinator = next(a for a in agents if a.role == "coordinator")
    assert coordinator.discover_sellers(agents) == ["S1", "S2"]
    assert coordinator.discover_sellers(agents, exclude_ids={"S1"}) == ["S2"]


def test_default_competition_selects_volume_seller():
    outcome = run_supplier_competition()
    assert set(outcome["negotiations"]) == {"S1", "S2"}
    assert outcome["negotiations"]["S1"]["status"] == "AGREED"
    assert outcome["negotiations"]["S2"]["status"] == "AGREED"
    assert outcome["negotiations"]["S1"]["agreed_price"] == 155
    assert outcome["negotiations"]["S2"]["agreed_price"] == 150
    assert outcome["selection"]["selected_seller_id"] == "S2"
    assert outcome["selection"]["selected_price"] == 150
    assert outcome["selection"]["expected_gross_profit"] == 10000
    conversations = [r["conversation_id"] for r in outcome["negotiations"].values()]
    assert len(set(conversations)) == 2


def test_all_sellers_reject_unacceptable_initial_offer():
    outcome = run_supplier_competition(initial_price=100)
    assert outcome["selection"]["selected_seller_id"] is None
    assert all(r["status"] == "REJECTED" for r in outcome["negotiations"].values())


def test_supplier_selection_uses_only_public_agreements():
    offers = [
        {"seller_id": "S1", "status": "AGREED", "agreed_price": 160, "rounds": 2},
        {"seller_id": "S2", "status": "AGREED", "agreed_price": 155, "rounds": 3},
    ]
    result = build_supplier_selection_graph().invoke({
        "offers": offers, "requested_quantity": 100,
        "budget": 20000.0, "maximum_price": 165.0,
        "expected_retail_price": 200.0,
        "selected_seller_id": None, "selected_price": None,
        "expected_gross_profit": 0.0, "reasoning": "", "evaluations": [],
    })
    assert result["selected_seller_id"] == "S2"
    assert all("minimum_price" not in row for row in result["evaluations"])


def test_tie_breaker_is_deterministic():
    offers = [
        {"seller_id": "S2", "status": "AGREED", "agreed_price": 150, "rounds": 2},
        {"seller_id": "S1", "status": "AGREED", "agreed_price": 150, "rounds": 1},
    ]
    result = build_supplier_selection_graph().invoke({
        "offers": offers, "requested_quantity": 100,
        "budget": 20000.0, "maximum_price": 165.0,
        "expected_retail_price": 200.0,
        "selected_seller_id": None, "selected_price": None,
        "expected_gross_profit": 0.0, "reasoning": "", "evaluations": [],
    })
    assert result["selected_seller_id"] == "S1"


def test_invalid_seller_selection_and_quantity():
    with pytest.raises(ValueError):
        run_supplier_competition(seller_ids=["S1", "NOT_REGISTERED"])
    with pytest.raises(ValueError):
        run_supplier_competition(seller_ids=["S1", "S1"])
    with pytest.raises(ValueError):
        run_supplier_competition(quantity=201, retailer_id="R1")
    with pytest.raises(ValueError):
        run_supplier_competition(quantity=151, retailer_id="R2")


def test_single_seller_still_supported():
    outcome = run_supplier_competition(seller_ids=["S1"])
    assert outcome["evaluated_seller_ids"] == ["S1"]
    assert outcome["selection"]["selected_seller_id"] == "S1"
