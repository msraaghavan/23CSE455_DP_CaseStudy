# Part 1 - checking every claim of the LLM run

Run: `run_info.txt` (Claude Opus 5.5, 2026-10-06). Raw answer: `output_raw.json`, text: `output.md`.
How we checked: we read the cited lines in `data/code` (commit 5943319) and the Django 4.1.13 source,
and ran `data/test_result/probe_test.py` (log: `data/test_result/probe_test.log`, 10/10 passed).

**Our counting rule:** we count GoF design patterns where at least one class or method of the app takes part.
Architecture styles, Django idioms and GRASP principles are named in the report but not counted.

| # | LLM claim | Our verdict | Evidence and correction |
|---|---|---|---|
| 1 | Template Method "Upload-validation hook": `ContentTypeRestrictedFileField.clean` is a hook of `Field.clean` | **Incorrect** | `Field.clean` *is* the recipe (to_python, validate, run_validators). The app overrides the whole recipe and calls `super()`. That is plain extension, not a hook. Recorded as rejected candidate R1. The real pattern here is the Strategy in claim 4. |
| 2 | Template Method "Admin change-form hooks": `get_readonly_fields` and `changeform_view` are hook overrides | **Partially correct** | `get_readonly_fields` is a real hook (probe `test_2_admin_recipe_calls_the_hook`). This is our instance "Admin Read-only Fields". `changeform_view` is not a hook: it is the recipe's entry method. The app overrides it to handle the Publish button and then calls the base method. |
| 3 | Template Method "HTTP-method dispatch": `View.dispatch` calls `DocumentView.get` | **Correct** | Same as our "Published Document Page". Probe `test_1_*`: dispatch called `get` once, and a POST got 405. |
| 4 | Strategy "Pluggable extension validator": `FileExtensionValidator` in the field's validators | **Correct** | Same as our "Upload File Checks". Probe `test_3_*`: the validator is in the list, it rejects `test.txt` with code `invalid_extension`, and swapping it changes the rule. |
| 5 | Strategy "Upload widget swap": `formfield_overrides` puts `FileInput` in place of the default widget | **Correct** (one small correction) | **We had missed this one** and added it as "Upload Widget Choice". Probe `test_4_*`: the widget is `FileInput`; without the override it is `AdminFileWidget`. Correction: the replaced default is `AdminFileWidget` (a subclass of `ClearableFileInput`). |
| 6 | GRASP Information Expert (`publish`, `filename`, `set_published`) | **Correct**, not counted | A true description. GRASP is outside our counting rule. |
| 7 | GRASP Controller (`changeform_view`, `DocumentView.get`) | **Correct**, not counted | A true description. Not counted (GRASP). |
| 8 | Active Record (`DocumentModel.publish` calls `self.save()`) | **Correct**, not counted | Provided by Django's `Model`. Named in the architecture section. |
| 9 | Model-View-Template | **Correct**, not counted | Django's overall architecture. |
| 10 | Post/Redirect/Get (`HttpResponseRedirect` after the Publish POST, admin.py 49-52) | **Correct**, not counted | A web idiom, not GoF. |
| 11 | Custom Manager (`DocumentManager`) | **Correct**, not counted | A Django idiom. |
| 12 | Abstract Base Model (`Meta.abstract = True`) | **Correct**, not counted | A Django idiom. |
| 13 | Rejected list (Singleton, Factory Method, Decorator, Command, Facade, Repository, Proxy, Observer, `model = None`, template inheritance, AppConfig, Creator, Front Controller) | **Correct** | We agree with every reason. We kept the ones that have real candidate code (see the report). |
| 14 | Totals: 9 types, 14 instances, 14 concrete classes | **Incorrect** (for our rule) | The LLM counts idioms and GRASP, and also counts base classes such as `Model`, `Manager` and `View` as concrete classes. With our rule there are **2 types, 4 instances and 4 concrete classes**. |

**Summary:** 14 claims: 11 correct, 1 partially correct, 2 incorrect, 0 cannot confirm.
**What we used:** claim 5 (a missed instance, verified by a probe test before we used it).
**What we did not use:** claims 1 and 14 (wrong), and the non-GoF names (described in the report, not counted).
Reviewer: team B5. Every verdict above points to the source lines or the probe test that supports it.
