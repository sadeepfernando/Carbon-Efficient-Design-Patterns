# Run: python strategy.py [messages] [metrics] [sink]

import sys, time, json, os, sqlite3
from datetime import datetime
from Common import gen_message, parse, transform_compute_avg, serialize


class TransformStrategy:
    def apply(self, t):
        raise NotImplementedError


class AvgTransform(TransformStrategy):
    def apply(self, t):
        return transform_compute_avg(t)


class FilterStrategy:
    def keep(self, t):
        raise NotImplementedError


class ThresholdFilter(FilterStrategy):
    def __init__(self, threshold):
        self.threshold = threshold

    def keep(self, t):
        return t["avg"] >= self.threshold


class Processor:
    def __init__(self, transform, filter_, sink_file):
        self.transform = transform
        self.filter = filter_
        self.sink = open(sink_file, "a")

    def handle(self, json_s):
        t = parse(json_s)
        self.transform.apply(t)
        if self.filter.keep(t):
            self.sink.write(serialize(t) + "\n")

    def close(self):
        self.sink.close()


if __name__ == "__main__":

    messages = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    metrics = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    sink = sys.argv[3] if len(sys.argv) > 3 else os.devnull

    p = Processor(AvgTransform(), ThresholdFilter(0.5), sink)

    start = time.perf_counter()

    for i in range(messages):
        p.handle(gen_message(metrics, i))

    end = time.perf_counter()
    p.close()

    elapsed_ms = (end - start) * 1000

    # -------- PRINT RESULT --------
    print(json.dumps({
        "pattern": "strategy",
        "lang": "python",
        "messages": messages,
        "elapsed_ms": elapsed_ms
    }))

    # -------- INSERT INTO SQLITE DATABASE --------
    try:
        conn = sqlite3.connect("../telemetry_results.db")
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        average_power = 0.0   # will update later from HWInfo
        energy = 0.0          # will compute later

        cursor.execute("""
        INSERT INTO benchmark_results
        (timestamp, pattern, language, messages,
         execution_time_ms, average_power_w, energy_j)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            "strategy",
            "python",
            messages,
            elapsed_ms,
            average_power,
            energy
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        print("Database error:", e)
