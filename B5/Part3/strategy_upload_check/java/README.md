# Strategy - "Upload File Checks" - Java

- **Production code (the pattern):** `UploadCheck.java`
- **Test runner (kept separate):** `TestUploadCheck.java`
- **Roles:** UploadField = Context; Validator = Strategy (not declared in Python/JavaScript); ExtensionValidator = ConcreteStrategy; documentField() = Client that picks the strategy.
- **Version used:** Java 25 (javac + java)

## How to run (working folder: `Part3/strategy_upload_check/java/`)
```
javac -d build UploadCheck.java TestUploadCheck.java
java -cp build TestUploadCheck
```
The runner reads the shared cases in `../../test-cases/upload_check_cases.txt` (the same file for all four languages)
and prints PASS/FAIL per case. Last line we got: `passed 8/8`. Exit code 0 means all passed.

`build/` is a temporary output folder; do not upload it.
