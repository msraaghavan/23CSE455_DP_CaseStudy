import java.util.List;
import java.util.Map;

/** Template Method - the "Published Document Page" from doc_manager, made small. */
abstract class View {
    /** The fixed recipe (like Django's View.dispatch). final: subclasses cannot change it. */
    public final String dispatch(String method) {
        if (!method.equals("GET")) {
            return "405 Method Not Allowed";
        }
        return get(); // the step a subclass fills in
    }

    protected abstract String get();
}

/** One saved version of the document. */
record Version(String name, boolean published) {}

/** ConcreteClass. Fills in get() (like doc_manager's DocumentView.get). */
public class DocumentPage extends View {
    private static final Map<String, String> CONTENT_TYPES =
            Map.of("pdf", "application/pdf", "html", "text/html");
    private final List<Version> versions;

    public DocumentPage(List<Version> versions) {
        this.versions = versions;
    }

    @Override
    protected String get() {
        for (Version version : versions) {
            if (version.published()) {
                String extension = version.name().substring(version.name().lastIndexOf('.') + 1);
                return "200 " + CONTENT_TYPES.get(extension);
            }
        }
        return "404 Not Found";
    }
}
