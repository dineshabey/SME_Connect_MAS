# SMEConnect AI — Architecture and Execution Status

## Phase 02: Two-way autonomous agent negotiation

```mermaid
sequenceDiagram
  participant R as Retailer Agent (LangGraph)
  participant B as In-memory Message Bus
  participant S as Seller Agent (LangGraph)
  R->>B: PROPOSE initial price
  B->>S: Deliver typed offer
  S->>S: Evaluate stock, minimum and target
  S->>B: PROPOSE seller counter / ACCEPT / REJECT
  B->>R: Deliver seller decision
  R->>R: Evaluate budget, demand and profit
  R->>B: PROPOSE retailer counter / ACCEPT / REJECT
  Note over R,S: Repeat with bounded rounds or terminate
```

## Module boundaries

- `smeconnect/agents/` defines distinct agent instances and private constraints.
- `smeconnect/graphs/seller_graph.py` owns the seller's LangGraph pricing decision.
- `smeconnect/graphs/retailer_graph.py` owns retailer financial analysis and bounded concessions.
- `smeconnect/communication/message_schema.py` validates typed FIPA-inspired messages.
- `smeconnect/communication/message_bus.py` transports the messages and records the history.
- `smeconnect/simulation/negotiation.py` runs a bounded, event-driven interaction and records its actual messages.
- `dashboard/app.py` displays the genuine trace as an animated negotiation; it does not decide prices.

## What works versus what is still planned

**Implemented in code:** Separate seller/retailer StateGraphs; explicit proposals and responses; agent-specific limits; finite maximum rounds; recorded messages; outcome status `AGREED`, `REJECTED`, or `MAX_ROUNDS`; Streamlit animation driven by those recorded events.

**Still planned / not verified:** Live external buyer discovery; delivery coordination; atomic inventory reservations; actual order/payment settlement; durable event persistence; full message origin authentication for arbitrary callers; comprehensive experiments and self-organization measures.

**Important:** `AGREED` means a **provisional agreement on unit price**, not a completed commercial transaction. The demonstration uses synthetic market data. The architecture documents intended security boundaries in [TRUST_BOUNDARIES.md](../TRUST_BOUNDARIES.md) and STRIDE risks in [STRIDE_THREAT_MODEL.md](STRIDE_THREAT_MODEL.md).

## Running locally

```powershell
python -m pytest -q
python -m streamlit run dashboard/app.py
```

The dashboard provides standalone seller and retailer tests plus an animated two-agent negotiation example. The animation replays recorded messages, and the demonstration remains offline and free of paid APIs.

## Phase 03: Multi-seller competition and retailer-owned supplier selection

```mermaid
sequenceDiagram
  participant C as Coordinator (discovery)
  participant R as Retailer R1 (LangGraph)
  participant S1 as Seller S1 (firm)
  participant S2 as Seller S2 (volume)
  R->>C: Discover registered sellers
  C-->>R: S1, S2 IDs only
  R->>S1: PROPOSE initial price
  S1-->>R: Counter / Accept / Reject
  R->>S2: PROPOSE initial price
  S2-->>R: Counter / Accept / Reject
  Note over R,S2: Two separate, bounded negotiation conversations
  R->>R: Evaluate public agreements in supplier selection StateGraph
  R->>R: Maximize expected gross profit under budget and max price
  Note over R: Select one provisional supplier or none
```

The coordinator only lists discovered seller identifiers: it does not inspect seller minimum prices or decide the winner. `run_supplier_competition()` uses each seller's existing LangGraph negotiation separately, then supplies **public outcomes** to `build_supplier_selection_graph()`.

Seller S1 retains its margin-focused pricing policy. Seller S2 has a **documented simulated bulk-volume policy**: for orders of 100 or more packets, it accepts offers at least Rs.10 above its private minimum, if stock permits. This gives the experiment two distinct autonomous seller strategies rather than hard-coding a winning supplier.

The retailer compares feasible agreements using expected gross profit `(expected retail price - negotiated purchase price) × requested quantity`, subject to its budget and maximum price. Ties are resolved by fewer negotiation rounds and seller ID.

The Streamlit **Phase 03 · Supplier Competition** tab displays the three-agent network, compares actual outcome records, shows the retailer's decision reason, and replays the recorded conversation with each seller using the existing neon visualization.

**Important limitations:** Discovery uses in-memory registered agents, not real buyer discovery or an external API. Negotiations run as separate bounded simulations rather than simultaneous distributed processes; there is no shared stock reservation. Supplier selection is provisional, no real business transaction occurs, and self-organization has not yet been experimentally demonstrated.
