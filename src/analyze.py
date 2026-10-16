import os, json, re, time, statistics as st, boto3
from boto3.dynamodb.conditions import Key
ddb = boto3.resource("dynamodb")
ev = ddb.Table(os.environ["EVENTS"]); state = ddb.Table(os.environ["STATE"])
br = boto3.client("bedrock-runtime"); sf = boto3.client("stepfunctions")
LABEL = {"ramadan": "Ramadan", "temple": "Sunday temple", "diwali": "Diwali"}
SKIP = {"ramadan": {"kitchen"}, "diwali": {"kitchen", "outing"}}   # checks paused by the cultural calendar

def features(items, day0):
    f = {"kitchen": None, "outing": None, "night_bath": 0, "night_kitchen": 0}
    for i in sorted(items, key=lambda x: x["ts"]):
        m = (int(i["ts"]) - day0) / 60
        if i["room"] == "kitchen" and f["kitchen"] is None and m > 300: f["kitchen"] = m
        if i["room"] == "front_door" and f["outing"] is None: f["outing"] = m
        if i["room"] == "bathroom" and m < 360: f["night_bath"] += 1
        if i["room"] == "kitchen_night": f["night_kitchen"] += 1
    return f

def rule_msg(today, base, cal):
    skip, notes = SKIP.get(cal, set()), []
    bk = base["kitchen"][0]
    if "kitchen" not in skip and today["kitchen"] is None and bk:
        notes.append(f"Mom usually reaches the kitchen around {int(bk//60)}:{int(bk%60):02d} but has not been there yet today")
    nb = base["night_bath"]
    if today["night_bath"] > nb[0] + 2 * nb[1] + 1:
        notes.append(f"she made {today['night_bath']} bathroom trips overnight versus about {nb[0]} on a normal night")
    if "outing" not in skip and today["outing"] is None and base["outing"][0]:
        notes.append("there has been no outing yet, which is part of her routine")
    msg = ("CareRing noticed a change: " + "; ".join(notes) + ". Please check in with her.") if notes else "Routine matches the 30-day baseline."
    if cal in LABEL: msg += f" ({LABEL[cal]} routine applied.)"
    return msg, len(notes) >= 2

def handler(event, ctx):
    elder = event.get("elder", "mom")
    prefs = state.get_item(Key={"pk": f"prefs#{elder}"}).get("Item", {})
    cal = prefs.get("calendar", "everyday")
    mid = int(time.time()) // 86400 * 86400; days = []
    for d in range(31):
        s = mid - d * 86400
        items = ev.query(KeyConditionExpression=Key("pk").eq(elder) & Key("sk").between(f"{s:012d}", f"{s+86399:012d}~"))["Items"]
        days.append(features(items, s))
    today, hist = days[0], days[1:]
    def avg(k):
        v = [h[k] for h in hist if h[k] is not None]
        return (round(st.mean(v), 1), round(st.pstdev(v), 1)) if v else (None, 0)
    base = {k: avg(k) for k in today}
    summary = {"today": today, "baseline_mean_sd": base, "cultural_calendar": cal,
               "family_rules": {"ignore_night_kitchen": prefs.get("ignore_night_kitchen", True)}}
    source = "ai"
    try:
        if prefs.get("privacy_mode", False): raise Exception("privacy mode")
        prompt = ("You are CareRing, a calm elder-care assistant. Compare today's activity with the 30-day baseline "
                  "(minutes after midnight). Respect the family's cultural calendar (e.g. Ramadan: no morning-kitchen expectation). Reply ONLY JSON: "
                  '{"severity":0-3,"message":"<=2 warm, specific sentences"}.\n' + json.dumps(summary))
        r = br.converse(modelId=os.environ["MODEL_ID"], messages=[{"role": "user", "content": [{"text": prompt}]}],
                        inferenceConfig={"maxTokens": 300, "temperature": 0.2})
        out = json.loads(re.search(r"\{.*\}", r["output"]["message"]["content"][0]["text"], re.S).group())
        msg, severe = out["message"], out["severity"] >= 2
    except Exception as ex:
        print("AI skipped, using rules:", ex)
        source = "rules"
        msg, severe = rule_msg(today, base, cal)
    state.put_item(Item={"pk": f"insight#{elder}", "msg": msg, "ts": int(time.time()), "ack": False, "source": source})
    if severe and not event.get("dry"):
        sf.start_execution(stateMachineArn=os.environ["MACHINE"],
                           input=json.dumps({"elder": elder, "msg": msg, "wait": int(os.environ["WAIT"])}))
    return {"severe": severe, "msg": msg, "source": source}
