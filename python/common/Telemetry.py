import time
import psutil

class Telemetry:
    @staticmethod
    def measure(fn, *args, **kwargs):
        """
        Measure execution time and CPU usage snapshot.
        HWINFO will collect actual energy (W, Joules).
        """

        # CPU usage before execution
        cpu_before = psutil.cpu_percent(interval=None)

        # Start timer
        start_time = time.perf_counter()

        # Execute the target workload
        result = fn(*args, **kwargs)

        # Stop timer
        end_time = time.perf_counter()

        # CPU usage after execution
        cpu_after = psutil.cpu_percent(interval=None)

        return {
            "time_ms": (end_time - start_time) * 1000,
            "cpu_before_percent": cpu_before,
            "cpu_after_percent": cpu_after,
            "result": str(result)[:100]
        }
