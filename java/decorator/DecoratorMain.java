package decorator;
import common.*;
import java.util.*;
import java.io.*;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class DecoratorMain {
    interface Processor { void process(String json) throws Exception; }
    static class CoreProcessor implements Processor {
        private BufferedWriter sink; CoreProcessor(BufferedWriter sink){ this.sink=sink; }
        public void process(String json) throws Exception {
            Telemetry t = Utils.fromJson(json);
            // core parse/serialize handled by decorators - core will serialize only
            sink.write(Utils.toJson(t)); sink.newLine();
        }
    }
    static abstract class ProcessorDecorator implements Processor {
        protected Processor wrap;
        ProcessorDecorator(Processor wrap){ this.wrap = wrap; }
    }
    static class TransformDecorator extends ProcessorDecorator {
        TransformDecorator(Processor wrap){ super(wrap); }
        public void process(String json) throws Exception {
            Telemetry t = Utils.fromJson(json);
            Utils.transformComputeAvg(t);
            wrap.process(Utils.toJson(t));
        }
    }
    static class FilterDecorator extends ProcessorDecorator {
        private double threshold;
        FilterDecorator(Processor wrap, double threshold){ super(wrap); this.threshold = threshold; }
        public void process(String json) throws Exception {
            Telemetry t = Utils.fromJson(json);
            if(Utils.transformComputeAvg(t) >= threshold) wrap.process(Utils.toJson(t));
        }
    }
    public static void main(String[] args) throws Exception {

    int messages = 100000, metrics = 50;
    if(args.length >= 1) messages = Integer.parseInt(args[0]);
    if(args.length >= 2) metrics = Integer.parseInt(args[1]);

    
    String sinkPath = (args.length >= 3) ? args[2] : "/dev/null";
    BufferedWriter sink = new BufferedWriter(new FileWriter(sinkPath));

    Processor core = new CoreProcessor(sink);

    // Compose decorators: Filter -> Transform -> Core
    Processor p = new FilterDecorator(new TransformDecorator(core), 0.5);

    long start = System.nanoTime();

    for(int i = 0; i < messages; i++){
        String msg = Utils.genMessage(metrics, i);
        p.process(msg);
    }

    long end = System.nanoTime();

    sink.flush();
    sink.close();

    double elapsedMs = (end - start) / 1_000_000.0;

    // -------- PRINT RESULT ----------
    System.out.println("{\"pattern\":\"decorator\",\"lang\":\"java\",\"messages\":"
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
        pstmt.setString(2, "decorator");
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
