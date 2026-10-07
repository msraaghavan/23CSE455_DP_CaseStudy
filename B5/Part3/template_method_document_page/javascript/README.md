# Template Method - "Published Document Page" - JavaScript

- **Production code (the pattern):** `documentPage.js`
- **Test runner (kept separate):** `testDocumentPage.js`
- **Roles:** View = AbstractClass (dispatch() is the fixed recipe); DocumentPage = ConcreteClass (fills in get()).
- **Version used:** Node.js v24.17.0

## How to run (working folder: `Part3/template_method_document_page/javascript/`)
```
node testDocumentPage.js
```
The runner reads the shared cases in `../../test-cases/document_page_cases.txt` (the same file for all four languages)
and prints PASS/FAIL per case. Last line we got: `passed 7/7`. Exit code 0 means all passed.
