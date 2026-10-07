import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Upload:
    name: str
    content_type: str
    size: int


def extension(name):
    _, dot, ext = name.rpartition(".")
    return ext.lower() if dot else ""


# Strategy: not declared - any object with check(upload) -> str | None works (duck typing)

class ExtensionValidator:                         # ConcreteStrategy
    def __init__(self, allowed):
        self.allowed = allowed

    def check(self, upload):
        return None if extension(upload.name) in self.allowed else "ERROR extension not allowed"


class UploadField:                                # Context
    CONTENT_TYPES = ("application/pdf", "text/html")

    def __init__(self, validators, max_size):
        self.validators = validators
        self.max_size = max_size

    def clean(self, upload):
        for validator in self.validators:
            error = validator.check(upload)
            if error:
                return error
        if upload.content_type not in self.CONTENT_TYPES:
            return "ERROR file type not supported"
        if upload.size > self.max_size:
            return "ERROR file too big"
        return "OK"


def document_field(max_size):                     # Client
    return UploadField([ExtensionValidator(["pdf", "html"])], max_size)


def main(path):
    passed = total = 0
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, ctype, size, max_size, expected = (x.strip() for x in line.split("|"))
            actual = document_field(int(max_size)).clean(Upload(name, ctype, int(size)))
            total += 1
            if actual == expected:
                passed += 1
                print(f"PASS case {total}: {actual}")
            else:
                print(f"FAIL case {total}: expected '{expected}', got '{actual}'")
    print(f"passed {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python upload_check.py <cases file>")
    sys.exit(main(sys.argv[1]))
