"""Phase 05.3: report-evidence export must reflect real simulation results."""
import csv
import json

from smeconnect.simulation.experiment_evaluation import run_experiment_batch
from smeconnect.simulation.export_evidence import export_evidence, render_results_markdown


def _one_real_pair():
    return run_experiment_batch(
        scenarios=("s2_shortage",),
        quantities=(200,),
        initial_prices=(150.0,),
    )


def test_evidence_export_matches_computed_batch(tmp_path):
    batch = _one_real_pair()
    paths = export_evidence(tmp_path / "evaluation", batch=batch)

    with paths["csv"].open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["scenario"] == "s2_shortage"
    assert rows[0]["before_supplier"] == batch["trials"][0]["before"]["selected_seller"]
    assert rows[0]["after_supplier"] == batch["trials"][0]["after"]["selected_seller"]

    data = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert data["config"] == batch["config"]
    assert data["summary"] == batch["summary"]
    assert data["status"] == "generated_from_executed_synthetic_simulation"

    markdown = paths["markdown"].read_text(encoding="utf-8")
    assert "S2 Stock Shortage" in markdown
    assert "100.00%" in markdown
    assert "not empirical observations" in markdown


def test_report_renders_numerical_table_from_batch_not_placeholders():
    text = render_results_markdown(_one_real_pair())
    assert "| S2 Stock Shortage | 1 |" in text
    assert "Rs. 10,000.00" in text
    assert "Rs. 9,000.00" in text
    assert "Insert measured value" not in text
