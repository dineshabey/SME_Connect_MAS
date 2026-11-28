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
        "ReservationLedger.from_marketplace(market_state)", "neon_scene(",
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
    assert 'height=900, scrolling=True' in source
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
    assert "Retailer Agent Limits" in source
    assert "Insufficient scenario stock" in source
    assert "Click Run and animate agent sequence" in source
    assert 'if run:' in source
    assert 'run_result = _run_session(' in source
    # Only the seller-edit modal uses a form; main scenario inputs remain live.
    main_controls = source.split("def render_sequence_replay():", 1)[1].split(
        'run = st.button(', 1
    )[0]
    assert "st.form(" not in main_controls


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
        'height=900, scrolling=True', 'st.download_button(',
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
    # Sticky positioning is allowed on the fixed header wrapper. The invariant
    # is structural: agent header precedes the independently scrollable viewport.
    assert '.agent-header-viewport{position:sticky;top:0;z-index:30}' in html
    assert '<div class="diagram" id="viewport">' in html


def test_sequence_desktop_only_message_pane_scrolls_and_header_remains_visible():
    src = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(src)
    for marker in (
        '@media (min-width:1051px)',
        'html,body{height:100%;overflow:hidden}',
        '.shell:not(:fullscreen) .presentation-stage .diagram{',
        'flex:1 1 0;min-height:0;height:auto;overflow:auto',
        '.agent-header-viewport{position:sticky;top:0;z-index:30}',
        'components.html(sequence_document, height=900, scrolling=True)',
    ):
        assert marker in src


def test_seller_popup_is_real_dialog_and_uses_isolated_decision_parameters():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    for expected in (
        '@st.dialog("⚙ Configure Seller Agent", width="large")',
        'def _edit_seller_popup(seller_id: str):',
        '"Minimum acceptable price (Rs.) · private decision rule"',
        '"Target selling price (Rs.) · private decision rule"',
        '"Available stock (packets)"',
        'st.session_state["seq_seller_overrides"] = current',
        'market_state=market_state,',
        'scenario_sellers[sid]',
        '_edit_seller_popup(sid)',
        'st.button(',
    ):
        assert expected in source


def test_seller_popup_changes_negotiation_policy_and_reservation_stock():
    from dashboard.sequence_replay import _seller_market_snapshot
    from dashboard.workflow_simulator import _run_session
    from smeconnect.environment.marketplace import build_agents

    original = {a.agent_id: a for a in build_agents() if a.role == "seller"}
    snapshot = _seller_market_snapshot({
        "S2": {
            "minimum_price": 175.0,
            "target_price": 185.0,
            "available_stock": 90,
        }
    })
    altered = {a.agent_id: a for a in build_agents(snapshot) if a.role == "seller"}
    assert altered["S2"].minimum_price == 175.0
    assert altered["S2"].target_price == 185.0
    assert altered["S2"].available_stock == 90
    # The default registered seller is never mutated by the what-if editor.
    assert original["S2"].minimum_price == 140.0
    assert original["S2"].available_stock == 300
    baseline = _run_session("R1", ["S1", "S2"], 200, 150.0, 150.0, 5, 200.0)
    customized = _run_session(
        "R1", ["S1", "S2"], 200, 150.0, 150.0, 5, 200.0,
        market_state=snapshot,
    )
    assert baseline["competition"]["selection"]["selected_seller_id"] == "S2"
    assert customized["competition"]["selection"]["selected_seller_id"] == "S1"
    assert customized["before"]["seller_stock"]["S2"] == 90
    assert customized["after"]["seller_stock"]["S2"] == 90
    assert customized["after"]["seller_stock"]["S1"] == 300


def test_seller_popup_rejects_invalid_internal_policy_values():
    import pytest
    from dashboard.sequence_replay import _seller_market_snapshot

    with pytest.raises(ValueError):
        _seller_market_snapshot({"UNKNOWN": {
            "minimum_price": 150, "target_price": 170, "available_stock": 100
        }})
    with pytest.raises(ValueError):
        _seller_market_snapshot({"S1": {
            "minimum_price": 180, "target_price": 160, "available_stock": 500
        }})
    with pytest.raises(ValueError):
        _seller_market_snapshot({"S1": {
            "minimum_price": 150, "target_price": 170, "available_stock": -1
        }})


def test_edited_seller_prices_propagate_through_real_negotiation_and_selection():
    from dashboard.sequence_replay import _seller_market_snapshot, _seller_run_evidence
    from dashboard.workflow_simulator import _run_session

    normal = _run_session("R1", ["S1", "S2"], 200, 150, 150, 5, 200)
    assert normal["competition"]["selection"]["selected_seller_id"] == "S2"
    altered = _seller_market_snapshot({
        "S1": {"minimum_price": 160, "target_price": 180, "available_stock": 500},
        "S2": {"minimum_price": 175, "target_price": 185, "available_stock": 300},
    })
    result = _run_session(
        "R1", ["S1", "S2"], 200, 150, 150, 5, 200,
        market_state=altered,
    )
    evidence = {r["seller_id"]: r for r in _seller_run_evidence(result)}
    assert evidence["S1"]["minimum_price"] == 160
    assert evidence["S1"]["target_price"] == 180
    assert evidence["S2"]["minimum_price"] == 175
    assert evidence["S2"]["target_price"] == 185
    assert result["competition"]["negotiations"]["S1"]["status"] == "REJECTED"
    assert result["competition"]["negotiations"]["S2"]["status"] == "REJECTED"
    assert result["competition"]["selection"]["selected_seller_id"] is None
    assert result["coordination"]["status"] == "NO_AGREEMENT"
    assert evidence["S1"]["reserved_packets"] == 0
    assert evidence["S2"]["reserved_packets"] == 0
    assert result["after"]["seller_stock"] == result["before"]["seller_stock"]


def test_seller_price_changes_affect_actual_successful_booking_and_comparison():
    from dashboard.sequence_replay import (
        _seller_market_snapshot, _seller_run_evidence, _compare_seller_runs,
    )
    from dashboard.workflow_simulator import _run_session

    before = _run_session("R1", ["S1", "S2"], 200, 150, 150, 5, 200)
    snapshot = _seller_market_snapshot({
        "S2": {"minimum_price": 175, "target_price": 185, "available_stock": 300}
    })
    after = _run_session(
        "R1", ["S1", "S2"], 200, 150, 150, 5, 200,
        market_state=snapshot,
    )
    assert after["competition"]["selection"]["selected_seller_id"] == "S1"
    assert after["coordination"]["status"] == "RESERVED_SIMULATED"
    reservation = after["coordination"]["reservation"]
    assert reservation["seller_id"] == "S1"
    assert reservation["unit_price"] == 155
    policy = {row["seller_id"]: row for row in _seller_run_evidence(after)}
    assert policy["S2"]["negotiation_status"] == "REJECTED"
    assert policy["S2"]["remaining_stock"] == 300
    assert policy["S1"]["remaining_stock"] == 300
    compare = {row["seller_id"]: row for row in _compare_seller_runs(before, after)}
    assert compare["S2"]["previous_minimum"] == 140
    assert compare["S2"]["current_minimum"] == 175
    assert compare["S2"]["previous_selected"] is True
    assert compare["S2"]["current_selected"] is False
    assert compare["S1"]["current_selected"] is True


def test_seller_policy_evidence_detects_disagreement_with_recorded_ledger():
    import pytest
    from dashboard.sequence_replay import _seller_run_evidence
    from dashboard.workflow_simulator import _run_session

    result = _run_session("R1", ["S1", "S2"], 200, 150, 150, 5, 200)
    result["before"]["seller_stock"]["S1"] = 999
    with pytest.raises(ValueError, match="disagree"):
        _seller_run_evidence(result)


def test_seller_evidence_is_clearly_separated_from_public_messages():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    for marker in (
        'def _seller_run_evidence(run: dict)',
        'def _compare_seller_runs(previous: dict, current: dict)',
        'seller_policy_evidence',
        'previous_comparison',
        'Seller policy verification',
        'Effective seller policies and actual outcomes',
        'Previous Run vs Current Run',
        'run_result["seller_policy_evidence"] = _seller_run_evidence(run_result)',
    ):
        assert marker in source


def test_sequence_replay_warns_if_seller_policy_changes_without_rerun():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert 'st.session_state.get("seq_preview_revision", 0)' in source
    assert 'st.session_state.get("seq_last_run_revision", 0)' in source
    assert "Scenario or Seller Agent policy changed — rerun required." in source
    assert "ACTUAL POLICY USED IN THIS RUN" in source
    assert "_seller_run_evidence(result)" in source


def test_sequence_policy_notes_are_large_readable_green_explanation_panels():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    for marker in (
        "seq-policy-box", "seq-policy-heading", "seq-policy-value",
        "seq-policy-info", "Retailer Agent Limits",
        "Registered Demand", "Available Budget",
        "Seller Private Pricing Rules", "Minimum Acceptable Price",
        "Target Selling Price", "Minimum = lowest price the seller",
        "Shown for viva explanation only; not shared with buyer agents.",
        "Budget = maximum funds available for buying.",
        "font-size:22px", "font-size:24px",
    ):
        assert marker in source
    assert "Private demo policy: minimum" not in source
    assert "Agent baseline · Demand" not in source


def test_sequence_final_decision_has_prominent_readable_status_card():
    from dashboard.sequence_replay import _final_decision_html
    from dashboard.workflow_simulator import _run_session

    successful = _run_session("R1", ["S1", "S2"], 200, 150, 150, 5, 200)
    html = _final_decision_html(successful)
    assert "FINAL MULTI-AGENT DECISION" in html
    assert "Seller Agent S2" in html
    assert "RESERVED_SIMULATED" in html
    assert "SIMULATED ORDER RESERVED" in html
    assert "200 packets" in html
    assert "Rs.31,000.00" in html
    assert "Synthetic simulation only" in html
    assert 'class="seq-result-card success"' in html

    declined = _run_session("R1", ["S1"], 200, 100, 100, 2, 200)
    failure_html = _final_decision_html(declined)
    assert 'class="seq-result-card attention"' in failure_html
    assert "No supplier selected" in failure_html
    assert "Not reserved" in failure_html
    assert "SIMULATED ORDER RESERVED" not in failure_html


def test_sequence_final_decision_card_is_responsive_and_not_buried_in_expander():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert "st.markdown(_final_decision_html(result), unsafe_allow_html=True)" in source
    assert ".seq-result-card{" in source
    assert ".seq-result-grid{" in source
    assert "@media(max-width:600px)" in source
    assert source.index("st.markdown(_final_decision_html(result)") < source.index(
        'with st.expander("✅ Seller policy verification'
    )


def test_sequence_viva_summary_includes_all_seven_registered_agents():
    from dashboard.sequence_replay import _AGENT_SUMMARIES, _agent_summary_html
    from smeconnect.environment.marketplace import build_agents

    known_ids = {agent.agent_id for agent in build_agents()}
    summary_ids = [agent_id for agent_id, *_ in _AGENT_SUMMARIES]
    assert len(summary_ids) == len(known_ids) == 7
    assert set(summary_ids) == known_ids
    html = _agent_summary_html()
    for agent_id in known_ids:
        assert agent_id in html
    assert "Agent Network" in html
    assert "Market Agent M1 acts " in html and "Market Adaptation experiments" in html


def test_sequence_viva_conclusion_maps_professors_three_essential_mas_features():
    from dashboard.sequence_replay import (
        _MAS_FEATURE_SUMMARIES, _AGENT_CHARACTERISTICS,
        _mas_features_html,
    )

    features = [name for name, *_ in _MAS_FEATURE_SUMMARIES]
    assert features == [
        "1 · Communication", "2 · Coordination", "3 · Negotiation",
    ]
    assert {name for name, *_ in _AGENT_CHARACTERISTICS} == {
        "Situatedness", "Works for a master / owner", "Autonomy",
        "Adaptivity — Reactive", "Sociability / Interaction",
    }
    html = _mas_features_html()
    assert "Multi-Agent Capabilities" in html
    assert "Core capabilities demonstrated by the simulation" in html
    assert "Agent Characteristics" in html
    assert "Self-Interested MAS (SMAS)" in html
    assert "Topic 4 · Slide 119" not in html
    assert "KQML" in html
    assert "not implemented or proven" in html
    assert "not a decentralized production deployment" in html
    assert "System Architecture" in html



def test_viva_summary_position_and_readability_in_sequence_page():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    render = source.split("def render_sequence_replay():", 1)[1]
    assert render.index("st.markdown(_agent_summary_html()") < render.index(
        'st.markdown("### Configure and run a real sequence")'
    )
    assert render.index("st.markdown(_mas_features_html()") > render.index(
        'with st.expander("Technical evidence'
    )
    for marker in (
        ".seq-flow-pair{display:grid;",
        ".seq-mas-features{display:grid;",
        ".seq-flow-node-name{font-size:",
        ".seq-mas-feature-title{font-size:",
        "@media(max-width:760px)",
    ):
        assert marker in source


def test_viva_does_not_mislabel_agent_traits_as_essential_mas_features():
    from dashboard.sequence_replay import (
        _MAS_FEATURE_SUMMARIES, _AGENT_CHARACTERISTICS, _MAS_NOT_DEMONSTRATED,
    )
    assert len(_MAS_FEATURE_SUMMARIES) == 3
    mas_features = " ".join(row[0] for row in _MAS_FEATURE_SUMMARIES)
    for trait in ("Autonomy", "Learning", "Situatedness", "Mobility"):
        assert trait not in mas_features
    assert any("Reactive" in row[0] for row in _AGENT_CHARACTERISTICS)
    assert "Learning from experience" in _MAS_NOT_DEMONSTRATED
    assert "self-organization" in _MAS_NOT_DEMONSTRATED


def test_sequence_dashboard_headings_are_clean_and_professional():
    from dashboard.sequence_replay import _agent_summary_html, _mas_features_html
    agent_html = _agent_summary_html()
    feature_html = _mas_features_html()
    assert "Agent Network" in agent_html
    assert "Multi-Agent Capabilities" in feature_html
    assert "Agent Characteristics" in feature_html
    assert "System Architecture" in feature_html
    assert "Professor" not in feature_html
    assert "Slide 119" not in feature_html
    assert "OUR 7" not in agent_html
    assert "Slide 35" not in feature_html


def test_agent_network_diagram_explains_real_request_to_reservation_flow():
    from dashboard.sequence_replay import _agent_summary_html
    html = _agent_summary_html()
    for marker in (
        "Agent Network",
        "Retailer Request",
        "Independent Seller Negotiation",
        "Retailer-Side Supplier Selection",
        "Coordination",
        "Delivery Feasibility",
        "Final Outcome",
        "Compare Feasible Offers",
        "Simulated Reservation Decision",
        "Agent R1", "Agent R2", "Agent S1", "Agent S2",
        "Agent C1", "Agent D1",
        "Why LangGraph?",
        "Pydantic messages and the in-memory message bus",
        "S1 and S2 are the currently implemented sellers",
    ):
        assert marker in html
    stages = [
        "1 · Retailer Request", "2 · Independent Seller Negotiation",
        "3 · Retailer-Side Supplier Selection", "4 · Coordination",
        "5 · Delivery Feasibility", "6 · Final Outcome",
    ]
    assert [html.index(stage) for stage in stages] == sorted(
        html.index(stage) for stage in stages
    )
    assert "Market Agent M1 acts " in html
    assert "Market Adaptation experiments" in html
    assert "not in the order sequence" in html


def test_agent_network_diagram_has_projector_readable_responsive_nodes():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    for marker in (
        ".seq-flow-layout{display:flex;",
        ".seq-flow-pair{display:grid;",
        ".seq-flow-node-name{font-size:clamp(20px",
        ".seq-flow-langgraph strong{display:block;font-size:22px",
        ".seq-flow-connector i{font-size:39px",
        "@media(max-width:800px)",
    ):
        assert marker in source


def test_delivery_agent_preview_card_shows_real_capacity_and_trip_fee():
    source = (PROJECT / "dashboard" / "sequence_replay.py").read_text(encoding="utf-8")
    ast.parse(source)
    for marker in (
        'aria-label="Delivery Agent D1 preview"',
        'Delivery Agent D1',
        'Available Capacity',
        'Delivery Fee per Trip',
        'Requested Quantity',
        'delivery.cost_per_trip',
        'delivery.capacity',
        'The Delivery Agent makes its',
        '.seq-delivery-card{',
        '.seq-delivery-metrics{display:grid;',
    ):
        assert marker in source
    assert 'delivery = next(a for a in build_agents() if a.role == "delivery"' in source


def test_final_result_distinguishes_product_cost_delivery_quote_and_total():
    from dashboard.sequence_replay import _final_decision_html
    from dashboard.workflow_simulator import _run_session

    run = _run_session("R1", ["S1", "S2"], 200, 150, 150, 5, 200)
    card = _final_decision_html(run)
    assert run["coordination"]["status"] == "RESERVED_SIMULATED"
    assert "PRODUCT COST" in card
    assert "DELIVERY FEE (D1)" in card
    assert "SIMULATED ORDER TOTAL (INCLUDING DELIVERY)" in card
    assert "Rs.30,000.00" in card
    assert "Rs.1,000.00" in card
    assert "Rs.31,000.00" in card

    declined = _run_session("R1", ["S1"], 200, 100, 100, 2, 200)
    failed_card = _final_decision_html(declined)
    assert "Not quoted" in failed_card
    assert "Not reserved" in failed_card
    assert "SIMULATED ORDER RESERVED" not in failed_card
