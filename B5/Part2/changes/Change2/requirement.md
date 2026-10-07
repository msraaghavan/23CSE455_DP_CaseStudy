# CH02 - Open an older version of a document

**Requirement.** The app keeps every old version, but visitors can only see the published one.
People ask "what did the Privacy Policy say last year?". Every version that has been published at some
time must be readable at `see_document/<id>/`. Drafts that were never published stay private.

**Acceptance criteria (what we can observe):**
1. `see_document/<id>/` shows that version, even when a newer version is published.
2. A draft (never published) gives "404 Not Found".
3. An id that does not exist gives "404 Not Found".
4. `see_document/` still shows the published version (all old tests still pass).

**Refactoring done first (behaviour unchanged).**
- *Code smell:* Long Method. `DocumentView.get` did everything: choose the document, check it, pick the
  content type and send the file.
- *Technique:* Extract Method. The first step ("which document?") moved into `get_document()`.
- *Proof that behaviour did not change:* the same 19 tests passed before and after (`test_result.log`, steps 1-2).

**The change itself.** A new class `DocumentVersionView(DocumentView)` that overrides only
`get_document()`: find the version by its id, but only if it has a publication date. `DocumentView.get`
now accepts the URL arguments. The example project and the README show the new page.
*Note:* our first version also showed drafts. The Part 2 LLM run pointed out that this would make
unreleased drafts public, so we added requirement 2 and its test (see `Part2/llm/verification.md`).

**Pattern effects.**
| Instance | Status | Why |
|---|---|---|
| Published Document Page (Template Method) | extended | new ConcreteClass `DocumentVersionView`; Django's `View.dispatch` calls the inherited `get` |
| Document Choice Step (Template Method) | newly_introduced | `DocumentView.get` is now a small recipe; its step `get_document()` is a hook that `DocumentVersionView` overrides. It grew out of the refactoring and lives inside the Published Document Page collaboration |
| Upload File Checks, Upload Widget Choice, Admin Read-only Fields | preserved | not touched |

**Files.** `refactoring.diff`, `feature.diff`, `test_result.log`, `code/` (full source after CH02).
**Tests.** 19 -> 22. All pass. The new test file failed before the change (`test_result.log`, step 3).
