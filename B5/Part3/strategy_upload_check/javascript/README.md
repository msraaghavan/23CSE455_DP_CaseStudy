# Strategy - "Upload File Checks" - JavaScript

- **Production code (the pattern):** `uploadCheck.js`
- **Test runner (kept separate):** `testUploadCheck.js`
- **Roles:** UploadField = Context; Validator = Strategy (not declared in Python/JavaScript); ExtensionValidator = ConcreteStrategy; documentField() = Client that picks the strategy.
- **Version used:** Node.js v24.17.0

## How to run (working folder: `Part3/strategy_upload_check/javascript/`)
```
node testUploadCheck.js
```
The runner reads the shared cases in `../../test-cases/upload_check_cases.txt` (the same file for all four languages)
and prints PASS/FAIL per case. Last line we got: `passed 8/8`. Exit code 0 means all passed.
