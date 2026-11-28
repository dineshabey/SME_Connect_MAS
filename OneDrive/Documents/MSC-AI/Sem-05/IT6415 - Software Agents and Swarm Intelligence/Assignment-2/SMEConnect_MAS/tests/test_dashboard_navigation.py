"""Phase 06 dashboard navigation and structural smoke checks.

These checks do not claim browser-level visual verification.
"""
import ast
from pathlib import Path

from dashboard.ui_design import PAGE_METADATA, PAGES, navigate_to


PROJECT = Path(__file__).resolve().parents[1]


def test_all_workspaces_have_distinct_navigation_names_and_descriptions():
    assert len(PAGES) == 12
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
        'st.session_state["wf_autoplay"] = True',
        'st.session_state.pop("wf_autoplay", False)',
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


def test_animated_sequence_is_routed_and_uses_real_workflow_data():
    src = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    app = (PROJECT / "dashboard" / "app.py").read_text(encoding="utf-8")
    theme = (PROJECT / "dashboard" / "ui_design.py").read_text(encoding="utf-8")
    ast.parse(src)
    assert '"🔀 Sequence Replay"' in theme
    assert "if selected_page == PAGES[11]:" in app
    assert "render_sequence_replay()" in app
    for item in (
        "def _sequence_events(", "def _sequence_html(", "_run_session(",
        'components.html(', 'msg.performative.value', 'msg.sender', 'msg.receiver',
        'st.button(', 'Play', 'Pause', 'Show final result',
    ):
        assert item in src


def test_sequence_trace_is_grounded_in_validated_messages():
    from dashboard.sequence_replay import _sequence_events

    class Dummy:
        def __init__(self, sender, receiver, action, price=150.0, quantity=200):
            self.sender, self.receiver, self.unit_price, self.quantity = (
                sender, receiver, price, quantity)
            self.performative = type("P", (), {"value": action})()

    run = {
        "competition": {
            "retailer": type("Buyer", (), {"agent_id": "R1"})(),
            "discovered_seller_ids": ["S1"],
            "evaluated_seller_ids": ["S1"],
            "negotiations": {"S1": {
                "timeline": [{"sender": "R1", "receiver": "S1",
                              "performative": "PROPOSE", "reason": "Submitted.",
                              "round": 1}],
                "messages": [Dummy("R1", "S1", "PROPOSE")],
            }},
            "selection": {"selected_seller_id": "S1",
                          "reasoning": "Highest feasible profit."},
        },
        "coordination": {
            "events": [
                {"actor": "C1", "action": "CFP",
                 "explanation": "C1 → D1 delivery request"},
                {"actor": "D1", "action": "THINK",
                 "explanation": "Checked capacity."},
                {"actor": "D1", "action": "PROPOSE",
                 "explanation": "D1 → C1 delivery quote"},
            ],
            "messages": [Dummy("C1", "D1", "CFP", 0.0),
                         Dummy("D1", "C1", "PROPOSE", 1000.0, 1)],
            "status": "RESERVED_SIMULATED",
            "reason": "Simulated allocation.",
        },
    }
    events = _sequence_events(run)
    assert [e["kind"] for e in events] == [
        "decision", "message", "decision", "message",
        "decision", "message", "decision",
    ]
    assert events[3]["sender"] == "C1"
    assert events[3]["receiver"] == "D1"
    assert events[5]["sender"] == "D1"
    assert events[5]["receiver"] == "C1"
    assert events[4]["kind"] == "decision"
    assert events[-1]["action"] == "RESERVED_SIMULATED"


def test_sequence_rejects_mismatched_recorded_messages():
    import pytest
    from dashboard.sequence_replay import _sequence_events

    run = {
        "competition": {
            "retailer": type("Buyer", (), {"agent_id": "R1"})(),
            "discovered_seller_ids": ["S1"],
            "evaluated_seller_ids": ["S1"],
            "negotiations": {"S1": {"timeline": [{"sender": "R1"}], "messages": []}},
        },
        "coordination": {},
    }
    with pytest.raises(ValueError, match="counts differ"):
        _sequence_events(run)


def test_sequence_html_escapes_untrusted_script_payloads():
    from dashboard.sequence_replay import _sequence_html

    event = {"sender": "R1", "receiver": "S1", "kind": "message",
             "action": "PROPOSE", "phase": "Negotiation",
             "label": "</script><script>alert(1)</script>",
             "description": "<img src=x onerror=alert(1)>"}
    html = _sequence_html([event], ["R1", "S1"], {
        "status": "STOP", "seller": "None",
        "price": "-", "delivery": "-", "total": "-", "reason": "Ended.",
    })
    assert "</script><script>alert(1)</script>" not in html
    assert "<img src=x onerror=alert(1)>" not in html
    assert "\\u003c" in html
    assert "document.createElementNS" in html
    assert "clearInterval" in html


def test_sequence_decision_explanations_are_projector_readable():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    for required in (
        'id="decision-panel"', 'id="why-title"', 'id="reason"', 'id="impact"',
        'id="provenance"', 'font-size:26px!important',
        'font-size:24px', 'AGENT DECISION EXPLAINED',
        'Why did ', 'What happened next?', 'RESERVED_SIMULATED',
    ):
        assert required in source


def test_sequence_final_explanation_uses_actual_reservation_values():
    from dashboard.sequence_replay import _sequence_events

    retailer = type("Buyer", (), {"agent_id": "R1"})()
    run = {
        "competition": {
            "retailer": retailer,
            "discovered_seller_ids": ["S1"],
            "evaluated_seller_ids": [],
            "negotiations": {},
            "selection": {"selected_seller_id": "S1", "reasoning": "Feasible choice."},
        },
        "coordination": {
            "events": [], "messages": [], "status": "RESERVED_SIMULATED",
            "reason": "Recorded reservation.",
            "reservation": {
                "quantity": 120, "seller_id": "S1", "retailer_id": "R1",
                "unit_price": 155.0, "delivery_fee": 1000.0,
                "reserved_total": 19600.0,
            },
        },
    }
    final = _sequence_events(run)[-1]
    assert final["kind"] == "decision"
    assert "120 packets" in final["description"]
    assert "S1" in final["description"]
    assert "Rs.155.00" in final["description"]
    assert "Rs.1,000.00" in final["description"]
    assert "Rs.19,600.00" in final["description"]


def test_sequence_technical_evidence_uses_large_escaped_tables():
    from dashboard.sequence_replay import _large_evidence_table
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert "def _large_evidence_table(" in source
    assert "escape(str(row.get(c" in source
    assert "font-size:20px!important" in source
    assert "font-size:19px!important" in source
    assert 'st.dataframe(result["sequence_events"]' not in source


def test_sequence_configuration_is_live_and_run_is_independent():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert 'with st.form("sequence_config")' not in source
    assert 'st.markdown("### Live scenario preview")' in source
    assert '"seq_quantity"' in source
    assert '"seq_retailer"' in source
    assert '"seq_sellers"' in source
    assert 'disabled=not can_run' in source
    assert 'quantity_ok = quantity <= buyer.demand' in source
    assert 'run = st.button(' in source
    assert 'if run:' in source


def test_sequence_iframe_accommodates_large_explanation_and_final_result():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert 'height=1600, scrolling=True' in source
    assert 'type:"streamlit:setFrameHeight"' in source
    assert "ResizeObserver(resizeFrame)" in source
    assert "bootstrap@5.3.8/dist/css/bootstrap-grid.min.css" in source
    assert 'class="row g-3 detail"' in source
    assert 'class="col-12 col-xl-7"' in source
    assert '#decision-panel #reason{overflow-wrap:anywhere' in source
    assert '.detail .panel{height:100%;min-height:270px;overflow:visible;overflow-wrap:anywhere}' in source



def test_sequence_preview_reacts_without_executing_agent_graph():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert "def _sequence_preview_changed()" in source
    assert 'on_change=_sequence_preview_changed' in source
    assert 'key="seq_quantity", on_change=_sequence_preview_changed' in source
    assert "Current request:" in source
    assert "Opening offer received:" in source
    assert "Expected gross margin at offer:" in source
    assert "Agent baseline" in source
    assert "Insufficient advertised stock" in source
    assert "Click Run and animate agent sequence" in source
    assert 'if run:' in source
    assert 'run_result = _run_session(' in source
    assert "st.form(" not in source


def test_sequence_replay_uses_readable_agent_role_labels_without_changing_ids():
    from dashboard.sequence_replay import _agent_label, _sequence_html

    assert _agent_label("R1") == "Retailer Agent R1"
    assert _agent_label("R2") == "Retailer Agent R2"
    assert _agent_label("S1") == "Seller Agent S1"
    assert _agent_label("S2") == "Seller Agent S2"
    assert _agent_label("C1") == "Coordinator Agent C1"
    assert _agent_label("D1") == "Delivery Agent D1"
    assert _agent_label("M1") == "Market Agent M1"
    assert _agent_label("UNKNOWN") == "UNKNOWN"
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert "format_func=_agent_label" in source
    assert "actorLabel(agent)" in source
    assert "actorLabel(item.sender)" in source
    event = {"phase": "Negotiation", "kind": "message", "sender": "R1",
             "receiver": "S1", "action": "PROPOSE", "label": "PROPOSE",
             "description": "Recorded offer."}
    html = _sequence_html([event], ["R1", "S1"], {
        "status": "NO_AGREEMENT", "seller": "None", "price": "-",
        "delivery": "-", "total": "-", "reason": "No agreement."
    })
    assert '"R1": "Retailer Agent R1"' in html
    assert '"S1": "Seller Agent S1"' in html
    assert '"sender": "R1"' in html


def test_sequence_fullscreen_and_fit_controls_are_real_and_replay_only():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    for required in (
        'id="fullscreen"', 'id="fit"', '⛶ Full Screen',
        'Fit Entire Sequence', 'shell.requestFullscreen()',
        'document.exitFullscreen()', 'document.addEventListener("fullscreenchange"',
        'fitAll=true', 'if(fitAll){', 'svg.setAttribute("preserveAspectRatio"',
        'height=1600, scrolling=True', 'st.download_button(',
        'SMEConnect_Sequence_Replay.html',
    ):
        assert required in source
    # Playback is entirely client-side: a fullscreen/fit click never runs a
    # new seller negotiation, delivery coordination or reservation ledger.
    iframe = source.split("page = r'''", 1)[1].split("'''", 1)[0]
    assert "_run_session(" not in iframe
    assert "run_delivery_coordination(" not in iframe
    assert "ReservationLedger" not in iframe


def test_sequence_fullscreen_overview_uses_readable_event_cards_instead_of_tiny_svg():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    for marker in (
        'id="sequence-overview"',
        'class="sequence-overview"',
        '.diagram.overview-active #sequence{display:none}',
        'function renderOverview(){',
        'overview.style.gridTemplateRows=',
        'Math.ceil(ev.length/3)',
        'j===index?"current"',
        'card.onclick=()=>{stop();step(j)}',
        'viewport.classList.toggle("overview-active",fitAll)',
        'if(fitAll){',
        'fitButton.textContent=fitAll?"◉ Detailed Sequence":"⊞ Fit Entire Sequence"',
        '.shell:fullscreen:has(.diagram.overview-active) .detail{display:flex}',
    ):
        assert marker in source
    # The original event-by-event SVG is deliberately retained as a separate view.
    assert 'function draw(){' in source
    assert 'svg.replaceChildren();' in source


def test_sequence_presentation_cockpit_moves_explanations_left():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    for marker in (
        'class="presentation-layout"',
        'class="presentation-side"',
        'class="presentation-stage"',
        '.presentation-layout{display:grid;grid-template-columns:',
        '.shell:fullscreen .presentation-layout',
        '.shell:fullscreen .presentation-side',
        '.shell:fullscreen .presentation-stage .diagram',
        '.shell:fullscreen:has(.diagram.overview-active) .detail{display:flex}',
        'class="row g-3 detail"',
    ):
        assert marker in source
    side = source.index('<aside class="presentation-side"')
    stage = source.index('<div class="presentation-stage">')
    assert side < stage
    assert 'height:100dvh;overflow:hidden' in source


def test_sequence_run_attempts_fullscreen_with_browser_safe_fallback():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    for marker in (
        'id="present"',
        'function tryAutomaticFullscreen(){',
        'requestAnimationFrame(tryAutomaticFullscreen)',
        'presentButton.onclick=launchPresentation;',
        'function launchPresentation(){',
        'if(!isFullscreen())toggleFullscreen();',
        'Browser requires a direct click:',
    ):
        assert marker in source
    assert 'run_result = _run_session(' in source
    # Fullscreen/replay controls must not re-execute backend agent actions.
    embedded_html = source.split("page = r'''", 1)[1].split("'''", 1)[0]
    assert '_run_session(' not in embedded_html


def test_sequence_run_enters_presentation_mode_and_hides_setup():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert 'presenting = bool(st.session_state.get("seq_presenting", False))' in source
    assert 'if not presenting:' in source
    assert 'st.markdown("### Configure and run a real sequence")' in source
    assert 'st.markdown("### Live scenario preview")' in source
    assert 'st.session_state["seq_presenting"] = True' in source
    assert 'st.session_state["seq_presenting"] = False' in source
    assert '"✎ Edit Scenario"' in source
    assert 'key="seq_edit_scenario"' in source
    assert 'if not st.session_state.get("seq_presenting", False) and (' in source
    assert 'st.rerun()' in source
    # Editing the UI simply changes session presentation state, never reruns
    # the negotiation/reservation engine until the explicit Run button is clicked.
    edit_block = source.split('key="seq_edit_scenario"', 1)[1].split(
        'result = st.session_state.get("sequence_run")', 1
    )[0]
    assert '_run_session(' not in edit_block
    assert 'st.session_state["seq_presenting"] = False' in edit_block


def test_sequence_edit_scenario_restores_previous_input_values():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert 'st.session_state["seq_saved_controls"] = {' in source
    assert 'st.session_state.pop("seq_restore_inputs", False)' in source
    assert 'st.session_state["seq_restore_inputs"] = True' in source
    for key in (
        "seq_retailer", "seq_sellers", "seq_quantity", "seq_offer",
        "seq_target", "seq_rounds", "seq_resale", "seq_speed",
    ):
        assert '"'+key+'":' in source


def test_sequence_agent_names_remain_fixed_outside_scrollable_diagram():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert 'id="agent-header-viewport"' in source
    assert 'id="agent-header-track"' in source
    assert 'function renderAgentHeader(){' in source
    assert 'function alignAgentHeader(){' in source
    assert 'label.textContent=actorLabel(agent);' in source
    assert 'viewport.addEventListener("scroll",alignAgentHeader' in source
    assert 'requestAnimationFrame(alignAgentHeader);' in source
    assert 'matrix.a*x(j)+matrix.e-rect.left' in source
    assert '.presentation-stage:has(.diagram.overview-active) .agent-header-viewport{display:none}' in source
    html = source.split("page = r'''", 1)[1].split("'''", 1)[0]
    header_pos = html.index('id="agent-header-viewport"')
    viewport_pos = html.index('id="viewport"')
    assert header_pos < viewport_pos
    assert 'id="sticky-agent-header"' not in html
    assert 'position:sticky' not in html
