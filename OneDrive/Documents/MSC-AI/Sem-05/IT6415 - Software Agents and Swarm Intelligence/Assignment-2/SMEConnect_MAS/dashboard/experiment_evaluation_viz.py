"""Phase 05.2 evaluation dashboard: measured simulation metrics and CSV evidence."""
import csv
import io
import json

import streamlit as st

from smeconnect.environment.market_state import SCENARIO_NAMES
from smeconnect.simulation.experiment_evaluation import (
    CHANGED_SCENARIOS, flat_trial_rows, run_experiment_batch,
)


def _to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _metric(value, *, percent=False, rupees=False):
    if value is None:
        return "N/A"
    if percent:
        return f"{value:,.1f}%"
    if rupees:
        return f"Rs. {value:,.2f}"
    return str(value)


def render_experiment_evaluation() -> None:
    st.subheader("🧪 Phase 05.2 · Experimental Evaluation Lab")
    st.caption("Measured outcomes of repeated independent LangGraph simulations; no fabricated data.")
    st.info(
        "**සිංහලෙන්:** Market scenarios කිහිපයක් run කරලා Agent decisions, "
        "negotiation messages, price සහ supplier changes සසඳමු."
    )
    st.markdown("### 1 · Define a reproducible experiment")
    selected = st.multiselect(
        "Market scenarios",
        list(CHANGED_SCENARIOS),
        default=list(CHANGED_SCENARIOS),
        format_func=lambda name: SCENARIO_NAMES[name],
        key="eval5_scenarios",
    )
    col1, col2, col3 = st.columns(3)
    quantities = col1.multiselect(
        "Order quantity (packets)", [100, 150, 200],
        default=[100, 200], key="eval5_quantities",
    )
    offers = col2.multiselect(
        "Initial offered price (Rs.)", [140, 150, 160],
        default=[140, 150, 160], key="eval5_prices",
    )
    max_rounds = col3.slider(
        "Maximum negotiation rounds", 1, 10, 5, key="eval5_max_rounds",
    )
    pairs = len(selected) * len(quantities) * len(offers)
    st.caption(
        f"Planned: **{pairs} paired trials**, **{2 * pairs} independent marketplace runs** "
        "(each run negotiates with S1 and S2). Fixed grid = reproducible scenario inputs."
    )
    if st.button(
        "▶ Run experiment grid", type="primary",
        use_container_width=True, key="eval5_run",
        disabled=not pairs or pairs > 36,
    ):
        try:
            result = run_experiment_batch(
                scenarios=tuple(selected),
                quantities=tuple(quantities),
                initial_prices=tuple(offers),
                max_rounds=max_rounds,
            )
            st.session_state["eval5_batch"] = result
        except (ValueError, RuntimeError, PermissionError) as exc:
            st.session_state.pop("eval5_batch", None)
            st.error(f"Experiment failed: {exc}")
    result = st.session_state.get("eval5_batch")
    if result is None:
        st.write("Run the experiment to generate measured comparison tables and downloadable evidence.")
        return

    st.markdown("### 2 · Experiment results")
    config = result["config"]
    st.caption(
        f"Showing last completed run: {config['paired_trials']} paired trials. "
        f"Quantities {config['quantities']}; offers {config['initial_prices']}; "
        f"maximum rounds {config['max_rounds']}."
    )
    metrics = result["summary"]
    total_trials = sum(row["paired_trials"] for row in metrics)
    total_changes = sum(row["supplier_switches"] for row in metrics)
    c1, c2, c3 = st.columns(3)
    c1.metric("Paired trials", total_trials)
    c2.metric("Supplier switches", total_changes)
    c3.metric(
        "Supplier switching rate",
        f"{100 * total_changes / total_trials:.1f}%" if total_trials else "N/A",
    )
    st.caption(
        "Supplier switch = selected seller ID changed, including switching to/from no supplier. "
        "This is not a learning accuracy metric."
    )

    st.markdown("### 3 · Compare outcomes by market condition")
    comparison = []
    for row in metrics:
        comparison.append({
            "Market shock": row["scenario_name"],
            "Trials": row["paired_trials"],
            "Switch rate (%)": row["supplier_switch_rate_pct"],
            "Normal selection (%)": row["normal"]["selection_rate_pct"],
            "After selection (%)": row["changed"]["selection_rate_pct"],
            "Normal mean gross profit (Rs.)": row["normal"]["mean_expected_gross_profit_rs"],
            "After mean gross profit (Rs.)": row["changed"]["mean_expected_gross_profit_rs"],
            "Normal messages/trial": row["normal"]["mean_messages_per_trial"],
            "After messages/trial": row["changed"]["mean_messages_per_trial"],
        })
    st.dataframe(comparison, use_container_width=True, hide_index=True)
    st.bar_chart(
        comparison, x="Market shock", y="Switch rate (%)",
        y_label="Supplier switching rate (%)",
    )
    with st.expander("📏 How we calculate each metric"):
        st.markdown(
            "**Selection rate:** percentage of trials with a feasible selected seller.\n\n"
            "**Supplier switch rate:** percentage of paired comparisons with different supplier IDs.\n\n"
            "**Mean gross profit:** average expected gross profit across all trials, "
            "including zero where no supplier was selected. Delivery/overhead costs excluded.\n\n"
            "**Average messages:** total recorded seller–retailer messages per trial "
            "across both independent negotiations. Market signals not counted.\n\n"
            "**Average rounds:** sum of rounds used by each seller negotiation in a trial. "
            "This is not elapsed time or a measure of parallelism."
        )
    st.markdown("### 4 · Examine individual trials")
    rows = flat_trial_rows(result)
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.markdown("### 5 · Download reproducible experiment evidence")
    export_csv = _to_csv(rows)
    public_export = {
        "config": result["config"],
        "scenario_summary": result["summary"],
        "trial_results": rows,
        "limitations": result["limitations"],
    }
    a, b = st.columns(2)
    a.download_button(
        "⬇ Export trial results (CSV)", data=export_csv,
        file_name="smeconnect_phase05_experiment_trials.csv",
        mime="text/csv", use_container_width=True,
    )
    b.download_button(
        "⬇ Export academic summary (JSON)",
        data=json.dumps(public_export, indent=2),
        file_name="smeconnect_phase05_experiment_summary.json",
        mime="application/json", use_container_width=True,
    )
    st.caption(result["limitations"])
