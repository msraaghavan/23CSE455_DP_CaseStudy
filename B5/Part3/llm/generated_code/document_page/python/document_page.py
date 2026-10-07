import sys
from abc import ABC, abstractmethod

CONTENT_TYPES = {"pdf": "application/pdf", "html": "text/html"}


def extension(name):
    _, dot, ext = name.rpartition(".")
    return ext.lower() if dot else ""


class View(ABC):                                  # AbstractClass
    def dispatch(self, method):                   # fixed recipe
        if method != "GET":
            return "405 Method Not Allowed"
        return self.get()

    @abstractmethod
    def get(self):                                # the step
        ...


class DocumentPage(View):                         # ConcreteClass
    def __init__(self, versions):
        self.versions = versions                  # list of (name, published)

    def get(self):
        for name, published in self.versions:
            if published:
                return "200 " + CONTENT_TYPES[extension(name)]
        return "404 Not Found"


def parse_versions(text):
    if text == "-":
        return []
    return [(n.strip(), p.strip() == "yes") for n, p in (i.rsplit(":", 1) for i in text.split(","))]


def main(path):
    passed = total = 0
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            method, versions, expected = (x.strip() for x in line.split("|"))
            actual = DocumentPage(parse_versions(versions)).dispatch(method)
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
        sys.exit("usage: python document_page.py <cases file>")
    sys.exit(main(sys.argv[1]))
