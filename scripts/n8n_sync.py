#!/usr/bin/env python3
"""
n8n Workflow Sync — Bidirectional sync between n8n instance and local JSON files.

Usage:
    python scripts/n8n_sync.py export          # Export all workflows from n8n to local files
    python scripts/n8n_sync.py export --id ID   # Export a specific workflow
    python scripts/n8n_sync.py import FILE      # Import a local JSON file to n8n
    python scripts/n8n_sync.py import --all     # Import all local JSON files to n8n
    python scripts/n8n_sync.py list             # List workflows in n8n
    python scripts/n8n_sync.py diff             # Show differences between n8n and local files
    python scripts/n8n_sync.py watch            # Watch for changes and sync (export mode)

Environment variables (or .env file):
    N8N_API_URL   — n8n instance URL (default: http://localhost:5678)
    N8N_API_KEY   — n8n API key (required)
    N8N_SYNC_DIR  — Local directory for workflow JSONs (default: workflows)
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def load_env():
    """Load .env file if it exists."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


load_env()

API_URL = os.environ.get("N8N_API_URL", "http://localhost:5678")
API_KEY = os.environ.get("N8N_API_KEY", "")
SYNC_DIR = os.environ.get("N8N_SYNC_DIR", "workflows")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SYNC_PATH = PROJECT_ROOT / SYNC_DIR


def get_headers():
    if not API_KEY:
        print("ERROR: N8N_API_KEY not set. Set it in .env or as an environment variable.")
        sys.exit(1)
    return {
        "X-N8N-API-KEY": API_KEY,
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def api_get(path: str, params: dict = None) -> dict:
    """GET request to n8n API."""
    url = f"{API_URL}/api/v1{path}"
    resp = requests.get(url, headers=get_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, data: dict) -> dict:
    """POST request to n8n API."""
    url = f"{API_URL}/api/v1{path}"
    resp = requests.post(url, headers=get_headers(), json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


def api_put(path: str, data: dict) -> dict:
    """PUT request to n8n API."""
    url = f"{API_URL}/api/v1{path}"
    resp = requests.put(url, headers=get_headers(), json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sanitize_filename(name: str) -> str:
    """Convert workflow name to a safe filename."""
    # Replace special chars with underscores, collapse multiples
    safe = re.sub(r'[^\w\s-]', '_', name)
    safe = re.sub(r'[\s_]+', '_', safe).strip('_')
    return safe[:100]  # Limit length


def detect_category(workflow: dict) -> str:
    """Detect category from workflow nodes (primary integration)."""
    nodes = workflow.get("nodes", [])
    for node in nodes:
        node_type = node.get("type", "")
        # Extract integration name from node type like "n8n-nodes-base.slack"
        if "." in node_type:
            integration = node_type.split(".")[-1]
            # Skip generic nodes
            if integration.lower() not in (
                "start", "set", "function", "if", "switch", "merge",
                "noop", "noOp", "stickyNote", "manualTrigger",
                "executeWorkflowTrigger", "executeWorkflow",
                "httpRequest", "code", "manualChat",
            ):
                return integration.capitalize()
    return "General"


def workflow_hash(workflow: dict) -> str:
    """Compute hash of workflow content for change detection."""
    # Hash only the meaningful parts (exclude metadata that changes on every save)
    content = {
        "name": workflow.get("name"),
        "nodes": workflow.get("nodes", []),
        "connections": workflow.get("connections", {}),
        "settings": workflow.get("settings", {}),
    }
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()[:16]


def get_all_workflows() -> list:
    """Fetch all workflows from n8n, handling pagination."""
    workflows = []
    cursor = None
    while True:
        params = {"limit": 100}
        if cursor:
            params["cursor"] = cursor
        data = api_get("/workflows", params=params)
        workflows.extend(data.get("data", []))
        next_cursor = data.get("nextCursor")
        if not next_cursor:
            break
        cursor = next_cursor
    return workflows


def get_workflow_detail(workflow_id: str) -> dict:
    """Fetch a single workflow with full details."""
    return api_get(f"/workflows/{workflow_id}")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_list():
    """List all workflows in n8n."""
    workflows = get_all_workflows()
    if not workflows:
        print("No workflows found in n8n.")
        return

    print(f"\n{'ID':<25} {'Name':<50} {'Active':<8} {'Nodes'}")
    print("-" * 100)
    for wf in workflows:
        node_count = len(wf.get("nodes", []))
        active = "✅" if wf.get("active") else "⬜"
        print(f"{wf['id']:<25} {wf['name'][:50]:<50} {active:<8} {node_count}")
    print(f"\nTotal: {len(workflows)} workflows")


def cmd_export(workflow_id: Optional[str] = None):
    """Export workflows from n8n to local JSON files."""
    if workflow_id:
        workflows = [get_workflow_detail(workflow_id)]
    else:
        # Get list first, then fetch full details
        workflow_list = get_all_workflows()
        workflows = []
        for wf in workflow_list:
            detail = get_workflow_detail(wf["id"])
            workflows.append(detail)

    exported = 0
    skipped = 0
    for wf in workflows:
        category = detect_category(wf)
        category_dir = SYNC_PATH / category
        category_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{sanitize_filename(wf['name'])}.json"
        filepath = category_dir / filename

        # Check if file already exists with same content
        if filepath.exists():
            existing = json.loads(filepath.read_text(encoding="utf-8"))
            if workflow_hash(existing) == workflow_hash(wf):
                skipped += 1
                continue

        # Write workflow JSON (pretty-printed)
        filepath.write_text(
            json.dumps(wf, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        exported += 1
        print(f"  ✅ {category}/{filename}")

    print(f"\nExported: {exported}, Skipped (unchanged): {skipped}")


def cmd_import(filepath: Optional[str] = None, import_all: bool = False):
    """Import local JSON files to n8n."""
    if import_all:
        files = list(SYNC_PATH.rglob("*.json"))
    elif filepath:
        files = [Path(filepath)]
    else:
        print("ERROR: Specify a file path or use --all")
        return

    existing_workflows = {wf["name"]: wf for wf in get_all_workflows()}
    imported = 0
    updated = 0
    errors = 0

    for f in files:
        try:
            wf_data = json.loads(f.read_text(encoding="utf-8"))
            name = wf_data.get("name", f.stem)

            # Prepare workflow data for n8n API
            payload = {
                "name": name,
                "nodes": wf_data.get("nodes", []),
                "connections": wf_data.get("connections", {}),
                "settings": wf_data.get("settings", {}),
            }

            if name in existing_workflows:
                # Update existing workflow
                wf_id = existing_workflows[name]["id"]
                api_put(f"/workflows/{wf_id}", payload)
                updated += 1
                print(f"  🔄 Updated: {name} (id:{wf_id})")
            else:
                # Create new workflow
                result = api_post("/workflows", payload)
                imported += 1
                print(f"  ✅ Created: {name} (id:{result.get('id', '?')})")

        except Exception as e:
            errors += 1
            print(f"  ❌ Error with {f}: {e}")

    print(f"\nCreated: {imported}, Updated: {updated}, Errors: {errors}")


def cmd_diff():
    """Show differences between n8n instance and local files."""
    remote_workflows = {wf["name"]: wf for wf in get_all_workflows()}
    local_files = {}

    for f in SYNC_PATH.rglob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            name = data.get("name", f.stem)
            local_files[name] = {"path": f, "data": data}
        except (json.JSONDecodeError, OSError):
            continue

    # Find differences
    only_remote = set(remote_workflows.keys()) - set(local_files.keys())
    only_local = set(local_files.keys()) - set(remote_workflows.keys())
    common = set(remote_workflows.keys()) & set(local_files.keys())

    modified = []
    for name in common:
        remote_hash = workflow_hash(remote_workflows[name])
        local_hash = workflow_hash(local_files[name]["data"])
        if remote_hash != local_hash:
            modified.append(name)

    print(f"\n📊 Sync Status: n8n ({API_URL}) ↔ {SYNC_PATH}")
    print("=" * 60)

    if only_remote:
        print(f"\n🔵 Only in n8n ({len(only_remote)}):")
        for name in sorted(only_remote):
            print(f"  - {name}")

    if only_local:
        print(f"\n🟢 Only local ({len(only_local)}):")
        for name in sorted(only_local):
            print(f"  - {name} ({local_files[name]['path'].relative_to(PROJECT_ROOT)})")

    if modified:
        print(f"\n🟡 Modified ({len(modified)}):")
        for name in sorted(modified):
            print(f"  - {name}")

    in_sync = len(common) - len(modified)
    if in_sync > 0:
        print(f"\n✅ In sync: {in_sync}")

    if not only_remote and not only_local and not modified:
        print("\n✅ Everything is in sync!")


def cmd_watch(interval: int = 10):
    """Watch n8n for changes and export them."""
    print(f"👁  Watching n8n at {API_URL} every {interval}s... (Ctrl+C to stop)")
    known_hashes = {}

    # Initial snapshot
    for wf in get_all_workflows():
        detail = get_workflow_detail(wf["id"])
        known_hashes[wf["id"]] = workflow_hash(detail)

    try:
        while True:
            time.sleep(interval)
            current_workflows = get_all_workflows()

            for wf in current_workflows:
                detail = get_workflow_detail(wf["id"])
                current_hash = workflow_hash(detail)

                if wf["id"] not in known_hashes:
                    print(f"\n🆕 New workflow detected: {wf['name']}")
                    cmd_export(wf["id"])
                    known_hashes[wf["id"]] = current_hash
                elif known_hashes[wf["id"]] != current_hash:
                    print(f"\n🔄 Change detected: {wf['name']}")
                    cmd_export(wf["id"])
                    known_hashes[wf["id"]] = current_hash

    except KeyboardInterrupt:
        print("\n\n⏹  Watch stopped.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="n8n Workflow Sync — Bidirectional sync with local JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # list
    subparsers.add_parser("list", help="List all workflows in n8n")

    # export
    export_parser = subparsers.add_parser("export", help="Export workflows from n8n to local files")
    export_parser.add_argument("--id", help="Export a specific workflow by ID")

    # import
    import_parser = subparsers.add_parser("import", help="Import local JSON files to n8n")
    import_parser.add_argument("file", nargs="?", help="Path to JSON file to import")
    import_parser.add_argument("--all", action="store_true", help="Import all local JSON files")

    # diff
    subparsers.add_parser("diff", help="Show differences between n8n and local files")

    # watch
    watch_parser = subparsers.add_parser("watch", help="Watch for changes and auto-export")
    watch_parser.add_argument("--interval", type=int, default=10, help="Poll interval in seconds")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "list":
            cmd_list()
        elif args.command == "export":
            cmd_export(args.id)
        elif args.command == "import":
            cmd_import(args.file, args.all)
        elif args.command == "diff":
            cmd_diff()
        elif args.command == "watch":
            cmd_watch(args.interval)
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Cannot connect to n8n at {API_URL}. Is n8n running?")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: API request failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
