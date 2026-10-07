# CH03 - Lock the file of a version once it has been published

**Requirement.** The app promises to keep historical documents, but an admin could open an old,
published version and silently replace its file. Once a version has been published, its file must be
read-only. To change the text, the admin uploads a new version. Drafts (never published) can still be fixed.

**Acceptance criteria (what we can observe):**
1. For a version that has been published (it has a publication date), `file_obj` is a read-only field.
2. The edit form for such a version has no upload box (`file_obj` is not in the form).
3. For a draft, the file can still be changed.

**Refactoring done first (behaviour unchanged).**
- *Code smell:* misleading name. `DocumentAdmin.make_published(self, request, queryset)` receives one
  document, not a QuerySet, so `queryset.pk` reads wrong.
- *Technique:* Rename Parameter (`queryset` -> `document`). Every caller passes it by position.
- *Proof that behaviour did not change:* the same 22 tests passed before and after (`test_result.log`, steps 1-2).

**The change itself.** The hook `DocumentAdmin.get_readonly_fields` adds `'file_obj'` when the version
has a `pub_date`. Django's admin recipe already calls this hook when it builds the form and the page,
so no other code had to change.

**Pattern effects.**
| Instance | Status | Why |
|---|---|---|
| Admin Read-only Fields (Template Method) | modified | the hook now also returns `file_obj` for published versions |
| all other instances | preserved | not touched |

**Files.** `refactoring.diff`, `feature.diff`, `test_result.log`. Full source after CH03: `Part2/code/`.
**Tests.** 22 -> 25. All pass. The two "locked" tests failed before the change (`test_result.log`, step 3).
