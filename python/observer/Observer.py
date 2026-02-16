
import sys, time
from common import gen_message, parse, transform_compute_avg, serialize
import json

class TelemetrySubject:
    def __init__(self):
        self.subs = []
    def register(self, o): self.subs.append(o)
    def publish(self, json_s):
        for o in self.subs: o.on_message(json_s)

class ProcessorObserver:
    def __init__(self, sink_file, threshold=0.5):
        self.sink = open(sink_file, "a")
        self.threshold = threshold
    def on_message(self, json_s):
        t = parse(json_s)
        transform_compute_avg(t)
        if t["avg"] >= self.threshold:
            self.sink.write(serialize(t) + "\n")
    def close(self): self.sink.close()

if __name__=="__main__":
    messages = int(sys.argv[1]) if len(sys.argv)>1 else 100000
    metrics = int(sys.argv[2]) if len(sys.argv)>2 else 50
    sink = sys.argv[3] if len(sys.argv)>3 else "/dev/null"
    subj = TelemetrySubject()
    proc = ProcessorObserver(sink)
    subj.register(proc)
    start = time.perf_counter()
    for i in range(messages):
        subj.publish(gen_message(metrics,i))
    end = time.perf_counter()
    proc.close()
    print(json.dumps({"pattern":"observer","lang":"python","messages":messages,"elapsed_ms":(end-start)*1000}))
