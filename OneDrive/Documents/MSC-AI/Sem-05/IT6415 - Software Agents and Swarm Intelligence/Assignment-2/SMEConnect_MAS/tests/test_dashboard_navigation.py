"""Phase 06 dashboard navigation and structural smoke checks.

These checks do not claim browser-level visual verification.
"""
import ast
from pathlib import Path

from dashboard.ui_design import PAGE_METADATA, PAGES, navigate_to


PROJECT = Path(__file__).resolve().parents[1]


def test_all_workspaces_have_distinct_navigation_names_and_descriptions():
    assert len(PAGES) == 9
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
    for group in ("WORKSPACE", "AGENT WORKFLOWS", "LEARNING LABS"):
        assert group in theme
    assert '.smc-menu-group' in theme
    assert 'smc_nav_' in theme
