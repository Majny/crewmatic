"""Built-in integration catalog — maps friendly names to MCP server configs."""

import logging

logger = logging.getLogger(__name__)

# Each integration defines:
# - name: Human-friendly display name
# - description: What it does (shown in wizard)
# - command: MCP server command
# - args: MCP server args
# - env_vars: Required environment variables (user must set these)
# - setup_hint: Short instruction for getting credentials
# - auto_roles: Agent roles that get this integration by default
# - keywords: Used by the wizard to match user descriptions to integrations

CATALOG = {
    "gmail": {
        "name": "Gmail",
        "description": "Send and read emails, draft outreach, manage inbox",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-gmail"],
        "env_vars": ["GMAIL_OAUTH_CREDENTIALS"],
        "setup_hint": "Follow: https://developers.google.com/gmail/api/quickstart/python",
        "auto_roles": ["leader"],
        "keywords": ["email", "outreach", "mail", "cold email", "inbox", "send email"],
    },
    "google-calendar": {
        "name": "Google Calendar",
        "description": "Schedule meetings, check availability, manage events",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-google-calendar"],
        "env_vars": ["GOOGLE_CALENDAR_CREDENTIALS"],
        "setup_hint": "Follow: https://developers.google.com/calendar/api/quickstart/python",
        "auto_roles": ["leader"],
        "keywords": ["calendar", "meeting", "schedule", "booking", "availability"],
    },
    "github": {
        "name": "GitHub",
        "description": "Create issues, review PRs, manage repositories",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env_vars": ["GITHUB_TOKEN"],
        "setup_hint": "Create a Personal Access Token at https://github.com/settings/tokens",
        "auto_roles": [],
        "keywords": ["github", "git", "repository", "pull request", "issues", "code review"],
    },
    "notion": {
        "name": "Notion",
        "description": "Read and write Notion pages, manage databases",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-notion"],
        "env_vars": ["NOTION_TOKEN"],
        "setup_hint": "Create an integration at https://www.notion.so/my-integrations",
        "auto_roles": [],
        "keywords": ["notion", "wiki", "documentation", "knowledge base", "notes"],
    },
    "slack": {
        "name": "Slack (extended)",
        "description": "Search messages, read channels beyond the bot's default access",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-slack"],
        "env_vars": ["SLACK_BOT_TOKEN"],
        "setup_hint": "Uses the same SLACK_BOT_TOKEN — no extra setup needed",
        "auto_roles": [],
        "keywords": ["slack", "messages", "search slack", "channels"],
    },
    "linear": {
        "name": "Linear",
        "description": "Create and manage issues, track project progress",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-linear"],
        "env_vars": ["LINEAR_API_KEY"],
        "setup_hint": "Get API key from Linear settings → API",
        "auto_roles": [],
        "keywords": ["linear", "issues", "project management", "tickets", "sprints"],
    },
    "google-drive": {
        "name": "Google Drive",
        "description": "Read and search files in Google Drive",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-google-drive"],
        "env_vars": ["GOOGLE_DRIVE_CREDENTIALS"],
        "setup_hint": "Follow: https://developers.google.com/drive/api/quickstart/python",
        "auto_roles": [],
        "keywords": ["drive", "google drive", "files", "documents", "sheets", "spreadsheet"],
    },
    "postgres": {
        "name": "PostgreSQL",
        "description": "Query and manage PostgreSQL databases",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-postgres"],
        "env_vars": ["POSTGRES_URL"],
        "setup_hint": "Set POSTGRES_URL to your connection string: postgresql://user:pass@host/db",
        "auto_roles": [],
        "keywords": ["postgres", "database", "sql", "db", "query"],
    },
    "hubspot": {
        "name": "HubSpot",
        "description": "Manage contacts, deals, and CRM data",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-hubspot"],
        "env_vars": ["HUBSPOT_ACCESS_TOKEN"],
        "setup_hint": "Get access token from HubSpot developer portal",
        "auto_roles": [],
        "keywords": ["hubspot", "crm", "contacts", "deals", "sales", "pipeline"],
    },
}


def get_integration(name: str) -> dict | None:
    """Look up an integration by name. Returns None if not found."""
    return CATALOG.get(name)


def list_integrations() -> list[dict]:
    """Return all available integrations as a list with keys included."""
    result = []
    for key, integration in CATALOG.items():
        result.append({"key": key, **integration})
    return result


def build_mcp_config_for_integrations(integration_names: list[str]) -> dict:
    """Build a Claude CLI MCP config dict for a list of integration names.

    Returns dict in the format: {"mcpServers": {"name": {"command": ..., "args": ..., "env": ...}}}
    """
    servers = {}
    for name in integration_names:
        integration = CATALOG.get(name)
        if not integration:
            logger.warning(f"Unknown integration: {name}")
            continue
        server = {
            "command": integration["command"],
            "args": integration["args"],
        }
        # Build env dict from env_vars — use os.environ values
        import os

        env = {}
        for var in integration.get("env_vars", []):
            val = os.environ.get(var, "")
            if val:
                env[var] = val
        if env:
            server["env"] = env
        servers[name] = server
    return {"mcpServers": servers}


def resolve_integrations_for_agent(
    agent_role: str,
    agent_integrations: list[str] | None,
    global_integrations: list[str],
) -> list[str]:
    """Determine which integrations an agent should have.

    Priority:
    1. If agent has explicit integrations: list, use that
    2. Otherwise, auto-assign based on role + what's globally enabled
    """
    if agent_integrations is not None:
        return agent_integrations

    # Auto-assign: intersection of global integrations and role defaults
    result = []
    for name in global_integrations:
        integration = CATALOG.get(name)
        if not integration:
            continue
        if agent_role in integration.get("auto_roles", []):
            result.append(name)
    return result


def check_integration_credentials(integration_names: list[str]) -> list[tuple[str, str, bool]]:
    """Check which integrations have their required env vars set.

    Returns list of (integration_name, env_var, is_set) tuples.
    """
    import os

    results = []
    for name in integration_names:
        integration = CATALOG.get(name)
        if not integration:
            continue
        for var in integration.get("env_vars", []):
            is_set = bool(os.environ.get(var, ""))
            results.append((name, var, is_set))
    return results


def match_integrations_from_description(description: str) -> list[str]:
    """Match integrations based on keywords in a business description.

    Used by the setup wizard to suggest integrations.
    """
    description_lower = description.lower()
    matches = []
    for key, integration in CATALOG.items():
        for keyword in integration.get("keywords", []):
            if keyword in description_lower:
                if key not in matches:
                    matches.append(key)
                break
    return matches
