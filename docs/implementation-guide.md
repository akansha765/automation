# Implementation Guide

## 1. Lead Intake

Configure Outscraper to send business records to the n8n webhook. The workflow expects each lead to include:

```json
{
  "businessName": "Example Bakery",
  "category": "Bakery",
  "phone": "+15551234567",
  "email": "owner@example.com",
  "address": "123 Main St, Austin, TX",
  "googleMapsUrl": "https://maps.google.com/...",
  "website": ""
}
```

The filter step should only continue when `website` is empty, null, or missing.

## 2. Research and Content Generation

The Claude research agent should produce structured JSON for the demo site. Keep all generated claims grounded in the source business profile and public listing details.

Recommended output shape:

```json
{
  "slug": "example-bakery-austin",
  "businessName": "Example Bakery",
  "headline": "Fresh baked goods in Austin",
  "description": "A concise description based on public listing information.",
  "services": ["Custom cakes", "Pastries", "Coffee"],
  "callToAction": "Call to place an order",
  "contact": {
    "phone": "+15551234567",
    "email": "owner@example.com",
    "address": "123 Main St, Austin, TX"
  }
}
```

## 3. Demo Site Generation

Use the generated JSON to create or update a page in the GitHub template site. A common pattern is:

1. Create a branch named `demo/<slug>`.
2. Write the JSON to `content/demos/<slug>.json`.
3. Commit the generated content.
4. Trigger a Vercel deployment for that branch.

## 4. Outreach Sequence

Send the first email only after Vercel returns a successful deployment URL.

Suggested email sequence:

- Initial email: live demo link, short explanation, clear opt-out.
- Follow-up #1 after 3 days: ask whether the demo is worth polishing.
- Follow-up #2 after 4 more days: final reminder before deleting the demo.

## 5. Cleanup

Wait 7 days after the second follow-up, then delete non-converting demo resources:

- Remove the Vercel deployment or alias.
- Delete the GitHub demo branch or generated content.
- Mark the lead as expired in your CRM or sheet.

## 6. Environment Variables

Configure these credentials in n8n:

| Variable | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | Research and demo content generation. |
| `GITHUB_TOKEN` | Create branches and commit generated demo JSON. |
| `GITHUB_OWNER` | GitHub organization or user that owns the template repository. |
| `GITHUB_REPO` | Template site repository name. |
| `VERCEL_TOKEN` | Create and inspect deployments. |
| `VERCEL_PROJECT_ID` | Vercel project used for demo deployments. |
| `RESEND_API_KEY` | Send outreach and follow-up emails. |
| `FROM_EMAIL` | Verified sender address for Resend. |

## 7. Conversion Safeguards

- Store every lead status transition so follow-ups are idempotent.
- Stop the wait chain immediately when a business replies, unsubscribes, or converts.
- Rate-limit deployment and email steps to avoid provider throttling.
- Add a manual review queue before launch if generated content is unverified.
