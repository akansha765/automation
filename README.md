# Local Business Demo Funnel Automation

This repository contains a production-ready blueprint for an outbound automation that finds local businesses without websites, generates personalized demo sites, deploys them, emails the owners, follows up, and removes stale demos.

## Funnel Overview

```text
Outscraper
↓
n8n Webhook
↓
Filter businesses without websites
↓
Claude Research Agent
↓
Generate JSON content
↓
GitHub Template Site
↓
Vercel Deploy
↓
Resend Email
↓
Wait 3 Days
↓
Follow-up #1
↓
Wait 4 Days
↓
Follow-up #2
↓
Wait 7 Days
↓
Delete Demo Site
```

## Goal

1. Find businesses that do not currently list a website.
2. Generate a simple, personalized website demo from public business information.
3. Deploy the demo to a temporary Vercel URL.
4. Email the business a live demo link with a clear call to action.
5. Send two follow-ups to non-responders.
6. Delete demos that do not convert after the follow-up window.

## Repository Structure

- `workflows/local-business-demo-funnel.json` — importable n8n workflow skeleton with named nodes and integration placeholders.
- `docs/implementation-guide.md` — setup checklist, environment variables, payload contracts, and conversion safeguards.

## Required Services

- **Outscraper** for lead sourcing.
- **n8n** for orchestration.
- **Anthropic Claude** or an equivalent research/content agent.
- **GitHub** for committing generated demo content into a template site.
- **Vercel** for temporary demo deployment.
- **Resend** for outreach and follow-up email delivery.

## Compliance Notes

- Only contact businesses where you have a lawful basis to send outreach.
- Include unsubscribe/opt-out handling in every email.
- Avoid implying an existing business relationship.
- Keep generated copy factual and easy to correct.
- Delete demo deployments after the configured expiration window unless the business opts in.

## Run a Local Dry-Run

Run the automation locally without external API credentials:

```bash
python scripts/run-demo-automation.py
```

The dry-run reads `sample-data/leads.json`, filters out businesses that already have websites, generates demo JSON, renders a one-page HTML preview, writes an outreach email preview, and stores a manifest in `generated/demo-run/`.
