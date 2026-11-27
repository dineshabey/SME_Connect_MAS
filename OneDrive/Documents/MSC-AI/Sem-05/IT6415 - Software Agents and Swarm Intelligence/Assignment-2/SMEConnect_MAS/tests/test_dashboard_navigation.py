"""Phase 06 dashboard navigation and structural smoke checks.

These checks do not claim browser-level visual verification.
"""
import ast
from pathlib import Path

from dashboard.ui_design import PAGE_METADATA, PAGES, navigate_to


PROJECT = Path(__file__).resolve().parents[1]


def test_all_workspaces_have_distinct_navigation_names_and_descriptions():
    assert len(PAGES) == 11
    assert len(set(PAGES)) == len(PAGES)
    assert set(PAGE_METADATA) == set(PAGES)
    assert all(len(title) > 5 and len(description) > 25
               for title, description in PAGE_METADATA.values())


def test_all_pages_are_explicitly_routed_from_the_entrypoint():
    app = (PROJECT / "dashboard" / "app.py").read_text(encoding="utf-8")
    ast.parse(app)
    assert "show_sidebar()" in app
    assert "st.tabs(" not in app
    for index in range(len(PAGES)):
        assert f"if selected_page == PAGES[{index}]:" in app


def test_overview_and_shared_theme_have_valid_syntax():
    for filename in ("dashboard/ui_design.py", "dashboard/overview_viz.py"):
        ast.parse((PROJECT / filename).read_text(encoding="utf-8"))


def test_overview_shortcuts_have_callback_based_navigation():
    source = (PROJECT / "dashboard" / "overview_viz.py").read_text(encoding="utf-8")
    assert "on_click=navigate_to" in source
    assert "run_market_experiment(" in source
    assert "st.session_state" in source


def test_navigation_rejects_unknown_destinations():
    import pytest
    with pytest.raises(ValueError):
        navigate_to("NOT_A_REAL_PAGE")


def test_overview_renders_real_registry_statistics_in_custom_cards():
    source = (PROJECT / "dashboard" / "overview_viz.py").read_text(encoding="utf-8")
    assert 'len(agents)' in source
    assert 'len(sellers)' in source
    assert 'len(retailers)' in source
    assert 'len(SCENARIO_NAMES) - 1' in source
    assert 'smc-kpi-grid' in source
    assert 'smc-kpi-card' in source
    assert 'st.metric(title, value' not in source


def test_agent_cards_are_role_colored_and_trace_remains_real():
    overview = (PROJECT / "dashboard" / "overview_viz.py").read_text(encoding="utf-8")
    theme = (PROJECT / "dashboard" / "ui_design.py").read_text(encoding="utf-8")
    assert 'smc-agent-grid' in overview
    assert 'smc-agent-card' in overview
    assert 'smc-agent-avatar' in overview
    assert 'run_market_experiment(' in overview
    for classname in ('smc-kpi-card', 'smc-agent-card', 'smc-agent-avatar'):
        assert f'.{classname}' in theme
    assert 'st.button(' in overview


def test_quick_launch_navigation_keeps_real_buttons():
    overview = (PROJECT / "dashboard" / "overview_viz.py").read_text(encoding="utf-8")
    theme = (PROJECT / "dashboard" / "ui_design.py").read_text(encoding="utf-8")
    for key in ("quick_market", "quick_compete", "quick_experiment"):
        assert f'"{key}"' in overview
        assert f".st-key-{key} button" in theme
    assert 'on_click=navigate_to' in overview
    assert 'smc-launch-item' in overview


def test_sidebar_uses_grouped_buttons_instead_of_radio_circles():
    theme = (PROJECT / "dashboard" / "ui_design.py").read_text(encoding="utf-8")
    assert "st.radio(" not in theme
    assert 'key=f"smc_nav_{index}"' in theme
    assert 'on_click=navigate_to' in theme
    assert 'type="primary" if selected == page else "secondary"' in theme
    for group in ("WORKSPACE", "AGENT WORKFLOWS", "LEARNING LABS", "PRESENTATION"):
        assert group in theme
    assert '.smc-menu-group' in theme
    assert 'smc_nav_' in theme


def test_viva_page_has_ten_english_only_stages_and_real_simulation_calls():
    source = (PROJECT / "dashboard" / "viva_mode.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert '"🎓 Viva Presentation"' in (PROJECT / "dashboard" / "ui_design.py").read_text(encoding="utf-8")
    assert 'if selected_page == PAGES[9]:' in (PROJECT / "dashboard" / "app.py").read_text(encoding="utf-8")
    for part in (
        'Full multi-agent architecture',
        'Meet the two seller agents',
        'Meet retailer R1',
        'Discover available suppliers',
        'Replay actual negotiations',
        'Retailer selects the supplier',
        'Cooperate on delivery',
        'Reserve simulated resources',
        'Respond to a market shock',
        'Evaluate MAS characteristics',
    ):
        assert part in source
    for call in (
        'public_listings()',
        'run_supplier_competition(',
        'run_delivery_coordination(',
        'run_market_experiment(',
        'run_experiment_batch(',
    ):
        assert call in source
    assert 'viva_message_step' in source
    assert 'No real purchase' in source


def test_viva_presentation_typography_large_enough_for_projector():
    source = (PROJECT / "dashboard" / "viva_mode.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert "font-size:29px!important" in source  # Agent names
    assert "font-size:22px!important" in source  # Agent descriptions
    assert "font-size:23px!important" in source  # Communication connector labels
    assert "min-height:145px" in source          # Large architecture cards
    assert "font-size:46px!important" in source  # Numerical metrics
    assert "@media(max-width:850px)" in source   # Preserve mobile usability


def test_viva_evaluation_uses_projector_readable_evidence_cards():
    source = (PROJECT / "dashboard" / "viva_mode.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert "def _presentation_table(" in source
    assert "viva-feature-grid" in source
    assert "viva-feature-card" in source
    assert "viva-feature-title" in source
    assert "font-size:28px!important" in source
    assert "viva-table" in source
    assert "html.escape(str(value), quote=True)" in source
    evaluation = source.split("def _evaluation():", 1)[1].split("RENDER =", 1)[0]
    assert "st.dataframe(" not in evaluation
    assert "_presentation_table([" in evaluation


def test_interactive_workflow_simulator_is_a_real_routed_workspace():
    theme = (PROJECT / "dashboard" / "ui_design.py").read_text(encoding="utf-8")
    app = (PROJECT / "dashboard" / "app.py").read_text(encoding="utf-8")
    simulator = (PROJECT / "dashboard" / "workflow_simulator.py").read_text(encoding="utf-8")
    ast.parse(simulator)
    assert '"⚡ Workflow Simulator"' in theme
    assert 'if selected_page == PAGES[10]:' in app
    assert 'render_workflow_simulator()' in app
    for marker in (
        "st.form(", "st.form_submit_button(",
        "run_supplier_competition(", "run_delivery_coordination(",
        "ReservationLedger.from_marketplace()", "neon_scene(",
        "st.session_state", "time.sleep(", "wf_index",
        "Play to final outcome", "Final multi-agent decision",
    ):
        assert marker in simulator


def test_workflow_replay_builds_events_from_real_recordings_only():
    from dashboard.workflow_simulator import _recorded_events, _stage_html

    competition = {
        "retailer": type("Retailer", (), {"agent_id": "R1"})(),
        "discovered_seller_ids": ["S1"],
        "evaluated_seller_ids": ["S1"],
        "negotiations": {
            "S1": {"timeline": [
                {"sender": "R1", "receiver": "S1", "performative": "PROPOSE",
                 "price": 150.0, "round": 1, "reason": "Actual submitted offer."},
                {"sender": "S1", "receiver": "R1", "performative": "ACCEPT-PROPOSAL",
                 "price": 150.0, "round": 1, "reason": "Actual seller decision."},
            ]}
        },
        "selection": {"selected_seller_id": "S1", "reasoning": "Selected after evaluation."},
    }
    coordination = {
        "events": [{"actor": "C1", "action": "VERIFY",
                    "explanation": "Real coordinator verification."}],
        "status": "RESERVED_SIMULATED", "reason": "Synthetic allocation completed.",
    }
    events = _recorded_events(competition, coordination)
    assert len(events) == 6
    assert [item["phase"] for item in events] == [
        "Discovery", "Negotiation", "Negotiation", "Supplier selection",
        "Delivery & reservation", "Final outcome",
    ]
    assert events[1]["description"] == "Actual submitted offer."
    assert events[2]["action"] == "ACCEPT-PROPOSAL"
    assert events[-1]["action"] == "RESERVED_SIMULATED"
    assert "RECORDED EVENT" in _stage_html(events[0], 0, len(events))
    assert "no real" in events[-1]["note"].lower()


def test_workflow_scene_escapes_untrusted_values():
    from dashboard.workflow_simulator import _stage_html

    scene = _stage_html({
        "phase": "<b>unsafe</b>", "sender": "<img src=x>",
        "receiver": "R1", "action": "INFORM",
        "description": "<script>alert(1)</script>", "note": "From live trace",
    }, 0, 1)
    assert "<script>" not in scene
    assert "<img src=x>" not in scene
    assert "&lt;script&gt;" in scene
