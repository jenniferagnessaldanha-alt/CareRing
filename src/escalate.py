import os, boto3
state = boto3.resource("dynamodb").Table(os.environ["STATE"]); sns = boto3.client("sns")
def handler(e, ctx):
    if "requestContext" in e:
        elder = (e.get("queryStringParameters") or {}).get("elder", "mom")
        state.update_item(Key={"pk": f"insight#{elder}"}, UpdateExpression="SET ack=:t", ExpressionAttributeValues={":t": True})
        return {"statusCode": 200, "body": "Thanks, acknowledged."}
    if e["action"] == "acked":
        return bool(state.get_item(Key={"pk": f"insight#{e['elder']}"}).get("Item", {}).get("ack"))
    tier = e["tier"]
    sns.publish(TopicArn=os.environ["TOPIC"], Subject=f"CareRing alert (tier {tier})", Message=e["msg"])
    try:
        phone = os.environ["FAMILY_PHONE"] if tier == 1 else os.environ["CHW_PHONE"]
        sns.publish(PhoneNumber=phone, Message=f"CareRing (tier {tier}): {e['msg']}")
    except Exception as ex:
        print("SMS skipped:", ex)
