# Template Method - "Published Document Page" - Java

- **Production code (the pattern):** `DocumentPage.java`
- **Test runner (kept separate):** `TestDocumentPage.java`
- **Roles:** View = AbstractClass (dispatch() is the fixed recipe); DocumentPage = ConcreteClass (fills in get()).
- **Version used:** Java 25 (javac + java)

## How to run (working folder: `Part3/template_method_document_page/java/`)
```
javac -d build DocumentPage.java TestDocumentPage.java
java -cp build TestDocumentPage
```
The runner reads the shared cases in `../../test-cases/document_page_cases.txt` (the same file for all four languages)
and prints PASS/FAIL per case. Last line we got: `passed 7/7`. Exit code 0 means all passed.

`build/` is a temporary output folder; do not upload it.
