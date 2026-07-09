# Google Cloud Run Deployment

Use Cloud Run for the hosted demo. The Slack app needs a stable public HTTPS endpoint, and Cloud Run gives us that without running a server full-time.

## Important Credential Note

Do not put Google Cloud credentials in `.env`.

The app needs these runtime environment variables:

```text
OPENAI_API_KEY
OPENAI_MODEL
SLACK_BOT_TOKEN
SLACK_SIGNING_SECRET
GITHUB_OWNER
GITHUB_REPOS
GITHUB_TOKEN
TRAVEL_DATA_PATH
```

Google Cloud deployment credentials are different. Use one of these instead:

- Google Cloud Console in the browser
- `gcloud auth login`
- A service account key file stored outside the repo

For production-like setup, put sensitive app values in Secret Manager and expose them to Cloud Run as environment variables.

## Suggested Cloud Run Settings

```text
Service name: slack-gpt-agent-demo
Region: us-central1
Runtime: Dockerfile from this repository
Ingress: All
Authentication: Allow unauthenticated invocations
Port: 8080
```

Slack must be able to call `/slack/events`, so the service needs unauthenticated HTTPS access. Slack request signing still protects the endpoint.

## Environment Variables

Non-secret values can be plain Cloud Run environment variables:

```text
OPENAI_MODEL=gpt-5.6
GITHUB_OWNER=enschilling
GITHUB_REPOS=slack-gpt-agent-demo
TRAVEL_DATA_PATH=demo_travel.json
PORT=8080
```

Secret values should come from Secret Manager:

```text
OPENAI_API_KEY
SLACK_BOT_TOKEN
SLACK_SIGNING_SECRET
GITHUB_TOKEN
```

## Deploy With gcloud

After authenticating with Google Cloud:

```powershell
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com
gcloud run deploy slack-gpt-agent-demo --source . --region us-central1 --allow-unauthenticated
```

Then set runtime variables and secrets in the Cloud Run service configuration.

## Slack Callback URL

After deploy, Cloud Run gives you a URL like:

```text
https://slack-gpt-agent-demo-abc123-uc.a.run.app
```

Use this Slack Event Subscriptions request URL:

```text
https://YOUR_CLOUD_RUN_URL/slack/events
```

Then subscribe to:

```text
app_mention
message.im
```
