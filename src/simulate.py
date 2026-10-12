"""Seed 30 days of elder motion data. Invoke: {"concerning_today": true}"""
import os, random, time, boto3
t = boto3.resource("dynamodb").Table(os.environ["EVENTS"])
def put(b, elder, day, m, room):
    ts = int(day + m * 60)
    b.put_item(Item={"pk": elder, "sk": f"{ts:012d}#{room}", "ts": ts, "room": room, "ttl": ts + 40 * 86400})
def handler(event, ctx):
    random.seed(7); elder = event.get("elder", "mom")
    midnight = int(time.time()) // 86400 * 86400
    with t.batch_writer(overwrite_by_pkeys=["pk", "sk"]) as b:
        for d in range(30, -1, -1):
            day = midnight - d * 86400; today = d == 0 and event.get("concerning_today")
            put(b, elder, day, random.gauss(405, 10), "bedroom")
            if not today:
                put(b, elder, day, random.gauss(470, 15), "kitchen")
                put(b, elder, day, random.gauss(540, 25), "front_door")
            else:
                put(b, elder, day, 485, "living_room")
            for _ in range(max(0, round(random.gauss(2, .6))) if not today else 5):
                put(b, elder, day, random.uniform(0, 330), "bathroom")
            for _ in range(max(0, round(random.gauss(1.4, .7)))):
                put(b, elder, day, random.uniform(0, 300), "kitchen_night")
    return {"ok": True}
