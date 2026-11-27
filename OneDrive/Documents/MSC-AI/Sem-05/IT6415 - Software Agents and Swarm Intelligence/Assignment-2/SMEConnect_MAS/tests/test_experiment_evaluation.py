"""Measured Phase 05.2 evaluations: real model outputs, deterministic inputs."""
import pytest
from smeconnect.simulation.experiment_evaluation import (
    flat_trial_rows, run_experiment_batch,
)


def test_stock_shortage_switches_supplier_for_200_packet_offer():
    result = run_experiment_batch(
        scenarios=("s2_shortage",), quantities=(200,), initial_prices=(150.0,)
    )
    assert result["config"]["paired_trials"] == 1
    assert result["config"]["snapshot_runs"] == 2
    trial = result["trials"][0]
    assert trial["before"]["selected_seller"] == "S2"
    assert trial["after"]["selected_seller"] == "S1"
    assert trial["supplier_changed"] is True
    assert result["summary"][0]["supplier_switch_rate_pct"] == 100.0
    assert trial["before"]["expected_gross_profit"] == 10000
    assert trial["after"]["expected_gross_profit"] == 9000


def test_unchanged_supplier_is_not_incorrectly_counted_as_adaptation():
    result = run_experiment_batch(
        scenarios=("demand_surge",), quantities=(200,), initial_prices=(150.0,)
    )
    assert result["summary"][0]["supplier_switch_rate_pct"] == 0.0
    assert result["trials"][0]["supplier_changed"] is False
    assert result["summary"][0]["normal"]["selection_rate_pct"] == 100.0
    assert result["summary"][0]["changed"]["selection_rate_pct"] == 100.0


def test_repeatable_measures_excluding_fresh_message_ids():
    args = dict(scenarios=("s2_shortage",), quantities=(100, 200),
                initial_prices=(140.0, 150.0), max_rounds=3)
    first = run_experiment_batch(**args)
    second = run_experiment_batch(**args)
    assert first == second
    assert len(first["trials"]) == 4
    assert all(t["before"]["message_count"] > 0 for t in first["trials"])
    assert all(t["after"]["message_count"] > 0 for t in first["trials"])


def test_flat_export_has_no_private_agent_constraints():
    result = run_experiment_batch(
        scenarios=("price_pressure",), quantities=(200,), initial_prices=(150.0,)
    )
    rows = flat_trial_rows(result)
    assert len(rows) == 1
    assert "before_supplier" in rows[0]
    assert "after_messages" in rows[0]
    assert all("minimum_price" not in field and "target_price" not in field
               for field in rows[0])
    assert result["trials"][0]["after"]["expected_gross_profit"] >= 0


@pytest.mark.parametrize("options", [
    {"scenarios": ()},
    {"scenarios": ("s2_shortage", "s2_shortage")},
    {"scenarios": ("unknown",)},
    {"quantities": (0,)},
    {"quantities": (201,)},
    {"quantities": (True,)},
    {"initial_prices": (float("nan"),)},
    {"initial_prices": (150.0, 150.0)},
    {"max_rounds": 0},
    {"max_rounds": 11},
    {"max_rounds": True},
    {"retailer_target": float("inf")},
])
def test_experiment_validation_rejects_invalid_parameters(options):
    with pytest.raises(ValueError):
        run_experiment_batch(**options)


def test_multi_scenario_aggregation_totals_match_trial_rows():
    result = run_experiment_batch(
        scenarios=("s2_shortage", "price_pressure", "demand_surge"),
        quantities=(100,), initial_prices=(150.0,)
    )
    assert len(result["trials"]) == 3
    assert sum(x["paired_trials"] for x in result["summary"]) == 3
    assert sum(x["supplier_switches"] for x in result["summary"]) == sum(
        trial["supplier_changed"] for trial in result["trials"]
    )
    for group in result["summary"]:
        assert 0 <= group["normal"]["selection_rate_pct"] <= 100
        assert 0 <= group["changed"]["selection_rate_pct"] <= 100
        assert group["normal"]["mean_messages_per_trial"] >= 2
