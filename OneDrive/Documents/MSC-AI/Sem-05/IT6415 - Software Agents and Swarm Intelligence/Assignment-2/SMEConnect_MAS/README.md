# SMEConnect AI — LangGraph MAS assignment starter

A zero-paid-API, local-first **multi-agent marketplace** skeleton inspired organizationally by AEE-Bootcamp Week 10 (not copied): https://github.com/zuucrew/AEE-Bootcamp/tree/main/Week%2010

## Scope
- 2 seller instances, 2 retailer instances, 1 delivery instance, 1 market agent, 1 coordinator.
- Autonomous pricing rules and negotiation messages; modular `StateGraph` for offer evaluation.
- Minimal Streamlit UI and CLI smoke test. Additional behaviours (multi-round protocol, self-organization, failure recovery, experiments) belong to later phases and **are not yet implemented**.

## Setup (Windows PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m smeconnect.main
streamlit run dashboard/app.py
python -m pytest -q
```

If PowerShell blocks activation, run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and use that interpreter directly.

## Architecture
- `smeconnect/agents`: independently configured, goal-driven actor types.
- `smeconnect/graphs`: LangGraph logic (not a single LLM chatbot).
- `smeconnect/communication`: typed messages and an in-memory bus.
- `smeconnect/environment`: synthetic market facts and agent directory.
- `smeconnect/simulation`: runnable first scenario.
- `dashboard`: local demo.
- `tests`: initial automated checks.

## Academic integrity
Synthetic prices and products are illustrative. This is a starter project rather than a completed multi-agent evaluation. Cite the reference bootcamp for the **structuring inspiration**, not as the author of this project.
