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

### Phase 06.2 — Modern research dashboard (navigation and overview)

The Streamlit presentation was redesigned after reviewing patterns documented by LangSmith Studio (trace-first debugging), CrewAI tracing (agent activity and execution insights), and the official Streamlit guidance for responsive dashboards, navigation and native theming.

**What changed**

- **Workspace sidebar** replaces the long row of nine tabs. All original labs remain available: Overview, Marketplace, Competition, Delivery, Market Adaptation, Experiment Analytics, Guided Negotiation, Seller Decision and Retailer Decision.
- A shared **teal/dark visual system** in `dashboard/ui_design.py` and `.streamlit/config.toml`, with accessible text size, large native metrics, readable controls and responsive widths.
- A modern `dashboard/overview_viz.py` home page with genuine registry metrics, a clearly identified conceptual topology, large agent role cards, working shortcuts and a one-click before/after stock-shortage demonstration. Live outcomes and message timelines are generated by existing `run_market_experiment()`; none are fabricated.
- The negotiation, order reservation and experiment backends were **not modified** by the UI redesign. Navigation smoke tests were added in `tests/test_dashboard_navigation.py`.

**Run and verify locally (Windows, from this project's folder)**:

```powershell
git pull origin main
python -m py_compile dashboard/app.py dashboard/overview_viz.py dashboard/ui_design.py
python -m pytest -q
python -m streamlit run dashboard/app.py
```

**Browser checks:** Open the sidebar, switch among all nine workspaces, try the three Quick Start buttons, run the live S2 stock-shortage example, then check that Phase 04 session reservations and Phase 05 export still work. On narrow screens, use Streamlit's sidebar toggle. The UI is designed for an offline synthetic academic simulation, not an operational commerce portal.

**External design references:**
- [LangSmith Studio, graph mode and chat mode](https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/)
- [CrewAI tracing in AMP](https://github.com/crewAIInc/crewAI/blob/main/docs/edge/en/observability/tracing.mdx)
- [Streamlit dashboard design](https://docs.streamlit.io/develop/concepts/design/dashboards)
- [Streamlit multipage navigation](https://docs.streamlit.io/develop/api-reference/navigation/st.navigation)
- [Streamlit theme configuration](https://docs.streamlit.io/develop/api-reference/configuration/config.toml)

### Viva Presentation — English-only guided MAS demonstration

Use **🎓 Viva Presentation** under the sidebar's **PRESENTATION** section. The new `dashboard/viva_mode.py` provides a ten-step, presenter-controlled walkthrough:

1. Full conceptual architecture and LangGraph vs NetLogo/SPADE justification.
2. Public S1/S2 seller listing prices, stock, and different goals.
3. R1 budget, demand, strategy, and buying limits.
4. Coordinator-assisted seller discovery and public catalogue.
5. Actual two-seller message replay (previous/next messages) from `run_supplier_competition()`.
6. Retailer-owned supplier choice from genuine negotiation agreements.
7. D1 and R1 decisions from `run_delivery_coordination()`.
8. In-memory reservation, remaining resources and duplicate-allocation rejection.
9. Controlled stock-shortage comparison using `run_market_experiment()`.
10. Reproducible evaluation via `run_experiment_batch()` and an MAS evidence table.

The presenter uses **Previous step / Next step** to progress. Real calculations occur only when the relevant **Run** button is clicked. Slides 05–08 share the same competition and dedicated session ledger, while other workspaces' reservations remain separate. Seller private pricing constraints are not displayed as retailer-visible data. All wording inside this new page is English. It is a synthetic, sequential teaching simulation, not a production marketplace or distributed XMPP agent platform.

Run:

```powershell
git pull origin main
python -m py_compile dashboard/viva_mode.py dashboard/app.py dashboard/ui_design.py
python -m pytest -q
python -m streamlit run dashboard/app.py
```

During the viva, run the negotiation in step 05 before the selection/delivery stages; use the controls in steps 07 and 08 to demonstrate a successful reservation followed by a rejected duplicate attempt. Browser and complete pytest verification still need to be completed locally.

### Interactive Workflow Simulator — visual end-to-end MAS replay

Open **⚡ Workflow Simulator** under **PRESENTATION** in the Streamlit sidebar.

1. Choose Retailer **R1 or R2**, one or both Sellers **S1/S2**, a requested quantity within that retailer's demand, opening unit price, target price, negotiation rounds, assumed resale price and playback speed.
2. Review the synthetic retailer and public seller cards (only public seller asking prices and stock are shown).
3. Click **Run complete MAS workflow** once. The actual seller/retailer LangGraph negotiations, retailer-owned supplier choice and D1/C1 synthetic delivery/resource coordination execute **once in a fresh, isolated session ledger**, then the captured trace **automatically animates from discovery to the final outcome**. The presenter's Previous/Next/Replay controls allow revisiting the same recorded events.
4. Watch the generated trace, including supplier discovery, each genuine bilateral negotiation message (with the existing animated neon visual), supplier selection, delivery/coordination events, and the final status. Use **Previous**, **Next event**, **Play to final outcome** or **Replay from start**. Replaying never re-executes transactions.
5. Inspect the final decision, negotiated price, delivery quote, reservation outcome, pre/post simulated resource values and actual typed messages in Technical Evidence.

**Correctness constraints:** The discovery and supplier-choice visuals are clearly marked as summaries of computed results, *not* invented wire messages. THINK logs are described as rule evaluation, not hidden LLM reasoning. No live payments, dispatch, inventory changes, concurrent multi-process execution or external writes occur. Changing configuration after a run triggers an on-screen rerun warning.

```powershell
git pull origin main
python -m py_compile dashboard/workflow_simulator.py dashboard/app.py dashboard/ui_design.py
python -m pytest -q
python -m streamlit run dashboard/app.py
```

The automated test checks structural routing, sequential trace composition and HTML escaping. Visual and full runtime verification still require launching Streamlit locally.

### Animated Multi-Agent Sequence Replay (new Viva workspace)

Open **🔀 Sequence Replay** in the Streamlit **PRESENTATION** sidebar group. This is an independent, English-only workflow diagram page alongside the existing **⚡ Workflow Simulator**.

- Configure retailer R1/R2, sellers S1/S2, quantity, opening and target offers, round limit, resale price and speed.
- Click **Run and animate agent sequence**. The existing `_run_session()` controller computes one isolated real LangGraph/Pydantic synthetic scenario, including supplier selection, delivery and simulated reservation.
- A self-contained local SVG sequence viewer displays lifelines for the retailer, selected sellers, C1 and D1. Validated message events become directional arrows. Discovery, selection, THINK and reservation decisions are distinct labeled cards and are never presented as transmitted messages.
- The viewer auto-plays the recorded events and supports **Pause/Resume**, **Previous**, **Next**, **Restart** and **Show final result**. It displays event explanations, quantity/price where recorded, and a final summary with seller, price, delivery quote, reservation total and status. The full validated messages and supplier evaluations remain available in an expandable evidence panel.
- Playback runs entirely inside a locally rendered iframe with no web/CDN dependencies. Controls change only the displayed event index, **never the Python simulation or reservation ledger again**. A new Run explicitly generates a fresh isolated synthetic run. No real orders, payment or delivery occur.

```powershell
git pull origin main
python -m py_compile dashboard/sequence_replay.py dashboard/workflow_simulator.py dashboard/app.py
python -m pytest -q
python -m streamlit run dashboard/app.py
```

Verify in browser: select R1 + S1/S2, 200 packets and Rs.150 initial price; Run; watch arrows/decision cards appear; pause, step forward/backward, show the final simulated result; inspect the authentic message evidence. Repeat with a rejected or infeasible scenario to demonstrate failure handling. Browser-level visual validation and full pytest execution are still required locally.
