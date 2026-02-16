
import sys, time, json
from common import gen_message, parse, transform_compute_avg, serialize

class TransformStrategy:
    def apply(self, t): raise NotImplementedError

class AvgTransform(TransformStrategy):
    def apply(self,t): return transform_compute_avg(t)

class FilterStrategy:
    def keep(self,t): raise NotImplementedError

class ThresholdFilter(FilterStrategy):
    def __init__(self, threshold): self.threshold=threshold
    def keep(self,t): return t["avg"] >= self.threshold

class Processor:
    def __init__(self, transform, filter_, sink_file):
        self.transform=transform; self.filter=filter_; self.sink=open(sink_file,"a")
    def handle(self, json_s):
        t = parse(json_s)
        self.transform.apply(t)
        if self.filter.keep(t):
            self.sink.write(serialize(t)+"\n")
    def close(self): self.sink.close()

if __name__=="__main__":
    messages = int(sys.argv[1]) if len(sys.argv)>1 else 100000
    metrics = int(sys.argv[2]) if len(sys.argv)>2 else 50
    sink = sys.argv[3] if len(sys.argv)>3 else "/dev/null"
    p = Processor(AvgTransform(), ThresholdFilter(0.5), sink)
    start = time.perf_counter()
    for i in range(messages):
        p.handle(gen_message(metrics,i))
    end = time.perf_counter()
    p.close()
    print(json.dumps({"pattern":"strategy","lang":"python","messages":messages,"elapsed_ms":(end-start)*1000}))
