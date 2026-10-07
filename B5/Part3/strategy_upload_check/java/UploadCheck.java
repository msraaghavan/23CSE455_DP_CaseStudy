import java.util.List;

/** Strategy - the "Upload File Checks" from doc_manager, made small. */
record Upload(String name, String contentType, long size) {}

/** Strategy: every validator has the same method. null means "no problem". */
interface Validator {
    String check(Upload upload);
}

/** ConcreteStrategy (like Django's FileExtensionValidator). */
class ExtensionValidator implements Validator {
    private final List<String> allowed;

    ExtensionValidator(List<String> allowed) {
        this.allowed = allowed;
    }

    @Override
    public String check(Upload upload) {
        int dot = upload.name().lastIndexOf('.');
        String extension = dot < 0 ? "" : upload.name().substring(dot + 1).toLowerCase();
        if (!allowed.contains(extension)) {
            return "ERROR extension not allowed";
        }
        return null;
    }
}

/** Context (like ContentTypeRestrictedFileField): runs every validator, then its own checks. */
class UploadField {
    private final List<Validator> validators; // the strategies
    private final List<String> contentTypes;
    private final long maxSize;

    UploadField(List<Validator> validators, List<String> contentTypes, long maxSize) {
        this.validators = validators;
        this.contentTypes = contentTypes;
        this.maxSize = maxSize;
    }

    String clean(Upload upload) {
        for (Validator validator : validators) {
            String error = validator.check(upload);
            if (error != null) {
                return error;
            }
        }
        if (!contentTypes.contains(upload.contentType())) {
            return "ERROR file type not supported";
        }
        if (upload.size() > maxSize) {
            return "ERROR file too big";
        }
        return "OK";
    }
}

/** Client: chooses the strategy (like ContentTypeRestrictedFileField.__init__). */
public class UploadCheck {
    public static UploadField documentField(long maxSize) {
        return new UploadField(List.of(new ExtensionValidator(List.of("pdf", "html"))),
                List.of("application/pdf", "text/html"), maxSize);
    }
}
