# SMEConnect AI

**A LangGraph-Based Multi-Agent System for Intelligent Sales and Market Coordination of Small and Medium Enterprises**

An academic prototype for **IT6415 – Software Agents and Swarm Intelligence**. The project models a small business marketplace where autonomous software agents represent sellers, retailers, delivery services and market participants.

## Project objective

Demonstrate how agents with distinct goals, constraints and decision-making strategies can communicate, negotiate and coordinate business transactions in a changing marketplace.

## Agent roles

| Agent | Instances | Objective |
| --- | ---: | --- |
| Seller | 2 | Evaluate offers while pursuing profit or sales-volume goals |
| Retailer | 2 | Discover suppliers and negotiate purchasing conditions |
| Delivery | 1 | Evaluate transportation cost and capacity |
| Market | 1 | Observe demand and generate market signals |
| Coordinator | 1 | Support agent registration, discovery and communication |

## Technology stack

- **Python** – agent logic and simulation
- **LangGraph** – agent state and decision workflows
- **Pydantic** – structured inter-agent messages
- **Streamlit** – local demonstration interface
- **pytest** – automated testing

The core prototype is designed to run locally without requiring a paid LLM API or cloud service.

## Project structure

```text
SMEConnect_MAS/
├── smeconnect/
│   ├── agents/           # Agent roles and decision strategies
│   ├── graphs/           # LangGraph workflows and state
│   ├── communication/    # Message schemas and message bus
│   ├── environment/      # Marketplace facts and shared vocabulary
│   ├── simulation/       # Simulation entry points
│   └── main.py
├── dashboard/
│   └── app.py            # Streamlit demonstration
├── docs/                 # Design and development notes
├── tests/                # Automated tests
├── requirements.txt
└── README.md
```

## Getting started

Requirements: Python 3.10+.

From the project directory, run the following commands in Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m smeconnect.main
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Run the automated tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Multi-agent features

The target system demonstrates:

- **Autonomy:** each agent evaluates decisions using its own goals and constraints.
- **Communication:** agents exchange structured messages.
- **Negotiation:** buyers and sellers exchange proposals and counter-offers.
- **Coordination:** agents arrange commercial and delivery activities.
- **Adaptation:** agents respond to changes in demand, stock or resource availability.
- **Self-organization:** agents may establish alternative business relationships without centralized commercial decisions.

## Implementation status

This repository contains an **academic synthetic simulation prototype**, not a production marketplace. Implemented code includes separate LangGraph seller/retailer workflows, bounded negotiation, multiple-seller competition, retailer supplier selection, public synthetic catalogue, simulated resource/delivery reservation, controlled market scenarios, and a reproducible evaluation runner. Real-data validation, concurrency-safe persistence, actual payments/shipments, policy learning and evidence of emergent self-organization **remain future work**. Numerical experimental findings must be verified by executing the code locally.

The market data and business scenarios are **synthetic examples**, not real commercial transactions.

## Development approach

1. Implement and test independent seller and retailer decisions.
2. Complete a bounded proposal/counter-offer negotiation protocol.
3. Integrate delivery and coordination behaviours.
4. Add market-change scenarios and a useful dashboard.
5. Run repeatable experiments and document measured results.

## License

No license has been specified for this project.

## Phase 03 — Supplier competition

The **Phase 03 · Supplier Competition** tab demonstrates one retailer negotiating with two sellers independently. Seller S1 pursues margin; Seller S2 uses a simulated volume-based bulk-offer strategy. Each seller executes its own LangGraph decision process. The retailer compares only recorded public agreements, rejects infeasible options, and selects the offer with the greatest expected gross profit using a separate StateGraph.

**Run:** `python -m streamlit run dashboard/app.py`, then open the first tab. **Test:** `python -m pytest -q`.

All business data are synthetic. Negotiations run sequentially as separate conversations, not as a concurrent distributed marketplace. A supplier choice is a provisional price agreement; it does not reserve stock, charge money or schedule delivery.

### Phase 03.1 — Seller Marketplace

Open the first **Marketplace** tab to browse synthetic seller listings (S1 Rs.175; S2 Rs.165 per 100g packet), search by seller/product, inspect advertised stock, select sellers, and start real in-memory agent negotiations. The results distinguish the public asking price from the separately negotiated provisional price. Private seller minimum and target prices are not exposed in public listings.

`python -m py_compile dashboard/app.py dashboard/marketplace_viz.py smeconnect/environment/catalogue.py`
`python -m pytest -q`
`python -m streamlit run dashboard/app.py`

The catalogue supports only `roasted_peanuts_100g` in this phase; no real transactions, product inventory reservations or delivery scheduling take place.

### Phase 04 — Simulated Delivery Coordination

New tab **🚚 Phase 04 · Delivery Coordination**: select Retailer R1/R2, negotiate suppliers, let Delivery D1 quote trip capacity/fee, independently validate retailer finances and reserve session-scoped synthetic stock/budget/demand/capacity. You can run multiple attempts to see how reservations reduce available resources, or reset the session ledger. Failed coordination does not mutate any resources. Phase 04 is a simulated booking, **not** real delivery, payment or shipped order.

For the architecture, limitations and commands see [architecture notes](docs/architecture.md).

### Phase 04 dashboard: simplified teaching view

The Delivery Coordination tab now displays the latest attempt's outcome first, then a four-checkpoint agent journey, retailer supplier selection, transparent purchase + delivery breakdown, and **before/after session resources**. Technical message records and raw reservation IDs are available under expandable evidence sections. This is a presentation-only change: it does not modify LangGraph decisions, message passing, or reservation logic.

A fresh run is needed after changing input settings; the result panel describes the most recent completed attempt. Use **Reset market** to restore synthetic session resources.

### Phase 05.1 – Market Changes and Adaptation

Use the **📈 Phase 05 · Market Adaptation** tab to compare real bounded negotiations under independent normal and synthetic changed-market snapshots (stock shortage, private pricing shock, demand surge). Market Agent M1 records a typed public market notification; existing LangGraph decisions are rerun with scenario-specific agent constraints. The experiment shows actual before/after supplier choices, prices and message traces, without completing orders. See [architecture](docs/architecture.md) for limitations.

### Phase 05.2 — Experiment Evaluation and Evidence Export

Open **🧪 Phase 05.2 · Experiments** to run reproducible, bounded paired comparisons over quantities, initial offers and synthetic market shocks. The new tool measures actual supplier selection/switching rates, expected gross profit and communication volume through existing LangGraph negotiations, then exports a public CSV trial table or JSON evaluation summary. The default deterministic grid contains 18 pairs (36 independent marketplace runs). It does not involve random sampling, live SME data, payment or order fulfilment; see [architecture](docs/architecture.md) for formulas and limitations.

### Phase 05.3 — MSc Assignment Report and Demonstration Pack

- **Academic report draft:** [docs/FINAL_ASSIGNMENT_REPORT.md](docs/FINAL_ASSIGNMENT_REPORT.md) (architecture, problem, methodology, limitations and clearly marked results placeholders).
- **Professor walkthrough and Q&A:** [docs/FINAL_DEMO_SCRIPT.md](docs/FINAL_DEMO_SCRIPT.md).
- **Updated agent evidence:** [docs/agent_characteristics.md](docs/agent_characteristics.md).
- **Executable measured-results export:** `python -m smeconnect.simulation.export_evidence --out-dir evaluation_output`.

Before submitting, run the entire test suite and evidence exporter in your own environment. The exporter creates `evaluation_output/FINAL_REPORT_WITH_RESULTS.md` by inserting actual computed results into a copy of the report template, alongside `RESULTS_FOR_REPORT.md`, `phase05_trials.csv`, and `phase05_summary.json`. Review the generated report and confirm the test output, provenance and university formatting before submitting. Generated CSV/JSON/Markdown are *synthetic simulation evidence*, not externally verified market data. The export includes the Git revision and Python/package version metadata when available.

```powershell
git pull origin main
python -m py_compile smeconnect/simulation/export_evidence.py
python -m pytest -q
python -m smeconnect.simulation.export_evidence --out-dir evaluation_output
python -m streamlit run dashboard/app.py
```

The academic report and demonstration script are drafts, **not** automatically verified final submissions. Follow any university instructions for formatting, referencing and authorship disclosures.

### Automated Phase 05.3 verification (GitHub Actions)

A repository-level GitHub Actions workflow, [`phase05-verification.yml`](https://github.com/dineshabey/SME_Connect_MAS/blob/main/.github/workflows/phase05-verification.yml), is configured for pushes to `main` affecting this project and supports manual `workflow_dispatch`. It creates a clean Python 3.11 environment, installs `requirements.txt`, compiles Python files, runs **all pytest tests**, executes the deterministic default evaluation, and checks that the generated report includes results and has no placeholders.

On a **successful** workflow run, open the repository **Actions** page → **SMEConnect MSc Phase 05.3 verification** → latest run → download the **`smeconnect-phase05-evidence`** artifact. It contains the CSV, JSON, report-ready tables and `FINAL_REPORT_WITH_RESULTS.md`. A workflow committed to GitHub is *not* evidence of passing tests: only the actual completed run log and uploaded artifact verify completion.

If Actions is disabled or no run appears, execute the same tests and exporter locally using the commands above. Do not report CI as passed before inspecting its result.

### Phase 06.1 — Professor Demo overview and clearer navigation

The first dashboard tab, **🎓 Professor Demo**, now provides a native Streamlit introduction to seven agents, a conceptual network, and an ordered demonstration route through Marketplace, Phase 03 competition, Phase 04 delivery, Phase 05.1 market adaptation, and Phase 05.2 experiments. The **one-click stock-shortage demonstration** invokes the same `run_market_experiment()` controller as Phase 05.1 and displays *actual* before/after supplier decisions and message traces. The overview does not make business decisions or fake messages.

To review it after the latest pull:

```powershell
git pull origin main
python -m py_compile dashboard/app.py dashboard/overview_viz.py smeconnect/simulation/export_evidence.py
python -m pytest -q
python -m smeconnect.simulation.export_evidence --out-dir evaluation_output
python -m streamlit run dashboard/app.py
```

**Phase 06 remains incremental:** the new overview does not yet replace the existing negotiation, delivery, market and experiment tab interfaces. Review presentation legibility and the generated report before preparing final screenshots.
