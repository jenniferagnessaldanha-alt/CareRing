import os, json, boto3
from decimal import Decimal
t = boto3.resource("dynamodb").Table(os.environ["STATE"])
def handler(e, ctx):
    elder = (e.get("queryStringParameters") or {}).get("elder", "mom")
    it = t.get_item(Key={"pk": f"insight#{elder}"}).get("Item") or {}
    body = {k: (int(v) if isinstance(v, Decimal) else v) for k, v in it.items() if k != "pk"}
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(body)}