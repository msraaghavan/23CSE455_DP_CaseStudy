# doc_manager 1.0.2: Change-Request Analysis

**Convention for (c):** *preserved* means the roles and participants are unchanged, even if code inside a participant changes. *modified* means a role or participant changes. *extended* means a new participant is added.

---

## CH01: Accept `.txt` documents

**a. Smell and refactoring**
- **Smell: Shotgun Surgery / Duplicated Code.** The list of allowed types lives in four places:
  - `models.py:20` (MIME list)
  - `models.py:28` (hard-coded extensions; this also overwrites any `validators` the caller passes)
  - `admin.py:23` (the `accept` attribute)
  - `views.py:17-22` (an `if/elif` *Switch Statement*)
- **Refactoring:** *Replace Magic Literal with Symbolic Constant*. Add one `ALLOWED_TYPES = {'pdf': 'application/pdf', 'html': 'text/html'}` and derive all four uses from it.
  - In the view, use *Substitute Algorithm* (a dict lookup instead of `if/elif`).
  - Keep the unknown-extension path failing as it does today (an unbound `response`), or pin that behaviour in a test first.
- **Proof of no behaviour change:** write characterization tests before refactoring and run them unchanged afterwards. They should check:
  - pdf and html uploads are accepted; other files are rejected with the same messages
  - the view returns the same `Content-Type` and body for pdf and html
  - the rendered `accept` attribute is identical
  
  Also run `makemigrations --check`; it should report no migration.

**b. Smallest change**
- Add `'txt': 'text/plain'` to the mapping. This covers the validator, `content_types`, the widget `accept` and the view's content type.
- Without the refactoring, edit all four places plus a new `elif filename.endswith('.txt')`.
- Changed validators produce a migration in each concrete app (`our_app`).

**c. Patterns:** 1 preserved · 2 preserved · 3 preserved (same `FileExtensionValidator`, just configured differently) · 4 preserved. No new instance.

**d. Tests**
- An admin upload of `a.txt` (`text/plain`) is saved.
- `GET` on the view returns 200, `Content-Type: text/plain`, and the file content.
- `.exe`, or `.txt` sent with a wrong MIME type, gives a form error. pdf and html still work.
- A `.txt` file over the size limit is rejected.
- The rendered widget `accept` contains `text/plain`.

---

## CH02: Open an older version at `see_document/<id>/`

**a. Smell and refactoring**
- **Smell: Long Method.** `DocumentView.get` (8-23) mixes *which document* to load with *how to send it*, and repeats `FileResponse(...)`.
- **Refactoring:** *Extract Method* into `get_document(self)` (returns `published()` or raises 404) and `build_response(self, document)`.
- **Proof of no behaviour change:** characterization tests for the following, run before and after:
  - a published document returns 200 with the right type and body
  - no published document returns 404

**b. Smallest change**
- `DocumentView.get(self, request, id=None)` passes `id` to `get_document(id)`.
- `get_document(id)` returns `get_object_or_404(self.model, pk=id)` if `id` is given, otherwise uses the old path.
- Add the URL `path('see_document/<int:id>/', OurView.as_view())` in the host project.
- ⚠️ This also exposes **unpublished drafts** publicly. That is what the request says, but confirm it with the stakeholder.

**c. Patterns:** 1 preserved (`dispatch` still calls `get`; only an optional kwarg is added) · 2 preserved · 3 preserved · 4 preserved. No new instance: the extracted methods could act as hooks, but no subclass overrides them.

**d. Tests**
- Create v1 and v2, then publish v2:
  - `see_document/<v1.id>/` returns v1's bytes and correct type
  - the base URL still returns v2
- An unknown id returns 404.
- A draft id returns 200.

---

## CH03: Lock the file of a published version

**a. Smell and refactoring**
- **Smell: magic literal tuple inside a conditional** in the hook `get_readonly_fields` (`admin.py:27-30`). A second condition would make it messier.
- **Hidden trap:** `set_published` sets `published=False` on older versions, but their `pub_date` stays set. So "has been published" means `pub_date is not None`, not `published`.
- **Refactoring:**
  - *Extract Constant*: `change_readonly_fields = ('add_date','pub_date','published')`
  - *Decompose Conditional*
  - (Side smell: *Rename Parameter* `queryset` to `obj` in `make_published`.)
- **Proof of no behaviour change:** unit-test that `get_readonly_fields(req, None)` and `get_readonly_fields(req, obj)` return the same tuples before and after. The change-page HTML snapshot should be unchanged.

**b. Smallest change**
- Add `DocumentModel.was_published()`, which returns `self.pub_date is not None`.
- In `DocumentAdmin.get_readonly_fields`, if `obj` exists and `obj.was_published()`, add `'file_obj'`.
- Read-only fields are left out of the ModelForm, so a forged POST cannot replace the file. This protection applies only in the admin, as requested.

**c. Patterns:** 1 preserved · 2 preserved (same hook; only its body grows) · 3 preserved · 4 preserved (the widget is simply not rendered for locked objects). No new instance.

**d. Tests**
- **Published version:**
  - the change page has no `<input name="file_obj">`
  - a POST with a new file leaves the stored file unchanged
- **Version published earlier, now unpublished** (`pub_date` set): still locked.
- **Draft:** the file input is present, and uploading a replacement works.
- **Add page:** the file input is present.