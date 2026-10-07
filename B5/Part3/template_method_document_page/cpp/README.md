# Template Method - "Published Document Page" - C++

- **Production code (the pattern):** `document_page.hpp`
- **Test runner (kept separate):** `test_document_page.cpp`
- **Roles:** View = AbstractClass (dispatch() is the fixed recipe); DocumentPage = ConcreteClass (fills in get()).
- **Version used:** clang 21.1.0 (ziglang 0.16.0, -std=c++17 -O2)

## How to run (working folder: `Part3/template_method_document_page/cpp/`)
```
python -m ziglang c++ -std=c++17 -O2 -o test_document_page.exe test_document_page.cpp
test_document_page.exe
```
The runner reads the shared cases in `../../test-cases/document_page_cases.txt` (the same file for all four languages)
and prints PASS/FAIL per case. Last line we got: `passed 7/7`. Exit code 0 means all passed.

The compiler is clang from the `ziglang` pip package (`pip install ziglang==0.16.0`). Any C++17 compiler works, e.g. `g++ -std=c++17 -O2 -o test.exe test_document_page.cpp`. Do not upload the `.exe`.
