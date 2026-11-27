# Implemented agent characteristics and their evidence

**Scope:** Seven synthetic agents. These are deterministic Python decision-policy agents executed within a local simulation; they do not run as independent network services. The Coordinator performs discovery, while the central simulation driver orchestrates turns and resource checks.

| Agent | Own goal / constraints | Implemented behavior | Observable MAS evidence |
|---|---|---|---|
| S1 (Seller) | Preserve margin; private minimum/target and stock | Evaluate offer and counter, accept or reject using Seller LangGraph | Autonomous bargaining and stock limits |
| S2 (Seller) | Increase volume; private minimum/target and stock | Bulk-order pricing policy with independent accept/reject/counter | Heterogeneous strategy, supplier competition |
| R1 (Retailer) | Reduce purchasing cost; budget, demand, maximum buying price | Negotiate; evaluate public outcomes; approve total after delivery | Goal-oriented negotiation, supplier-selection StateGraph, financial approval |
| R2 (Retailer) | Fulfill synthetic demand within its own limits | Same retailer decision architecture, different synthetic constraints | Agent-specific constraints, alternative retailer scenario |
| D1 (Delivery) | Respect synthetic trip capacity and cost | Evaluate delivery CFP and propose one fixed-trip fee using LangGraph | Cooperation, independent resource assessment |
| M1 (Market) | Monitor controlled scenario change | Emit limited public market signal through typed INFORM message | Reactive signaling, observable communication |
| C1 (Coordinator) | Facilitate discovery and resource workflow | Discover seller IDs; simulation controller requests all-or-none ledger validation | Discovery, coordination without choosing prices |

## Evidence locations

- **Autonomy:** `smeconnect/graphs/seller_graph.py`, `retailer_graph.py`
- **Social communication:** `smeconnect/communication/message_schema.py` and `message_bus.py`
- **Competition:** `smeconnect/simulation/supplier_selection.py`, `graphs/supplier_selection_graph.py`
- **Delivery cooperation:** `smeconnect/graphs/delivery_graph.py`, `retailer_order_graph.py`, `simulation/fulfillment.py`
- **Resource constraints:** `smeconnect/simulation/reservation_ledger.py`
- **Rule-based reactivity:** `smeconnect/environment/market_state.py`, `simulation/market_experiment.py`
- **Experimental evidence:** `smeconnect/simulation/experiment_evaluation.py` and `export_evidence.py`

## Important non-claims

- No LLM, paid model, learned policy, training or online learning is used.
- No real SME buyer/seller discovery or external market-feed integration.
- No proof of emergent self-organization or statistical performance in real markets.
- Negotiations and ledger updates run sequentially in one process; production distributed coordination and concurrent transaction safety are not implemented.
- A price agreement or `RESERVED_SIMULATED` is not a completed commercial transaction.
