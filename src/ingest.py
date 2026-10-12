
"""Webhook target for RingGuard / Ring motion events. Body: {"elder","room","ts"}"""
import os, json, time, boto3
t = boto3.resource("dynamodb").Table(os.environ["EVENTS"])
def handler(event, ctx):
    e = json.loads(event.get("body") or "{}"); ts = int(e.get("ts", time.time()))
    t.put_item(Item={"pk": e.get("elder", "mom"), "sk": f"{ts:012d}#{e['room']}", "ts": ts, "room": e["room"], "ttl": ts + 40 * 86400})
    return {"statusCode": 200, "body": "ok"}
