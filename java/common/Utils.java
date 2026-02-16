package common;
import com.google.gson.*;
import java.util.*;
import java.io.*;
public class Utils {
    private static final Gson gson = new Gson();
    public static String toJson(Telemetry t){ return gson.toJson(t); }
    public static Telemetry fromJson(String s){ return gson.fromJson(s, Telemetry.class); }
    public static String genMessage(int metricsCount, int id) {
        Random r = new Random(id);
        Map<String,Object> m = new HashMap<>();
        m.put("id","t-"+id);
        m.put("ts", System.currentTimeMillis());
        List<Double> arr = new ArrayList<>(metricsCount);
        for(int i=0;i<metricsCount;i++) arr.add(r.nextDouble());
        m.put("metrics", arr);
        return gson.toJson(m);
    }
    public static double transformComputeAvg(Telemetry t){
        double s=0; for(double v: t.metrics) s+=v;
        t.avg = (t.metrics.size()==0)?0.0:s/t.metrics.size();
        return t.avg;
    }
}
