import java.nio.file.*;
import java.util.*;

record Upload(String name, String contentType, long size) {}

interface Validator {                                    // Strategy
    String check(Upload upload);                         // error text, or null = no error
}

class ExtensionValidator implements Validator {          // ConcreteStrategy
    private final List<String> allowed;
    ExtensionValidator(List<String> allowed) { this.allowed = allowed; }
    @Override public String check(Upload u) {
        int i = u.name().lastIndexOf('.');
        String ext = i < 0 ? "" : u.name().substring(i + 1).toLowerCase(Locale.ROOT);
        return allowed.contains(ext) ? null : "ERROR extension not allowed";
    }
}

class UploadField {                                      // Context
    private static final List<String> TYPES = List.of("application/pdf", "text/html");
    private final List<Validator> validators;
    private final long maxSize;
    UploadField(List<Validator> validators, long maxSize) { this.validators = validators; this.maxSize = maxSize; }

    String clean(Upload u) {
        for (Validator v : validators) { String e = v.check(u); if (e != null) return e; }
        if (!TYPES.contains(u.contentType())) return "ERROR file type not supported";
        if (u.size() > maxSize) return "ERROR file too big";
        return "OK";
    }
}

public class UploadCheckTest {
    static UploadField documentField(long maxSize) {     // Client
        return new UploadField(List.of(new ExtensionValidator(List.of("pdf", "html"))), maxSize);
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 1) { System.err.println("usage: java UploadCheckTest <cases file>"); System.exit(2); }
        int passed = 0, total = 0;
        for (String raw : Files.readAllLines(Path.of(args[0]))) {
            String line = raw.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] f = Arrays.stream(line.split("\\|")).map(String::trim).toArray(String[]::new);
            Upload upload = new Upload(f[0], f[1], Long.parseLong(f[2]));
            String actual = documentField(Long.parseLong(f[3])).clean(upload), expected = f[4];
            total++;
            if (actual.equals(expected)) { passed++; System.out.println("PASS case " + total + ": " + actual); }
            else System.out.println("FAIL case " + total + ": expected '" + expected + "', got '" + actual + "'");
        }
        System.out.println("passed " + passed + "/" + total);
        System.exit(passed == total ? 0 : 1);
    }
}
