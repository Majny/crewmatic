"""LLM prompt templates for the Slack onboarding setup wizard."""

WELCOME_MESSAGE = (
    "Hi there! I'm your Crewmatic setup assistant.\n\n"
    "It looks like you don't have a crew configured yet. "
    "I'll help you set up your AI team right here in Slack.\n\n"
    "Tell me about your business and what you want your AI team to do. "
    "Write in any language — I'll respond in yours."
)

FOLLOWUP_PROMPT = """\
The user described their business and goals for an AI team:

{business_description}

Ask 2-3 concise follow-up questions to fill in the gaps before you can \
design their AI crew. Focus on:
- Tech stack and tools they use (languages, frameworks, hosting)
- Specific roles or workflows they need automated
- Existing codebases or repositories the team should work with
- Preferred communication style (formal reports vs casual updates)

Keep it conversational and friendly. Do NOT generate any YAML yet.
Respond in the same language as the user."""

CREW_GENERATION_PROMPT = """\
Based on the following business description and technical details, generate a \
complete crew.yaml configuration for the user's AI team.

Business description:
{business_description}

Technical details:
{tech_details}

Output ONLY valid YAML (no markdown fences, no explanation). Follow these rules exactly:

1. Start with:
   name: "<company or team name inferred from description>"
   slack:
     app_token: ${{SLACK_APP_TOKEN}}
     bot_token: ${{SLACK_BOT_TOKEN}}
   owner:
     slack_id: ${{OWNER_SLACK_ID}}

2. Include a settings: section with sensible defaults.

3. Include data_dir: "./data", memory_dir: "./memory", context_dir: "./context".

4. Include a git: section with author_name and author_email based on the business.

5. Under agents: define the team. Rules:
   - There MUST be exactly one agent with role: leader.
   - Every worker and manager MUST have a reports_to field referencing another agent name.
   - The leader does NOT have reports_to.
   - Channel names must be lowercase, alphanumeric and hyphens only, max 80 chars.
   - delegates_to lists must reference actual agent names defined in the config.
   - Use model: "opus" for the leader and any managers.
   - Use model: "sonnet" for workers.
   - Each agent needs: channel, model, role, system_prompt, tools.
   - System prompts must be specific to this business — not generic placeholders.
   - Available tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch, WebSearch
   - Give the leader and managers: "Read,Write,Edit,WebFetch,WebSearch,Glob,Grep"
   - Give technical workers: "Read,Glob,Grep,Bash,Edit,Write,WebFetch,WebSearch"
   - Give non-technical workers: "Read,Write,Edit,WebFetch,WebSearch,Glob,Grep"

6. If the user mentioned a codebase or repository, include a projects: section:
   projects:
     <project-key>:
       name: "<project name>"
       description: "<what the project is>"
       codebase: "."
       context: |
         <brief project context>

7. If the user selected integrations, include them in the config:
   integrations:
     - gmail
     - github

   Auto-assign integrations to agents based on their role:
   - Leaders/managers get: gmail, google-calendar (if enabled)
   - Marketing/sales workers get: gmail, hubspot, notion (if enabled)
   - Technical workers get: github, linear (if enabled)
   - Override with per-agent integrations: [list] when appropriate

   Available integrations: {available_integrations}
   User selected: {selected_integrations}

Output ONLY the YAML. No commentary, no fences."""

ADD_AGENT_PROMPT = """\
The user wants to add a new agent to their existing crew.

User request:
{request}

Existing agents (YAML):
{existing_agents_yaml}

Generate ONLY a single new agent YAML block that can be inserted under the \
agents: key. The block must:
- Have a unique name not already in use
- Include: channel, model, role, system_prompt, tools, reports_to
- Channel name: lowercase, alphanumeric + hyphens only, max 80 chars
- delegates_to must only reference agents that already exist (or the new agent itself)
- Use model "opus" for leader/manager, "sonnet" for worker
- System prompt specific to the request

Output ONLY the YAML block (agent_name: followed by its config). No fences, no explanation."""

MODIFY_AGENT_PROMPT = """\
The user wants to modify an existing agent's system prompt.

User request:
{request}

Agent name: {agent_name}

Current system prompt:
{current_prompt}

Generate ONLY the updated system_prompt value (the text itself, not the YAML key). \
Incorporate the user's requested changes while keeping the prompt well-structured \
and specific. No fences, no explanation."""
