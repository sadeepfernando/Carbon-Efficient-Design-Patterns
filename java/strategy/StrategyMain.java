package strategy;
import common.*;
import java.io.*;
import java.util.*;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class StrategyMain {
    interface TransformStrategy { double apply(Telemetry t); }
    interface FilterStrategy { boolean keep(Telemetry t); }
    static class AvgTransform implements TransformStrategy {
        public double apply(Telemetry t){ return Utils.transformComputeAvg(t); }
    }
    static class ThresholdFilter implements FilterStrategy {
        private double threshold; ThresholdFilter(double threshold){ this.threshold = threshold; }
        public boolean keep(Telemetry t){ return t.avg >= threshold; }
    }
    static class Processor {
        private TransformStrategy transform;
        private FilterStrategy filter;
        private BufferedWriter sink;
        Processor(TransformStrategy tr, FilterStrategy f, BufferedWriter sink){ this.transform=tr; this.filter=f; this.sink = sink; }
        public void handle(String json) throws Exception {
            Telemetry t = Utils.fromJson(json);
            transform.apply(t);
            if(filter.keep(t)) { sink.write(Utils.toJson(t)); sink.newLine(); }
        }
    }
    public static void main(String[] args) throws Exception {

    int messages = 100000, metrics = 50;
    if(args.length >= 1) messages = Integer.parseInt(args[0]);
    if(args.length >= 2) metrics = Integer.parseInt(args[1]);

 
    String sinkPath = (args.length >= 3) ? args[2] : "/dev/null";

    BufferedWriter sink = new BufferedWriter(new FileWriter(sinkPath));

    Processor p = new Processor(new AvgTransform(), new ThresholdFilter(0.5), sink);

    long start = System.nanoTime();

    for(int i = 0; i < messages; i++){
        String msg = Utils.genMessage(metrics, i);
        p.handle(msg);
    }

    long end = System.nanoTime();

    sink.flush();
    sink.close();

    double elapsedMs = (end - start) / 1_000_000.0;

    // -------- PRINT RESULT ----------
    System.out.println("{\"pattern\":\"strategy\",\"lang\":\"java\",\"messages\":"
            + messages + ",\"elapsed_ms\":" + elapsedMs + "}");


    // -------- INSERT INTO SQLITE ---------------
    try {

        Connection conn = DriverManager.getConnection("jdbc:sqlite:../telemetry_results.db");

        String sql = "INSERT INTO benchmark_results " +
                "(timestamp, pattern, language, messages, execution_time_ms, average_power_w, energy_j) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?)";

        PreparedStatement pstmt = conn.prepareStatement(sql);

        String timestamp = LocalDateTime.now()
                .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));

        pstmt.setString(1, timestamp);
        pstmt.setString(2, "strategy");
        pstmt.setString(3, "java");
        pstmt.setInt(4, messages);
        pstmt.setDouble(5, elapsedMs);
        pstmt.setDouble(6, 0.0);  // power later
        pstmt.setDouble(7, 0.0);  // energy later

        pstmt.executeUpdate();
        conn.close();

    } catch (Exception e) {
        e.printStackTrace();
    }
}

}
