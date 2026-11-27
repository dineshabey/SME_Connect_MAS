# SMEConnect AI — Professor Demonstration Script

**Module:** IT6415 – Software Agents and Swarm Intelligence  
**Goal:** Explain *observable MAS behavior* using the running implementation, not merely describe code.  
**Requirement before presenting:** `python -m pytest -q` should pass; capture an actual experiment results export.  
**Demo data:** Entirely synthetic. No actual buyers, deliveries or payments.

## A. Quick setup

1. In the project directory, activate `(smec)`, run `git pull origin main` and `python -m pytest -q`.
2. Generate report results: `python -m smeconnect.simulation.export_evidence --out-dir evaluation_output`.
3. Launch the UI: `python -m streamlit run dashboard/app.py`.
4. Pre-open `http://localhost:8501`; keep terminal with test output available. Set browser zoom so the selected tab and content are readable.
5. If any command fails, do **not** hide the error; fix it before claiming full verification.

## B. Opening explanation — problem and approach

**Say (English):**

> "SMEConnect AI models a small marketplace where sellers, retailers and a delivery provider have different goals. Instead of centralizing every decision, we give agents separate LangGraph decision workflows and let them communicate using typed messages. The system is a local academic simulation with synthetic data."

**සිංහලෙන් මතක තියාගන්න:** Seller ට ලාභය වැදගත්; Retailer ට අඩු මිල සහ ලාභය වැදගත්; Delivery Agent ට capacity වැදගත්. එයාලා වෙන වෙනම තීරණ ගන්නවා.

## C. Marketplace — establish the scenario

**Tab:** `🏬 Marketplace`

**Do:** Point out S1 and S2, the public example asking prices and the advertised stock. Explain that the example listing prices and final negotiated prices are different fields.

**Say:**

> "The catalogue provides public supplier information, but it does not expose private reservation prices. Real MAS autonomy requires participants to keep their own constraints."

**Do not claim:** This is live market stock or actual Sri Lankan SME prices.

## D. Phase 03 — show competition and negotiation

**Tab:** `🏆 Phase 03 · Supplier Competition`

**Inputs:** R1; quantity 200; first offer Rs.150; preferred price Rs.150; 5 rounds.

**Do:** Run competition. Compare S1 and S2 outcomes, then show the message trace.

**Explain:**

- S1 is margin-oriented and can respond with a higher proposal.
- S2 is volume-oriented and can accept eligible bulk offers.
- R1 evaluates *real negotiated outcomes* using budget, maximum unit price and expected gross profit.
- The coordinator discovers sellers, but **does not choose the winner**.

**Expected demo outcome (confirm before saying it happened):** S1 may agree at Rs.155, S2 at Rs.150, R1 selects S2. Expected gross profit on 200 packets at resale assumption Rs.200 is Rs.9,000 versus Rs.10,000 before delivery.

**MAS characteristics:** autonomy, goal orientation, communication, negotiation, competition, heterogeneity.

## E. Phase 04 — demonstrate cooperation, limits and failure

**Tab:** `🚚 Phase 04 · Delivery Coordination`

**Do:** Reset synthetic market; select R1, 200 packets, initial offer Rs.150 and run.

**Expected result to verify:** Selected S2, provisional purchase cost Rs.30,000, delivery fee Rs.1,000, simulated total allocation Rs.31,000, margin after fee Rs.9,000.

**Explain:**

> "Agreement is not the same as a completed order. The Delivery Agent first evaluates its own trip capacity and fee. Then the Retailer Agent independently decides if purchase plus transport is affordable. Only after all checks does the coordinator reserve synthetic resources."

**Do:** Repeat the same request **without resetting** and show `DEMAND_EXHAUSTED` instead of a second reservation. Explain that the sequential ledger prevents double allocation within this browser session.

**MAS characteristics:** cooperation, coordination, bounded resources and failure handling.

**Do not claim:** A courier has been dispatched or money has been deducted from a bank account.

## F. Phase 05.1 — demonstrate changing markets

**Tab:** `📈 Phase 05 · Market Adaptation`

**Inputs:** `S2 Stock Shortage`, R1, quantity 200, initial offer Rs.150, preferred price Rs.150.

**Do:** Run before/after experiment and show S2 stock changing from 300 to 100.

**Expected outcome to verify:** Baseline retailer selects S2; changed market makes S2 unable to supply a 200-packet order, leaving feasible S1.

**Explain:**

> "We did not hard-code a different winner. The same LangGraph seller and retailer policies evaluate different market snapshots. The retailer then selects from the remaining viable offers."

**MAS characteristics:** reactivity and adaptation to changed inputs. **Not** machine-learned policy improvement.

## G. Phase 05.2 — quantitative evaluation

**Tab:** `🧪 Phase 05.2 · Experiments`

**Inputs:** Default three synthetic shocks, quantities 100 and 200, offers Rs.140/150/160, maximum five rounds.

**Do:** Run the experiment grid. Show 18 paired comparisons, per-scenario supplier switching, successful selections, expected gross profit and message counts. Show the report-ready CSV/JSON export.

**Say:**

> "We report what the simulations measured, including cases where the selected seller does not change. The experiment uses a deterministic parameter grid, not a sample of real companies or a statistically generalizable model."

**Important:** Do not quote any numerical switching rate or experimental mean until it appears in the real run output. Fixed inputs make this an internally repeatable **simulation**, not a real-market validation.

## H. Conclude the demonstration

**Say:**

> "The system demonstrates multiple autonomous decision owners connected by a validated message bus. We tested negotiation, supplier competition, delivery coordination and rule-based responses to market changes. We can measure these behaviors, but the prototype deliberately stops short of live commerce, machine learning and production concurrency."

**Recommended final screenshot evidence:** (i) seller marketplace, (ii) S1/S2 negotiation comparison, (iii) resource reservation and failure, (iv) market before/after comparison, (v) experiment metrics.

---

## I. Likely professor questions with defensible answers

**Q1: Why is this a MAS rather than one algorithm?**  
Because seller/retailer/delivery each own separate goals, constraints and decision graphs; structured messages connect their decisions. The scheduler is centralized in memory, but price decisions are not.

**Q2: Is an LLM involved?**  
No. LangGraph runs explicit deterministic StateGraphs. This is deliberate for reproducibility and explainability.

**Q3: What makes sellers different?**  
S1 protects margin; S2 uses a synthetic bulk-volume rule. Identical offers may produce different decisions.

**Q4: Does the coordinator decide who wins?**  
No. It provides discovery and reservation orchestration. The retailer's supplier-selection StateGraph compares public agreements and applies its own utility.

**Q5: What does 'ACCEPT' mean?**  
Agreement on a simulated unit price. The separate delivery phase must still check capacity, budget, stock and demand.

**Q6: Why do the market experiments show adaptation?**  
Agent decisions are recomputed on changed stock/pricing/demand state; no agent policy was retrained. This demonstrates *rule-based reactivity*, not online learning.

**Q7: What evidence is collected?**  
Typed messages, negotiation event timelines, supplier decisions, paired trials, message counts, switching rates and expected gross profit. The exported CSV/JSON identifies the synthetic scenario assumptions.

**Q8: Is this a distributed production system?**  
No. All agent processes are executed sequentially in one local Python simulation. A distributed broker, persistence and concurrency controls would be future work.

**Q9: How do you protect private seller prices?**  
Public listings and retailer selection use published asking prices and communicated negotiated outcomes, not sellers' internal minimum/target prices. Production authentication is not implemented.

**Q10: Did agents organize themselves without instructions?**  
No evidence supports that claim. Supplier switching follows explicit policies and changed constraints; emergent self-organization has not been demonstrated.

## J. Final presentation checklist

- [ ] Correct code revision and no new syntax errors
- [ ] Verified pytest output preserved
- [ ] CSV, JSON and measured-results Markdown generated locally
- [ ] Both normal and failure cases visible in the UI
- [ ] No confusion between listing price, negotiated price and final reservation cost
- [ ] No claim of real data, learning, parallel agents, delivery or payment
- [ ] All screenshots legible at presentation zoom
