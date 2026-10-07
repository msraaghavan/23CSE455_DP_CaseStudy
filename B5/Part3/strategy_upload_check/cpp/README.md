# Strategy - "Upload File Checks" - C++

- **Production code (the pattern):** `upload_check.hpp`
- **Test runner (kept separate):** `test_upload_check.cpp`
- **Roles:** UploadField = Context; Validator = Strategy (not declared in Python/JavaScript); ExtensionValidator = ConcreteStrategy; documentField() = Client that picks the strategy.
- **Version used:** clang 21.1.0 (ziglang 0.16.0, -std=c++17 -O2)

## How to run (working folder: `Part3/strategy_upload_check/cpp/`)
```
python -m ziglang c++ -std=c++17 -O2 -o test_upload_check.exe test_upload_check.cpp
test_upload_check.exe
```
The runner reads the shared cases in `../../test-cases/upload_check_cases.txt` (the same file for all four languages)
and prints PASS/FAIL per case. Last line we got: `passed 8/8`. Exit code 0 means all passed.

The compiler is clang from the `ziglang` pip package (`pip install ziglang==0.16.0`). Any C++17 compiler works, e.g. `g++ -std=c++17 -O2 -o test.exe test_upload_check.cpp`. Do not upload the `.exe`.
