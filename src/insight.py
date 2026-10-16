import os, json, boto3
from decimal import Decimal
t = boto3.resource("dynamodb").Table(os.environ["STATE"])
def clean(o): return {k: (int(v) if isinstance(v, Decimal) else v) for k, v in o.items() if k != "pk"}
def handler(e, ctx):
    elder = (e.get("queryStringParameters") or {}).get("elder", "mom")
    body = clean(t.get_item(Key={"pk": f"insight#{elder}"}).get("Item") or {})
    ring = t.get_item(Key={"pk": "ring#latest"}).get("Item")
    if ring: body["ring"] = clean(ring)
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(body)}
