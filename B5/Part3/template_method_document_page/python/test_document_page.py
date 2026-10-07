"""Test runner: reads the shared test cases and checks document_page.py."""
import sys

from document_page import DocumentPage

path = sys.argv[1] if len(sys.argv) > 1 else "../../test-cases/document_page_cases.txt"
passed = total = 0
with open(path, encoding="utf-8") as cases:
    for line in cases:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        method, versions_text, expected = [part.strip() for part in line.split("|")]
        versions = []
        if versions_text != "-":
            for item in versions_text.split(","):
                name, flag = item.split(":")
                versions.append((name, flag == "yes"))
        actual = DocumentPage(versions).dispatch(method)
        total += 1
        passed += actual == expected
        print(("PASS" if actual == expected else "FAIL"), method, versions_text, "->", actual)
print(f"passed {passed}/{total}")
sys.exit(0 if total and passed == total else 1)
