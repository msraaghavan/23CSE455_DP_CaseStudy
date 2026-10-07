import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/** Test runner: reads the shared test cases and checks DocumentPage.java. */
public class TestDocumentPage {
    public static void main(String[] args) throws Exception {
        String path = args.length > 0 ? args[0] : "../../test-cases/document_page_cases.txt";
        int passed = 0;
        int total = 0;
        for (String line : Files.readAllLines(Path.of(path))) {
            line = line.strip();
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            String[] parts = line.split("\\|");
            String method = parts[0].strip();
            String versionsText = parts[1].strip();
            String expected = parts[2].strip();
            List<Version> versions = new ArrayList<>();
            if (!versionsText.equals("-")) {
                for (String item : versionsText.split(",")) {
                    String[] pair = item.split(":");
                    versions.add(new Version(pair[0], pair[1].equals("yes")));
                }
            }
            String actual = new DocumentPage(versions).dispatch(method);
            total++;
            if (actual.equals(expected)) {
                passed++;
            }
            System.out.println((actual.equals(expected) ? "PASS " : "FAIL ") + method + " " + versionsText + " -> " + actual);
        }
        System.out.println("passed " + passed + "/" + total);
        System.exit(total > 0 && passed == total ? 0 : 1);
    }
}
