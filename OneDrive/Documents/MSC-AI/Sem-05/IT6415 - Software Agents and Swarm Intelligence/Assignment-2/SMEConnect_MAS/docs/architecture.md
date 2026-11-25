# Architecture reference

```mermaid
flowchart LR
  UI[Streamlit dashboard] --> SIM[Simulation Engine]
  SIM --> BUS[In-memory Message Bus]
  BUS --> SELL[Seller Agent StateGraph]
  BUS -.later.-> RET[Retailer Agent StateGraph]
  BUS -.later.-> DEL[Delivery Agent StateGraph]
  SIM --> ENV[Market Environment]
```

## Design notes
- The coordinator facilitates message routing, not commercial decisions.
- Agent private limits should be isolated in agent-specific state.
- Version 0.1 only has seller offer evaluation. Future versions add agent-to-agent negotiation rounds and delivery.
- Adapted organization principles from AEE-Bootcamp Week 10 (agents/state/orchestration separation); not copied code.
