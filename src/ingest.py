"""Ring Partner API webhook receiver (v1.1 motion events).
Verifies X-Signature (sha256=<hex HMAC-SHA256 over raw body>), dedupes by event id,
maps Ring device -> room, stores the event for the baseline engine."""
import os, json, hmac, hashlib, time, base64, boto3
from botocore.exceptions import ClientError
ddb = boto3.resource("dynamodb")
ev = ddb.Table(os.environ["EVENTS"]); st = ddb.Table(os.environ["STATE"])
KEY = os.environ["RING_HMAC_KEY"].encode(); ROOMS = json.loads(os.environ["DEVICE_ROOMS"])
def resp(code, msg): return {"statusCode": code, "body": msg}
def handler(e, ctx):
    raw = e.get("body") or ""
    raw_b = base64.b64decode(raw) if e.get("isBase64Encoded") else raw.encode()
    hdr = {k.lower(): v for k, v in (e.get("headers") or {}).items()}
    good = "sha256=" + hmac.new(KEY, raw_b, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(hdr.get("x-signature", ""), good): return resp(401, "bad signature")
    p = json.loads(raw_b); d = p.get("data") or {}; a = d.get("attributes") or {}
    if a.get("type", "motion_detected") != "motion_detected": return resp(200, "ignored")
    eid = d.get("id") or (p.get("meta") or {}).get("request_id"); device = a.get("source", "unknown")
    sub = a.get("subType") or a.get("sub_type") or d.get("subType") or "unknown"
    now = int(time.time()); ts = int(a.get("timestamp", now * 1000) / 1000)
    try: st.put_item(Item={"pk": f"seen#{eid}", "ttl": now + 86400}, ConditionExpression="attribute_not_exists(pk)")
    except ClientError as ex:
        if ex.response["Error"]["Code"] == "ConditionalCheckFailedException": return resp(200, "duplicate")
        raise
    room = ROOMS.get(device, "unmapped")
    if room == "kitchen" and (ts % 86400) / 60 <= 300: room = "kitchen_night"
    ev.put_item(Item={"pk": "mom", "sk": f"{ts:012d}#{room}#{eid}", "ts": ts, "room": room, "device": device, "sub_type": sub, "source": "ring", "ttl": ts + 40 * 86400})
    st.put_item(Item={"pk": "ring#latest", "device": device, "room": room, "event_type": "motion_detected", "sub_type": sub,
                      "event_id": eid, "verified": True, "received": now, "latency_ms": max(0, (now - ts) * 1000)})
    return resp(200, "ok")
