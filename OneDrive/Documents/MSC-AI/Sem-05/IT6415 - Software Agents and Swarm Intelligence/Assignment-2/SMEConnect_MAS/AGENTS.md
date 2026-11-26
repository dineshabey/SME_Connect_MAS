# AGENTS.md — SMEConnect AI Coding Agent Instructions

> Applies to this directory and all descendants. Read [TRUST_BOUNDARIES.md](TRUST_BOUNDARIES.md) before changing code. For human contributors and AI-assisted/vibe-coding workflows.

## 1. Mission and constraints

Build an explainable, locally executable **LangGraph-based multi-agent marketplace** for the MSc IT6415 Software Agents and Swarm Intelligence assignment.

**Learning outcomes:** independent agent autonomy, communication, coordination and negotiation; then competition, cooperation, adaptability and measurable self-organization.

**Hard constraints:** small scope (~16 hours of implementation work), no mandatory paid LLM/cloud APIs, synthetic demonstration data by default, reproducible experiments. Do not claim the application makes genuine sales or finds genuine buyers.

The project is a **simulation / academic prototype**, not an autonomous commerce service.

## 2. Repository map (relative to this file)

| Path | Responsibility |
| --- | --- |
| `smeconnect/agents/` | Roles, individual goals and constraints |
| `smeconnect/graphs/` | LangGraph StateGraph nodes, typed state and decisions |
| `smeconnect/communication/` | Structured messages and in-memory bus |
| `smeconnect/environment/` | Synthetic market data and shared vocabulary |
| `smeconnect/simulation/` | Simulation execution and scenarios |
| `dashboard/app.py` | Streamlit inspection UI, not business decision logic |
| `tests/` | Deterministic unit/integration tests |
| `docs/` | Architecture and academic documentation |

Existing design: seller and retailer each have a decision workflow; the message bus supports send/receive. **A full bidirectional negotiation protocol, delivery workflow, end-to-end transactions and experimental validation are not implemented yet.** Check the actual files before relying on this status.

## 3. Rules for human developers and coding assistants

1. **Inspect before editing.** Read the affected source, tests, README and this file; do not invent APIs or silently replace working logic.
2. **Change only what the task needs.** Prefer small, reviewable edits. Preserve existing features and unrelated files.
3. **Explain the business reason.** In summaries/PRs, state: (a) why the change matters for MAS, (b) what changed, (c) how it was verified.
4. **Preserve independent decisions.** Each agent owns its private state, goals, prices and budgets. The coordinator may route/discover, but **must not decide market prices on behalf of agents**.
5. **Messages are contracts.** Validate every inter-agent message using Pydantic before delivery. Include sender, receiver, conversation ID, performative, product, quantity and unit price; expand only with tests and documentation.
6. **No privileged state peeking.** A retailer must not directly read a seller's private minimum price. Agents learn via explicit authorized communication.
7. **Bound work and negotiations.** Cap rounds, retries, queue sizes and simulation events; use explicit termination conditions. Avoid uncontrolled loops, unbounded recursion and runaway LLM/API calls.
8. **Keep decisions explainable.** Start with deterministic utility/rule-based policies. Record reasons and decision inputs without leaking private constraints to other agents.
9. **Separate concerns.** LangGraph handles each agent's decision workflow; the message bus transports communications; the environment applies validated actions; Streamlit renders real outcomes.
10. **Honest status.** Clearly distinguish implemented code, planned features, simulated values, expected outcomes and measured outcomes. Never fake negotiation logs, benchmarks, buyer interest or transaction success.
11. **No unrelated dependencies or services.** Prefer the existing Python, LangGraph, Pydantic, Streamlit and pytest stack. New APIs, packages or infrastructure require a concrete justification and approval.
12. **Respect trust boundaries.** Follow `TRUST_BOUNDARIES.md`, including untrusted inputs, credentials, side effects and human approvals.

## 4. Agentic architecture checklist

Before introducing an agent or new interaction, answer:

- **Role / goal:** What is this agent trying to optimize?
- **Observations:** What information may it legitimately observe?
- **Private state:** What budget, stock, constraints, strategy or memory belongs only to it?
- **Decision policy:** Which utility/rules and trade-offs decide its next action?
- **Actions:** Which typed messages or simulated environment changes may it request?
- **Negotiation protocol:** What are the states, proposal/counter/accept/reject transitions and termination limits?
- **Coordination:** How are inventory, payment assumptions and delivery reservations checked before simulated confirmation?
- **Failure handling:** What if a peer declines, a delivery resource fails or a message is malformed?
- **Evidence:** Which tests and observable events prove the behaviour?

A set of functions labelled "agents" is insufficient. Demonstrate actual independent state, choices and interactions.

## 5. Approved coding workflow

1. **Read:** target files, adjacent interfaces, applicable tests and `TRUST_BOUNDARIES.md`.
2. **Plan:** define the smallest observable behaviour and expected tests.
3. **Implement:** explicit types, clear names, small functions, no hidden shared state or magical constants.
4. **Test:** add focused tests (normal, rejected, boundary and failure cases).
5. **Review:** inspect the diff for accidental data exposure, broken contracts, unsupported assertions and scope creep.
6. **Report:** list changed paths, test commands/results, limitations and the next safe step.
7. **Commit/push:** only when requested or otherwise explicitly authorized; do not rewrite history, force-push or delete unrelated files.

### Local commands (PowerShell, run in this directory)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m smeconnect.main
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

If the environment is already active, substitute `python -m ...`. Do not claim tests passed unless executed and their outputs observed.

## 6. Minimal quality gates

- Tests cover acceptance, counter-offer, rejection, invalid quantities, budget/stock bounds and distinct agent behaviours.
- Protocol changes include compatible changes to the schema, producers, consumers, tests and documentation.
- Every simulated negotiation has a unique conversation ID, traceable messages, limited rounds and a terminal state.
- Any simulated order must validate **seller stock, retailer budget and delivery capacity**; avoid double allocation.
- Experiments use explicit seeds/parameters, baseline comparisons and real measured logs.
- No real payment, unsolicited marketing, browser scraping or external writes without documented human authorization.

## 7. Vibe-coding collaboration contract

**For AI assistants:** You may propose implementations and write code, but clearly surface assumptions, uncertainty, risky migrations and unverified claims. Treat requests such as "make it agentic" as a request for explainable local decision-making and observable peer interaction—not a reason to add LLMs or uncontrolled external actions.

**For human reviewers:** Verify that each change serves an agent capability, read the diff, run tests, inspect the dashboard and reject simulated successes presented as real outcomes.

**Definition of done:** behaviour works locally, relevant tests pass, trust boundaries hold, the dashboard accurately reflects actual outputs and the report explains the resulting MAS characteristic.
