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

This repository currently contains a **starter prototype**, not a completed or experimentally validated multi-agent marketplace. The seller and retailer have separate LangGraph decision workflows, a bounded two-way negotiation protocol is implemented, and Phase 03 adds independent seller discovery, competing negotiations and a retailer-owned supplier-selection StateGraph. Integrated delivery coordination, atomic inventory/budget reservations, dynamic-market experiments and evaluated emergent behaviours remain development goals.

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
