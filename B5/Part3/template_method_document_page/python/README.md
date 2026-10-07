# Template Method - "Published Document Page" - Python

- **Production code (the pattern):** `document_page.py`
- **Test runner (kept separate):** `test_document_page.py`
- **Roles:** View = AbstractClass (dispatch() is the fixed recipe); DocumentPage = ConcreteClass (fills in get()).
- **Version used:** CPython 3.11.9

## How to run (working folder: `Part3/template_method_document_page/python/`)
```
python test_document_page.py
```
The runner reads the shared cases in `../../test-cases/document_page_cases.txt` (the same file for all four languages)
and prints PASS/FAIL per case. Last line we got: `passed 7/7`. Exit code 0 means all passed.
