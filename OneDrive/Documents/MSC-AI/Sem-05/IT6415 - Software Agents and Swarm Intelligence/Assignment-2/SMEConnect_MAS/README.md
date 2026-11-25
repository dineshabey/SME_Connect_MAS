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

This repository currently contains a **starter prototype**, not a completed or experimentally validated multi-agent marketplace. The initial seller decision workflow, message structures and project scaffolding are the starting point. Full multi-round negotiation, integrated delivery coordination, dynamic-market experiments and evaluated emergent behaviours remain development goals.

The market data and business scenarios are **synthetic examples**, not real commercial transactions.

## Development approach

1. Implement and test independent seller and retailer decisions.
2. Complete a bounded proposal/counter-offer negotiation protocol.
3. Integrate delivery and coordination behaviours.
4. Add market-change scenarios and a useful dashboard.
5. Run repeatable experiments and document measured results.

## License

No license has been specified for this project.
