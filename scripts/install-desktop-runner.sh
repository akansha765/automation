#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESKTOP_DIR="${DESKTOP_DIR:-$HOME/Desktop}"
APP_DIR="$DESKTOP_DIR/local-business-demo-automation"

mkdir -p "$APP_DIR/sample-data" "$APP_DIR/generated"
cp "$REPO_ROOT/scripts/run-demo-automation.py" "$APP_DIR/run-demo-automation.py"
cp "$REPO_ROOT/sample-data/leads.json" "$APP_DIR/sample-data/leads.json"

cat > "$APP_DIR/run-automation.sh" <<'RUNNER'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 run-demo-automation.py --leads sample-data/leads.json --output generated/demo-run
printf '\nAutomation completed. Outputs are in: %s\n' "$(pwd)/generated/demo-run"
RUNNER

cat > "$APP_DIR/README.txt" <<'README'
Local Business Demo Automation

Double-click or run ./run-automation.sh to generate demo artifacts from sample-data/leads.json.

Outputs are written to generated/demo-run/:
- demo JSON content
- one-page HTML preview
- outreach email preview
- manifest with cleanup timing
README

chmod 755 "$APP_DIR"
chmod +x "$APP_DIR/run-automation.sh" "$APP_DIR/run-demo-automation.py"

echo "Created executable desktop folder: $APP_DIR"
echo "Run it with: $APP_DIR/run-automation.sh"
