// Strategy - the "Upload File Checks" from doc_manager, made small.

// ConcreteStrategy (like Django's FileExtensionValidator).
// The Strategy itself is not declared: any object with check(upload) works.
class ExtensionValidator {
  constructor(allowed) {
    this.allowed = allowed;
  }

  check(upload) {
    const dot = upload.name.lastIndexOf(".");
    const extension = dot < 0 ? "" : upload.name.slice(dot + 1).toLowerCase();
    if (!this.allowed.includes(extension)) {
      return "ERROR extension not allowed";
    }
    return null;
  }
}

// Context (like ContentTypeRestrictedFileField): runs every validator, then its own checks.
class UploadField {
  constructor(validators, contentTypes, maxSize) {
    this.validators = validators; // the strategies
    this.contentTypes = contentTypes;
    this.maxSize = maxSize;
  }

  clean(upload) {
    for (const validator of this.validators) {
      const error = validator.check(upload);
      if (error) {
        return error;
      }
    }
    if (!this.contentTypes.includes(upload.contentType)) {
      return "ERROR file type not supported";
    }
    if (upload.size > this.maxSize) {
      return "ERROR file too big";
    }
    return "OK";
  }
}

// Client: chooses the strategy (like ContentTypeRestrictedFileField.__init__).
function documentField(maxSize) {
  return new UploadField([new ExtensionValidator(["pdf", "html"])],
    ["application/pdf", "text/html"], maxSize);
}

module.exports = { ExtensionValidator, UploadField, documentField };
