package observer;
import common.*;
import java.util.*;
import java.io.*;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class ObserverMain {
    interface TelemetryObserver { void onMessage(String json); }

    static class TelemetrySubject {
        private List<TelemetryObserver> subs = new ArrayList<>();
        public void register(TelemetryObserver o){ subs.add(o); }
        public void publish(String json){ for(TelemetryObserver o: subs) o.onMessage(json); }
    }


    static class ProcessorObserver implements TelemetryObserver {
        private BufferedWriter sink;
        private double threshold;
        public ProcessorObserver(BufferedWriter sink, double threshold) 
        { 
            this.sink=sink; this.threshold=threshold; 
        }

        public void onMessage(String json){
            try {
                Telemetry t = Utils.fromJson(json);
                Utils.transformComputeAvg(t);
                if(t.avg >= threshold){
                    sink.write(Utils.toJson(t));
                    sink.newLine();
                }
            } catch(Exception e){ e.printStackTrace(); }
        }
    }

    public static void main(String[] args) throws Exception {

    int messages = 100000, metrics = 50;
    if(args.length >= 1) messages = Integer.parseInt(args[0]);
    if(args.length >= 2) metrics = Integer.parseInt(args[1]);

    
    String sinkPath = (args.length >= 3) ? args[2] : "/dev/null";
    double threshold = 0.5;

    BufferedWriter sink = new BufferedWriter(new FileWriter(sinkPath));

    TelemetrySubject sub = new TelemetrySubject();
    ProcessorObserver proc = new ProcessorObserver(sink, threshold);
    sub.register(proc);

    long start = System.nanoTime();

    for(int i = 0; i < messages; i++){
        String msg = Utils.genMessage(metrics, i);
        sub.publish(msg);
    }

    long end = System.nanoTime();

    sink.flush();
    sink.close();

    double elapsedMs = (end - start) / 1_000_000.0;

    // -------- PRINT RESULT ----------
    System.out.println("{\"pattern\":\"observer\",\"lang\":\"java\",\"messages\":"
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
        pstmt.setString(2, "observer");
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
