import json, random, time
from typing import List, Dict
def gen_message(metrics_count:int, idx:int) -> str:
    r = random.Random(idx)
    m = {"id":f"t-{idx}","ts":int(time.time()*1000),"metrics":[r.random() for _ in range(metrics_count)]}
    return json.dumps(m)

def parse(json_s:str) -> Dict:
    return json.loads(json_s)

def transform_compute_avg(t:Dict) -> float:
    arr = t.get("metrics", [])
    if not arr: t["avg"]=0.0; return 0.0
    s = sum(arr)
    t["avg"] = s / len(arr)
    return t["avg"]

def serialize(t:Dict) -> str:
    return json.dumps(t)
