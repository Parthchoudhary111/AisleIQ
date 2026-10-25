import sys
import subprocess
import json
import httpx
import os

api_url = os.getenv("API_URL", "https://aisle-iq-api.onrender.com").rstrip("/")
stores = ["STORE_BLR_002", "STORE_MUM_076"]

print(f"[*] Target Cloud API: {api_url}")

for store in stores:
    print(f"\n[*] Generating realistic live events for {store}...")
    subprocess.run([sys.executable, "scripts/generate_test_events.py", store], check=True)
    file_path = f"data/sample_events_{store}.jsonl"

    with open(file_path, "r", encoding="utf-8") as f:
        events = [json.loads(line) for line in f if line.strip()]

    print(f"[*] Ingesting {len(events)} events for {store} into {api_url}/events/ingest...")
    batch_size = 50
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        resp = httpx.post(f"{api_url}/events/ingest", json={"events": batch}, timeout=25.0)
        data = resp.json()
        print(f"    [{store} Batch {i//batch_size + 1}] Status: {resp.status_code}, Accepted: {data.get('accepted', 0)}, Rejected: {data.get('rejected', 0)}")

print("\n[+] Done! Real-time telemetry and metrics successfully populated on the live cloud dashboard.")
