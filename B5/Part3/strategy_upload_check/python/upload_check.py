"""Strategy - the "Upload File Checks" from doc_manager, made small."""
from collections import namedtuple

Upload = namedtuple("Upload", "name content_type size")


class ExtensionValidator:
    """ConcreteStrategy (like Django's FileExtensionValidator)."""

    def __init__(self, allowed):
        self.allowed = allowed

    def check(self, upload):
        extension = upload.name.rsplit(".", 1)[-1].lower() if "." in upload.name else ""
        if extension not in self.allowed:
            return "ERROR extension not allowed"
        return None


class UploadField:
    """Context (like ContentTypeRestrictedFileField): runs every validator, then its own checks."""

    def __init__(self, validators, content_types, max_size):
        self.validators = validators  # the strategies
        self.content_types = content_types
        self.max_size = max_size

    def clean(self, upload):
        for validator in self.validators:
            error = validator.check(upload)
            if error:
                return error
        if upload.content_type not in self.content_types:
            return "ERROR file type not supported"
        if upload.size > self.max_size:
            return "ERROR file too big"
        return "OK"


def document_field(max_size):
    """Client: chooses the strategy (like ContentTypeRestrictedFileField.__init__)."""
    return UploadField([ExtensionValidator(["pdf", "html"])],
                       ["application/pdf", "text/html"], max_size)
