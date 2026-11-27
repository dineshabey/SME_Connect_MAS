"""Bounded and reproducible evaluation of Phase 05 market adaptation.

Every result is computed from actual Phase 05.1 negotiation runs. No random
sampling, fictitious results, inventory reservations or external API calls.
"""
from itertools import product
from math import isfinite
from statistics import mean

from smeconnect.environment.market_state import SCENARIO_NAMES
from smeconnect.simulation.market_experiment import run_market_experiment

CHANGED_SCENARIOS = ("s2_shortage", "price_pressure", "demand_surge")
DEFAULT_QUANTITIES = (100, 200)
DEFAULT_OFFERS = (140.0, 150.0, 160.0)
MAX_TRIALS = 36


def _validate_values(scenarios, quantities, initial_prices, max_rounds):
    if not scenarios or len(set(scenarios)) != len(scenarios) or any(
        name not in CHANGED_SCENARIOS for name in scenarios
    ):
        raise ValueError("Select distinct supported changed-market scenarios.")
    if not quantities or len(set(quantities)) != len(quantities) or any(
        isinstance(q, bool) or not isinstance(q, int) or not 1 <= q <= 200
        for q in quantities
    ):
        raise ValueError("Quantities must be distinct integers from 1 to 200 for R1.")
    if not initial_prices or len(set(initial_prices)) != len(initial_prices) or any(
        isinstance(price, bool) or not isinstance(price, (int, float))
        or not isfinite(price) or not 0 < price <= 1000
        for price in initial_prices
    ):
        raise ValueError("Initial offers must be distinct finite, positive prices.")
    if isinstance(max_rounds, bool) or not isinstance(max_rounds, int) or not 1 <= max_rounds <= 10:
        raise ValueError("Maximum negotiation rounds must be 1–10.")
    if len(scenarios) * len(quantities) * len(initial_prices) > MAX_TRIALS:
        raise ValueError(f"Experiment limited to {MAX_TRIALS} paired trials.")


def _snapshot_metrics(comp: dict) -> dict:
    """Only public outcomes and message counts, not private reservation prices."""
    chosen = comp["selection"]["selected_seller_id"]
    negotiators = list(comp["negotiations"].values())
    return {
        "selected_seller": chosen,
        "selected_price": comp["selection"]["selected_price"],
        "expected_gross_profit": comp["selection"]["expected_gross_profit"],
        "message_count": sum(len(run["messages"]) for run in negotiators),
        "round_count": sum(run["rounds"] for run in negotiators),
        "agreements": sum(run["status"] == "AGREED" for run in negotiators),
        "rejections": sum(run["status"] == "REJECTED" for run in negotiators),
        "negotiation_count": len(negotiators),
    }


def _aggregate(rows: list[dict], *, scenario: str) -> dict:
    total = len(rows)
    assert total > 0
    baseline = [r["before"] for r in rows]
    changed = [r["after"] for r in rows]

    def group_stats(items):
        successes = [x for x in items if x["selected_seller"] is not None]
        selected_prices = [x["selected_price"] for x in successes]
        negotiations = sum(x["negotiation_count"] for x in items)
        return {
            "selection_rate_pct": round(100 * len(successes) / total, 2),
            "mean_selected_price_rs": round(mean(selected_prices), 2) if selected_prices else None,
            "mean_expected_gross_profit_rs": round(
                mean(x["expected_gross_profit"] for x in items), 2
            ),
            "mean_messages_per_trial": round(mean(x["message_count"] for x in items), 2),
            "mean_negotiation_rounds_per_trial": round(mean(x["round_count"] for x in items), 2),
            "seller_agreement_rate_pct": round(
                100 * sum(x["agreements"] for x in items) / negotiations, 2
            ),
        }

    return {
        "scenario": scenario,
        "scenario_name": SCENARIO_NAMES[scenario],
        "paired_trials": total,
        "supplier_switches": sum(
            x["selected_seller"] != y["selected_seller"]
            for x, y in zip(baseline, changed)
        ),
        "supplier_switch_rate_pct": round(
            100 * sum(x["selected_seller"] != y["selected_seller"]
                      for x, y in zip(baseline, changed)) / total, 2
        ),
        "normal": group_stats(baseline),
        "changed": group_stats(changed),
    }


def run_experiment_batch(
    *, scenarios: tuple[str, ...] = CHANGED_SCENARIOS,
    quantities: tuple[int, ...] = DEFAULT_QUANTITIES,
    initial_prices: tuple[float, ...] = DEFAULT_OFFERS,
    retailer_target: float = 150.0,
    max_rounds: int = 5,
) -> dict:
    """Evaluate deterministic paired market experiments for retailer R1.

    A paired trial compares two independent snapshots with identical quantity,
    initial offer, preferred price and maximum rounds. Totals include a separate
    normal-market baseline for EACH shock. Order is deterministic.
    """
    scenarios = tuple(scenarios)
    quantities = tuple(quantities)
    initial_prices = tuple(initial_prices)
    _validate_values(scenarios, quantities, initial_prices, max_rounds)
    if isinstance(retailer_target, bool) or not isinstance(retailer_target, (int, float)) or (
        not isfinite(retailer_target) or not 0 < retailer_target <= 1000
    ):
        raise ValueError("Target price must be finite and positive.")
    trials = []
    for scenario, qty, offer in product(scenarios, quantities, initial_prices):
        outcome = run_market_experiment(
            scenario=scenario, retailer_id="R1", quantity=qty,
            initial_price=float(offer), retailer_target=float(retailer_target),
            max_rounds=max_rounds,
        )
        before = _snapshot_metrics(outcome["baseline"])
        after = _snapshot_metrics(outcome["changed"])
        trials.append({
            "scenario": scenario,
            "scenario_name": SCENARIO_NAMES[scenario],
            "quantity": qty,
            "initial_price_rs": float(offer),
            "before": before,
            "after": after,
            "supplier_changed": before["selected_seller"] != after["selected_seller"],
        })
    groups = [
        _aggregate([trial for trial in trials if trial["scenario"] == scenario],
                   scenario=scenario)
        for scenario in scenarios
    ]
    return {
        "config": {
            "scenarios": list(scenarios),
            "quantities": list(quantities),
            "initial_prices": [float(p) for p in initial_prices],
            "retailer": "R1",
            "retailer_target": float(retailer_target),
            "max_rounds": max_rounds,
            "paired_trials": len(trials),
            "snapshot_runs": len(trials) * 2,
            "method": "Deterministic factorial grid; independent snapshots for each pair",
        },
        "trials": trials,
        "summary": groups,
        "limitations": (
            "These metrics describe a fixed synthetic rule-based model, not real SME data. "
            "Supplier switching is a response to changed inputs, not proof of learning "
            "or emergent self-organization. No orders or delivery transactions occur."
        ),
    }


def flat_trial_rows(batch: dict) -> list[dict]:
    """Stable, CSV-ready PUBLIC summary; exclude private seller state and IDs."""
    rows = []
    for trial in batch["trials"]:
        before, after = trial["before"], trial["after"]
        rows.append({
            "scenario": trial["scenario"],
            "quantity": trial["quantity"],
            "initial_price_rs": trial["initial_price_rs"],
            "before_supplier": before["selected_seller"] or "NONE",
            "after_supplier": after["selected_seller"] or "NONE",
            "supplier_changed": trial["supplier_changed"],
            "before_price_rs": before["selected_price"],
            "after_price_rs": after["selected_price"],
            "before_expected_gross_profit_rs": before["expected_gross_profit"],
            "after_expected_gross_profit_rs": after["expected_gross_profit"],
            "before_messages": before["message_count"],
            "after_messages": after["message_count"],
            "before_rounds": before["round_count"],
            "after_rounds": after["round_count"],
        })
    return rows
