package common;
import java.util.List;
public class Telemetry {
    public String id;
    public long ts;
    public List<Double> metrics;
    public double avg; // derived
    public Telemetry() {}
    public Telemetry(String id, long ts, List<Double> metrics) {
        this.id = id; this.ts = ts; this.metrics = metrics;
    }
}
