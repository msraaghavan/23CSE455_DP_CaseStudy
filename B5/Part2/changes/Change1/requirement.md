# CH01 - Accept plain-text (.txt) documents

**Requirement.** Some documents are short notices written as plain text. The admin must be able to
upload a `.txt` version, and visitors must be able to read it on the document page.

**Acceptance criteria (what we can observe):**
1. A `.txt` file passes the upload check; an `.exe` file is still rejected.
2. A published `.txt` document is shown with content type `text/plain`.
3. The upload box tells the browser the allowed types: `accept="application/pdf,text/html,text/plain"`.
   (Before, the value was a Python list `['application/pdf', 'text/html']`, which browsers ignore.)
4. The document page never crashes because of the file name: `POLICY.PDF` is shown as a PDF, and an
   unknown type gives "404 Not Found" instead of a server error.

**Refactoring done first (behaviour unchanged).**
- *Code smell:* Shotgun Surgery / duplicated knowledge. The list of allowed types was written in
  four places: `models.py` (content types and extensions), `admin.py` (upload box), `views.py` (if/elif).
- *Technique:* Extract Constant + Replace Conditional with a lookup table. One table
  `FILE_TYPES = {'pdf': 'application/pdf', 'html': 'text/html'}` is now used by all four places.
- *Proof that behaviour did not change:* 3 characterization tests for the document page were written
  first (`characterization_tests.diff`). All 14 tests passed before and after the refactoring, and the
  HTML of the upload box is identical (`test_result.log`, steps 1-2).

**The change itself.** One new line in `FILE_TYPES` (`'txt': 'text/plain'`), the `accept` value
joined with commas, and the page compares the extension in lower case and returns 404 for unknown types.
One old test used `.txt` as its example of a *bad* file; it now uses `.exe`.

**Pattern effects.**
| Instance | Status | Why |
|---|---|---|
| Upload File Checks (Strategy) | modified | the ConcreteStrategy `FileExtensionValidator` is now built from `FILE_TYPES` and also allows `txt` |
| Upload Widget Choice (Strategy) | modified | the ConcreteStrategy `FileInput` gets a corrected `accept` value from `FILE_TYPES` |
| Published Document Page (Template Method) | modified | the hook `DocumentView.get` uses the table instead of if/elif; roles unchanged |
| Admin Read-only Fields (Template Method) | preserved | not touched |

**Files.** `characterization_tests.diff`, `refactoring.diff`, `feature.diff`, `test_result.log`, `code/` (full source after CH01).
**Tests.** 11 (original) -> 14 (characterization) -> 19 after CH01. All pass. The 5 new tests failed before the change (`test_result.log`, step 3).
