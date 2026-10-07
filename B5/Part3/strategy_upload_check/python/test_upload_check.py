"""Test runner: reads the shared test cases and checks upload_check.py."""
import sys

from upload_check import Upload, document_field

path = sys.argv[1] if len(sys.argv) > 1 else "../../test-cases/upload_check_cases.txt"
passed = total = 0
with open(path, encoding="utf-8") as cases:
    for line in cases:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, content_type, size, max_size, expected = [part.strip() for part in line.split("|")]
        actual = document_field(int(max_size)).clean(Upload(name, content_type, int(size)))
        total += 1
        passed += actual == expected
        print(("PASS" if actual == expected else "FAIL"), name, content_type, size, "->", actual)
print(f"passed {passed}/{total}")
sys.exit(0 if total and passed == total else 1)
