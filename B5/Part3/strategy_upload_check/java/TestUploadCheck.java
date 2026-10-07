import java.nio.file.Files;
import java.nio.file.Path;

/** Test runner: reads the shared test cases and checks UploadCheck.java. */
public class TestUploadCheck {
    public static void main(String[] args) throws Exception {
        String path = args.length > 0 ? args[0] : "../../test-cases/upload_check_cases.txt";
        int passed = 0;
        int total = 0;
        for (String line : Files.readAllLines(Path.of(path))) {
            line = line.strip();
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            String[] p = line.split("\\|");
            String name = p[0].strip();
            String contentType = p[1].strip();
            long size = Long.parseLong(p[2].strip());
            long maxSize = Long.parseLong(p[3].strip());
            String expected = p[4].strip();
            String actual = UploadCheck.documentField(maxSize).clean(new Upload(name, contentType, size));
            total++;
            if (actual.equals(expected)) {
                passed++;
            }
            System.out.println((actual.equals(expected) ? "PASS " : "FAIL ") + name + " " + contentType + " " + size + " -> " + actual);
        }
        System.out.println("passed " + passed + "/" + total);
        System.exit(total > 0 && passed == total ? 0 : 1);
    }
}
