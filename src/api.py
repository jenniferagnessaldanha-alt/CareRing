import os, json, time, boto3
state = boto3.resource("dynamodb").Table(os.environ["STATE"])
sns = boto3.client("sns"); lam = boto3.client("lambda"); sf = boto3.client("stepfunctions")
MODES = {"everyday", "ramadan", "temple", "diwali"}
def out(b): return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(b)}
def handler(e, ctx):
    q = e.get("queryStringParameters") or {}; elder = q.get("elder", "mom"); act = q.get("action")
    if act == "mode" and q.get("value") in MODES:   # cultural routine engine
        state.update_item(Key={"pk": f"prefs#{elder}"}, UpdateExpression="SET calendar=:c", ExpressionAttributeValues={":c": q["value"]})
        r = json.loads(lam.invoke(FunctionName=os.environ["ANALYZE"], Payload=json.dumps({"elder": elder, "dry": True}))["Payload"].read())
        r.update(ts=int(time.time()), ack=False); return out(r)
    if act == "help":                               # reverse check-in
        lvl = int(q.get("level", "1")); now = int(time.time())
        msg = f"{elder.title()} pressed the help button" + (" (EMERGENCY). Please call now." if lvl == 3 else " and asked for you.")
        state.put_item(Item={"pk": f"insight#{elder}", "msg": msg, "ts": now, "ack": False, "source": "help"})
        if lvl == 3:
            sns.publish(TopicArn=os.environ["TOPIC"], Subject="CareRing EMERGENCY", Message=msg)
            try: sns.publish(PhoneNumber=os.environ["CHW_PHONE"], Message="CareRing: " + msg)
            except Exception as ex: print("SMS skipped:", ex)
        else:
            sf.start_execution(stateMachineArn=os.environ["MACHINE"], input=json.dumps({"elder": elder, "msg": msg, "wait": int(os.environ["WAIT"])}))
        return out({"msg": msg, "source": "help", "ts": now, "ack": False})
    return out({"error": "unknown action"})
