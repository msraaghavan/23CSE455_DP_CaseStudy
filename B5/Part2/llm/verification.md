# Part 2 - checking every claim of the LLM run

Run: `run_info.txt` (Claude Opus 5.5, 2026-10-06). Raw answer: `output_raw.json`, text: `output.md`.
How we checked: we compared each claim with the source code, with our own changes
(`Part2/changes/Change1..3/`) and with their test logs. We also ran one extra probe for the migration
claims (`migration_probe.log`).

**Status words.** The LLM used its own meaning of the status words. We use these meanings everywhere:
- *preserved*: same roles, same participants, same behaviour (line numbers may move).
- *modified*: same roles and participants, but a participant's behaviour or configuration changed.
- *extended*: a new participant was added to the same collaboration.
- *newly_introduced*: a new collaboration appeared.

| # | LLM claim | Our verdict | Evidence and correction |
|---|---|---|---|
| 1 | CH01 smell: Shotgun Surgery. The type list is in 4 places (models.py 20 and 28, admin.py 23, views.py 17-22) | **Correct** | Same as our CH01 smell (`Change1/requirement.md`). |
| 2 | CH01 refactoring: one constant plus a dict instead of if/elif. Prove it with characterization tests and `makemigrations --check` | **Correct** | We did exactly this (`FILE_TYPES`; 3 characterization tests; 14/14 before and after). `migration_probe.log` step 1: "No changes detected". |
| 3 | `models.py:28` overwrites any validators the caller passes | **Correct** | `migration_probe.log` step 3: a field built with `[pdf, html]` really has `[pdf, html, txt]`. |
| 4 | CH01 makes a new migration in every project that uses the app | **Incorrect** | `migration_probe.log` step 2: "No changes detected". This happens because of claim 3: the field always replaces the saved validators with the current ones. |
| 5 | CH01 pattern effects: all four instances *preserved* | **Partially correct** | True under the LLM's own convention. With our status words, Upload File Checks, Upload Widget Choice and Published Document Page are *modified*, because their configuration or behaviour changed. Admin Read-only Fields is *preserved*. |
| 6 | CH01 tests: txt upload accepted, txt shown as text/plain, .exe rejected, `accept` contains text/plain | **Correct** | We have all of them (`Change1/feature.diff`, 19/19 passed). |
| 7 | CH02 smell: Long Method in `DocumentView.get`, fixed by Extract Method `get_document()` | **Correct** | Same as our CH02 refactoring (19/19 before and after). We did not also extract `build_response`, to keep it small. |
| 8 | CH02 implementation: an optional `id` argument in the same view | **Correct** (another valid design) | We used a subclass `DocumentVersionView` that overrides only `get_document()`. Both work. Ours keeps `get()` unchanged and shows the Template Method more clearly. |
| 9 | Warning: CH02 would make **unpublished drafts** public | **Correct, and we used it** | Our first version had this problem. We changed `DocumentVersionView.get_document()` to accept only versions with a publication date, and added `test_draft_gives_404` (`Change2/test_result.log`, 22/22). |
| 10 | CH02 pattern effects: all *preserved*, no new instance | **Partially correct** | True for the LLM's design (no subclass). With our design, Published Document Page is *extended* (new ConcreteClass) and "Document Choice Step" is *newly_introduced*. |
| 11 | CH03 trap: older versions keep `pub_date` after a new one is published, so "has been published" means `pub_date` is set | **Correct** | `set_published` only sets `published=False` (models.py 67). Our hook checks `obj.pub_date`. |
| 12 | CH03 smells: tuple literal in the hook; side smell: misleading parameter `queryset` | **Correct** | We used the side smell for our refactoring (Rename Parameter, 22/22 before and after). |
| 13 | Read-only fields are left out of the admin form, so a forged POST cannot replace the file | **Correct** | `test_published_file_not_in_edit_form`: `file_obj` is not in the form (`Change3/test_result.log`). |
| 14 | CH03 pattern effect: the hook is *preserved* (only its body grows) | **Partially correct** | Under our status words, the hook's answer changed, so Admin Read-only Fields is *modified*. |
| 15 | CH03 tests: published version locked, draft editable, add page editable | **Correct** | We have these, apart from the add page, which the old `test_get_readonly_fields` already covers. 25/25 passed. |

**Summary:** 15 claims: 11 correct, 3 partially correct, 1 incorrect, 0 cannot confirm.
**What we used:** claim 9 (CH02 now hides drafts). Claims 1, 2, 7 and 12 agreed with what we had already done.
Reviewer: team B5. Every verdict points to a test log, a diff or the probe log.
