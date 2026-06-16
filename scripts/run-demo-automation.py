#!/usr/bin/env python3
"""Run a local dry-run of the local business demo funnel.

This script intentionally avoids external API calls. It executes the same business
logic as the n8n blueprint with deterministic local outputs so the automation can
be tested without Outscraper, Anthropic, GitHub, Vercel, or Resend credentials.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DemoResult:
    slug: str
    business_name: str
    demo_url: str
    content_path: Path
    html_path: Path
    email_path: Path
    cleanup_at: str


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "business-demo"


def has_no_website(lead: dict[str, Any]) -> bool:
    website = lead.get("website")
    return website is None or str(website).strip() == ""


def generate_content(lead: dict[str, Any]) -> dict[str, Any]:
    business_name = str(lead.get("businessName", "Local Business")).strip()
    category = str(lead.get("category", "local service")).strip().lower()
    city = extract_city(str(lead.get("address", "your area")))
    slug = slugify(f"{business_name}-{city}")

    return {
        "slug": slug,
        "businessName": business_name,
        "headline": f"A modern website demo for {business_name}",
        "description": f"A simple one-page demo designed to help customers find and contact this {category} in {city}.",
        "services": default_services(category),
        "callToAction": "Call today or request a quote",
        "contact": {
            "phone": lead.get("phone", ""),
            "email": lead.get("email", ""),
            "address": lead.get("address", ""),
            "googleMapsUrl": lead.get("googleMapsUrl", ""),
        },
        "source": "local dry-run from sample lead data",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }


def extract_city(address: str) -> str:
    parts = [part.strip() for part in address.split(",") if part.strip()]
    return parts[1].split()[0] if len(parts) > 1 else "local"


def default_services(category: str) -> list[str]:
    service_map = {
        "bakery": ["Fresh pastries", "Custom orders", "Coffee and treats"],
        "restaurant": ["Menu highlights", "Online reservations", "Catering inquiries"],
        "plumber": ["Emergency repairs", "Drain cleaning", "Fixture installation"],
    }
    return service_map.get(category, ["Local service", "Fast contact", "Customer-friendly experience"])


def render_html(content: dict[str, Any]) -> str:
    contact = content["contact"]
    services = "".join(f"<li>{escape(service)}</li>" for service in content["services"])
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{escape(content['businessName'])} Website Demo</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f7f7fb; }}
    main {{ max-width: 880px; margin: 48px auto; padding: 32px; background: white; border-radius: 24px; box-shadow: 0 16px 40px rgba(23, 32, 51, 0.12); }}
    h1 {{ font-size: clamp(2rem, 5vw, 4rem); margin: 0 0 16px; }}
    p {{ font-size: 1.1rem; line-height: 1.6; }}
    .cta {{ display: inline-block; margin-top: 18px; padding: 14px 20px; border-radius: 999px; background: #315cff; color: white; text-decoration: none; font-weight: 700; }}
    ul {{ display: grid; gap: 12px; padding-left: 20px; }}
    footer {{ margin-top: 32px; color: #596275; }}
  </style>
</head>
<body>
  <main>
    <p>Website demo</p>
    <h1>{escape(content['headline'])}</h1>
    <p>{escape(content['description'])}</p>
    <h2>Featured services</h2>
    <ul>{services}</ul>
    <a class=\"cta\" href=\"tel:{escape(str(contact['phone']))}\">{escape(content['callToAction'])}</a>
    <footer>
      <strong>{escape(content['businessName'])}</strong><br>
      {escape(str(contact['address']))}<br>
      {escape(str(contact['phone']))} · {escape(str(contact['email']))}
    </footer>
  </main>
</body>
</html>
"""


def render_email(content: dict[str, Any], demo_url: str) -> str:
    return f"""Subject: I made a quick website demo for {content['businessName']}

Hi {content['businessName']} team,

I noticed your public listing does not include a website, so I mocked up a quick one-page demo:
{demo_url}

If you like the direction, reply and I can polish it, connect a domain, and launch it properly.

If this is not relevant, reply stop and I will not follow up.
"""


def run(leads_path: Path, output_dir: Path, demo_base_url: str) -> list[DemoResult]:
    leads = json.loads(leads_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[DemoResult] = []

    for lead in leads:
        if not has_no_website(lead):
            continue

        content = generate_content(lead)
        slug = content["slug"]
        demo_url = f"{demo_base_url.rstrip('/')}/{slug}"
        cleanup_at = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()

        content_path = output_dir / f"{slug}.json"
        html_path = output_dir / f"{slug}.html"
        email_path = output_dir / f"{slug}.email.txt"

        content_path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")
        html_path.write_text(render_html(content), encoding="utf-8")
        email_path.write_text(render_email(content, demo_url), encoding="utf-8")

        results.append(
            DemoResult(
                slug=slug,
                business_name=content["businessName"],
                demo_url=demo_url,
                content_path=content_path,
                html_path=html_path,
                email_path=email_path,
                cleanup_at=cleanup_at,
            )
        )

    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "input": str(leads_path),
        "generatedCount": len(results),
        "results": [result.__dict__ | {
            "content_path": str(result.content_path),
            "html_path": str(result.html_path),
            "email_path": str(result.email_path),
        } for result in results],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local dry-run of the demo funnel automation.")
    parser.add_argument("--leads", type=Path, default=Path("sample-data/leads.json"), help="Path to Outscraper-style lead JSON.")
    parser.add_argument("--output", type=Path, default=Path("generated/demo-run"), help="Directory for generated demo artifacts.")
    parser.add_argument("--demo-base-url", default="https://demo.example.com", help="Base URL used in generated outreach email previews.")
    args = parser.parse_args()

    results = run(args.leads, args.output, args.demo_base_url)
    print(f"Generated {len(results)} demo(s) from leads without websites.")
    for result in results:
        print(f"- {result.business_name}: {result.demo_url}")
        print(f"  content: {result.content_path}")
        print(f"  html:    {result.html_path}")
        print(f"  email:   {result.email_path}")
        print(f"  cleanup: {result.cleanup_at}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
