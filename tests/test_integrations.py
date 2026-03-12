"""Tests for crewmatic.integrations — integration catalog and helpers."""

from crewmatic.integrations import (
    get_integration, list_integrations, CATALOG,
    resolve_integrations_for_agent, match_integrations_from_description,
    build_mcp_config_for_integrations, check_integration_credentials,
)


def test_catalog_not_empty():
    assert len(CATALOG) > 0


def test_get_known_integration():
    gmail = get_integration("gmail")
    assert gmail is not None
    assert gmail["name"] == "Gmail"
    assert "command" in gmail


def test_get_unknown_integration():
    assert get_integration("nonexistent") is None


def test_list_integrations_has_keys():
    items = list_integrations()
    assert len(items) > 0
    assert all("key" in item for item in items)
    assert all("name" in item for item in items)


def test_list_integrations_count_matches_catalog():
    items = list_integrations()
    assert len(items) == len(CATALOG)


def test_resolve_explicit_override():
    """Agent with explicit integrations ignores auto-assignment."""
    result = resolve_integrations_for_agent("worker", ["github"], ["gmail", "github"])
    assert result == ["github"]


def test_resolve_auto_assignment():
    """Agent without explicit integrations gets role-based defaults."""
    result = resolve_integrations_for_agent("leader", None, ["gmail", "github"])
    assert "gmail" in result


def test_resolve_auto_assignment_no_match():
    """Agent role that doesn't match any auto_roles gets nothing."""
    result = resolve_integrations_for_agent("worker", None, ["gmail", "github"])
    # gmail auto_roles=["leader"], github auto_roles=[]
    assert result == []


def test_resolve_no_integrations():
    result = resolve_integrations_for_agent("worker", None, [])
    assert result == []


def test_resolve_explicit_empty_list():
    """Explicitly setting empty list means no integrations."""
    result = resolve_integrations_for_agent("leader", [], ["gmail"])
    assert result == []


def test_match_from_description_email():
    matches = match_integrations_from_description("I need to send cold emails to prospects")
    assert "gmail" in matches


def test_match_from_description_github():
    matches = match_integrations_from_description("We have a GitHub repository")
    assert "github" in matches


def test_match_from_description_multiple():
    matches = match_integrations_from_description("We use GitHub for code and Notion for docs")
    assert "github" in matches
    assert "notion" in matches


def test_match_no_keywords():
    matches = match_integrations_from_description("I sell handmade jewelry at craft fairs")
    assert isinstance(matches, list)


def test_build_mcp_config():
    config = build_mcp_config_for_integrations(["gmail"])
    assert "mcpServers" in config
    assert "gmail" in config["mcpServers"]
    assert "command" in config["mcpServers"]["gmail"]
    assert "args" in config["mcpServers"]["gmail"]


def test_build_mcp_config_unknown():
    config = build_mcp_config_for_integrations(["nonexistent"])
    assert config["mcpServers"] == {}


def test_build_mcp_config_empty():
    config = build_mcp_config_for_integrations([])
    assert config["mcpServers"] == {}


def test_check_integration_credentials_unknown():
    results = check_integration_credentials(["nonexistent"])
    assert results == []


def test_check_integration_credentials_structure():
    results = check_integration_credentials(["gmail"])
    assert len(results) > 0
    name, var, is_set = results[0]
    assert name == "gmail"
    assert var == "GMAIL_OAUTH_CREDENTIALS"
    assert isinstance(is_set, bool)
