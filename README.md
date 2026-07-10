# Slack Agent Demo

A lightweight GPT-powered Slack agent that responds to `@mentions`, calls OpenAI, and can use simple tools for GitHub, weather, and simulated travel data.

This is intentionally small. The goal is to show the pattern: Slack is the chat surface, OpenAI is the reasoning layer, and tools connect the agent to useful systems.

## Recommended Workspace Flow

For ChatGPT Work/Desktop, use a Project when you want durable context, notes, and attached files grouped together. For this build, the cleaner flow is:

1. Keep this folder as the source project.
2. Open it in Codex Desktop when you want code navigation and iteration.
3. Push it to GitHub when you are ready for Google Cloud Run deployment.

Suggested repo name:

```text
slack-agent-demo
```

## What Works First

Milestone 1:

```text
@demo-agent hello
```

The bot responds in a Slack thread.

Milestone 2:

```text
@demo-agent summarize what changed in my GitHub repos this week
```

The bot uses the GitHub tool when `GITHUB_OWNER` and `GITHUB_REPOS` are configured.

Milestone 3:

```text
@demo-agent I'm traveling to Denver. What should I know?
```

The bot can combine demo travel data and weather.

## Local Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Fill in:

```text
OPENAI_API_KEY
SLACK_BOT_TOKEN
SLACK_SIGNING_SECRET
```

Optional GitHub settings:

```text
GITHUB_TOKEN
GITHUB_OWNER
GITHUB_REPOS
```

Run locally:

```powershell
python app.py
```

The app listens on:

```text
http://localhost:8080
```

For Slack local testing, expose it with a tunnel such as ngrok or Cloudflare Tunnel:

```text
https://your-tunnel-url/slack/events
```

## Slack App Setup

Create a Slack app at:

```text
https://api.slack.com/apps
```

Use these bot scopes:

```text
app_mentions:read
chat:write
im:history
im:read
im:write
```

Enable Event Subscriptions and set:

```text
Request URL: https://your-public-url/slack/events
```

Subscribe to bot events:

```text
app_mention
message.im
```

Install the app to your Slack workspace, then invite it to a test channel:

```text
/invite @demo-agent
```

## GitHub Tool

For public repositories, the GitHub summary tool may work without a token, but rate limits are lower. For private repositories or issue creation, create a GitHub token and set:

```text
GITHUB_TOKEN=...
GITHUB_OWNER=your-org-or-username
GITHUB_REPOS=repo-one,repo-two
```

The agent can:

- Summarize recent commits
- Summarize recent pull requests
- List recent open issues
- Create an issue when a token has permission

## Weather Tool

Weather uses Open-Meteo, which does not require an API key for this demo.

Example:

```text
@demo-agent What's the weather in Denver for the next 3 days?
```

## Demo Travel Tool

The travel tool reads the bundled month-specific demo files:

```text
demo_travel_july.json
demo_travel_august.json
```

This simulates an email or travel-confirmation integration without connecting to a real inbox. The tool can filter by destination or by month.

Examples:

```text
@demo-agent Check my July travel and tell me what to pack.
@demo-agent Check my August travel and tell me what to pack.
```

## Google Cloud Run Deployment

Detailed notes are in [docs/cloud-run.md](docs/cloud-run.md).

After pushing this folder to GitHub:

1. Open Google Cloud Run.
2. Create a service.
3. Choose continuous deployment from your GitHub repository.
4. Use the included `Dockerfile`.
5. Set environment variables or Secret Manager values for the same keys in `.env.example`.
6. Deploy and copy the Cloud Run HTTPS URL.
7. Update the Slack Request URL to:

```text
https://your-cloud-run-service.run.app/slack/events
```

## Notes

- The OpenAI model is controlled by `OPENAI_MODEL`.
- The default in this template follows current OpenAI docs examples, but you can swap in a cheaper or preferred model without changing the app code.
- Keep Slack and OpenAI secrets out of GitHub.
