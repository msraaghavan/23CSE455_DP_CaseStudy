import java.nio.file.*;
import java.util.*;

record Version(String name, boolean published) {}

abstract class View {                                   // AbstractClass
    public final String dispatch(String method) {       // fixed recipe, cannot be overridden
        if (!method.equals("GET")) return "405 Method Not Allowed";
        return get();
    }
    protected abstract String get();                    // the step
}

class DocumentPage extends View {                       // ConcreteClass
    private static final Map<String, String> TYPES = Map.of("pdf", "application/pdf", "html", "text/html");
    private final List<Version> versions;
    DocumentPage(List<Version> versions) { this.versions = versions; }

    @Override protected String get() {
        for (Version v : versions)
            if (v.published()) {
                int i = v.name().lastIndexOf('.');
                String ext = i < 0 ? "" : v.name().substring(i + 1).toLowerCase(Locale.ROOT);
                return "200 " + TYPES.get(ext);
            }
        return "404 Not Found";
    }
}

public class DocumentPageTest {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) { System.err.println("usage: java DocumentPageTest <cases file>"); System.exit(2); }
        int passed = 0, total = 0;
        for (String raw : Files.readAllLines(Path.of(args[0]))) {
            String line = raw.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] f = line.split("\\|");
            String method = f[0].trim(), list = f[1].trim(), expected = f[2].trim();
            List<Version> versions = new ArrayList<>();
            if (!list.equals("-"))
                for (String item : list.split(",")) {
                    String[] p = item.trim().split(":");
                    versions.add(new Version(p[0].trim(), p[1].trim().equals("yes")));
                }
            String actual = new DocumentPage(versions).dispatch(method);
            total++;
            if (actual.equals(expected)) { passed++; System.out.println("PASS case " + total + ": " + actual); }
            else System.out.println("FAIL case " + total + ": expected '" + expected + "', got '" + actual + "'");
        }
        System.out.println("passed " + passed + "/" + total);
        System.exit(passed == total ? 0 : 1);
    }
}
