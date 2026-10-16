"""Send a signed Ring-style v1.1 motion webhook to your Ingest URL.
  python tools/send_ring_event.py <IngestUrl> --device cam-kitchen --sub human [--dup] [--key demo-hmac-key]
For a fuller emulator see the community project `ring-sandbox` (pip install ring-sandbox)."""
import argparse, hmac, hashlib, json, time, uuid, urllib.request
from datetime import datetime, timezone
ap = argparse.ArgumentParser(); ap.add_argument("url"); ap.add_argument("--device", default="cam-kitchen")
ap.add_argument("--sub", default="human"); ap.add_argument("--key", default="demo-hmac-key"); ap.add_argument("--dup", action="store_true")
a = ap.parse_args(); ms = int(time.time() * 1000)
body = json.dumps({"version": "1.1", "meta": {"account_id": "ava1.ring.account.DEMO", "request_id": str(uuid.uuid4()), "time": datetime.now(timezone.utc).isoformat()},
  "data": {"id": f"{a.device}_{a.sub}_{ms}", "type": "events", "attributes": {"type": "motion_detected", "subType": a.sub, "source": a.device, "timestamp": ms}}}).encode()
sig = "sha256=" + hmac.new(a.key.encode(), body, hashlib.sha256).hexdigest()
for _ in range(2 if a.dup else 1):
    r = urllib.request.Request(a.url, body, {"Content-Type": "application/json", "X-Signature": sig})
    try: print(urllib.request.urlopen(r).read().decode())
    except urllib.error.HTTPError as e: print(e.code, e.read().decode())
