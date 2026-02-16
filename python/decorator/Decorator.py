
import sys, time, json
from common import gen_message, parse, transform_compute_avg, serialize

class Processor:
    def process(self, json_s): raise NotImplementedError

class CoreProcessor(Processor):
    def __init__(self, sink_file):
        self.sink = open(sink_file, "a")
    def process(self, json_s):
        t = parse(json_s)
        self.sink.write(serialize(t) + "\n")
    def close(self): self.sink.close()

class TransformDecorator(Processor):
    def __init__(self, wrap):
        self.wrap = wrap
    def process(self, json_s):
        t = parse(json_s)
        transform_compute_avg(t)
        self.wrap.process(serialize(t))

class FilterDecorator(Processor):
    def __init__(self, wrap, threshold=0.5):
        self.wrap=wrap; self.threshold=threshold
    def process(self, json_s):
        t = parse(json_s)
        transform_compute_avg(t)
        if t["avg"] >= self.threshold:
            self.wrap.process(serialize(t))

if __name__=="__main__":
    messages = int(sys.argv[1]) if len(sys.argv)>1 else 100000
    metrics = int(sys.argv[2]) if len(sys.argv)>2 else 50
    sink = sys.argv[3] if len(sys.argv)>3 else "/dev/null"
    core = CoreProcessor(sink)
    proc = FilterDecorator(TransformDecorator(core), 0.5)
    start = time.perf_counter()
    for i in range(messages):
        proc.process(gen_message(metrics,i))
    end = time.perf_counter()
    core.close()
    print(json.dumps({"pattern":"decorator","lang":"python","messages":messages,"elapsed_ms":(end-start)*1000}))
