"""Phase 05.1 scenario isolation, observable adaptation, and protocol tests."""
import pytest
from smeconnect.environment.market_state import MarketSnapshot, market_snapshot
from smeconnect.environment.marketplace import build_agents
from smeconnect.simulation.market_experiment import run_market_experiment
from smeconnect.simulation.supplier_selection import run_supplier_competition


def test_normal_snapshot_preserves_phase03_default():
    base = run_supplier_competition()
    normal = run_supplier_competition(market_state=market_snapshot("normal"))
    assert base["selection"]["selected_seller_id"] == "S2"
    assert normal["selection"]["selected_seller_id"] == "S2"
    assert normal["selection"]["selected_price"] == base["selection"]["selected_price"]


def test_stock_shortage_changes_supplier_via_real_seller_graph():
    result = run_market_experiment(scenario="s2_shortage", quantity=200)
    assert result["before"]["selected_seller"] == "S2"
    assert result["after"]["selected_seller"] == "S1"
    after_s2 = result["changed"]["negotiations"]["S2"]
    assert after_s2["status"] == "REJECTED"
    assert any("stock" in event["reason"].lower() or "quantity" in event["reason"].lower()
               for event in after_s2["timeline"])
    assert result["observable_state"]["after"]["stock_S2"] == 100


def test_price_pressure_changes_selection_without_private_price_leakage():
    result = run_market_experiment(scenario="price_pressure", quantity=200)
    assert result["before"]["selected_seller"] == "S2"
    assert result["after"]["selected_seller"] == "S1"
    assert result["changed"]["negotiations"]["S2"]["status"] == "REJECTED"
    signal = result["market_signal"]
    assert signal["signal"] == "INPUT_COST_PRESSURE"
    assert "minimum_price" not in signal
    assert "target_price" not in signal
    for message in result["signal_messages"]:
        assert message.sender == "M1"
        assert message.receiver == "R1"
        assert message.performative.value == "INFORM"
        assert message.unit_price == 0.0


def test_demand_surge_changes_demand_not_necessarily_winner():
    result = run_market_experiment(scenario="demand_surge", quantity=200)
    assert result["observable_state"]["before"]["demand_R1"] == 200
    assert result["observable_state"]["after"]["demand_R1"] == 240
    assert result["before"]["selected_seller"] == "S2"
    assert result["after"]["selected_seller"] == "S2"


def test_market_state_isolated_from_base_instances():
    changed = {a.agent_id: a for a in build_agents(market_snapshot("s2_shortage"))}
    unchanged = {a.agent_id: a for a in build_agents()}
    assert changed["S2"].available_stock == 100
    assert unchanged["S2"].available_stock == 300


def test_invalid_scenario_and_bad_state_rejected():
    with pytest.raises(ValueError):
        market_snapshot("unknown")
    with pytest.raises(ValueError):
        MarketSnapshot(scenario="s2_shortage", seller_stock={"S2": -5})
    with pytest.raises(ValueError):
        MarketSnapshot(scenario="normal", retailer_demand={"R1": True})
    with pytest.raises(ValueError):
        run_market_experiment(scenario="normal")
    with pytest.raises(ValueError):
        run_market_experiment(scenario="s2_shortage", quantity=201)


def test_market_messages_are_typed_and_separate_from_negotiation():
    result = run_market_experiment(scenario="s2_shortage")
    assert len(result["signal_messages"]) == 1
    market = result["signal_messages"][0]
    assert market.product == "market_s2_stock"
    assert market.quantity == 100
    assert market.conversation_id.startswith("MARKET-")
    assert market.conversation_id != result["changed"]["negotiations"]["S1"]["conversation_id"]
    assert all("minimum_price" not in record for record in result["after"]["offers"])
