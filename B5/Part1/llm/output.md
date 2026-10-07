# Design-pattern analysis: `doc_manager` 1.0.2 (commit 5943319)

## 1. Pattern instances

### P1. Template Method (GoF behavioral), 3 instances
In each case Django supplies the fixed algorithm and the app overrides a hook.

**1a. "Upload-validation hook"**

| Role | Participant | Location |
|---|---|---|
| AbstractClass / template method | `django.db.models.FileField` (`Field.clean`, called by `Model.clean_fields`) | Django |
| ConcreteClass | `doc_manager.models.ContentTypeRestrictedFileField` | models.py 18–54 |
| Hook override | `ContentTypeRestrictedFileField.clean` | models.py 36–54 |

Evidence: `clean` is overridden. It calls `super().clean(...)` (37–38) and then adds MIME-type and size checks (42–52).

**1b. "Admin change-form hooks"**

| Role | Participant | Location |
|---|---|---|
| AbstractClass | `django.contrib.admin.ModelAdmin` (`change_view`/`add_view` call `changeform_view`; `_changeform_view`/`get_form` call `get_readonly_fields`) | Django |
| ConcreteClass | `doc_manager.admin.DocumentAdmin` | admin.py 12–59 |
| Hook overrides | `DocumentAdmin.get_readonly_fields` | admin.py 27–30 |
| | `DocumentAdmin.changeform_view` | admin.py 42–59 |

Evidence:
- Both methods are overrides.
- `changeform_view` falls back to `admin.ModelAdmin.changeform_view(self, ...)` (54–59).
- `change_form_template` (15) plugs a template into the same algorithm.

**1c. "HTTP-method dispatch"**

| Role | Participant | Location |
|---|---|---|
| AbstractClass / template method | `django.views.View` (`as_view` → `dispatch`) | Django |
| ConcreteClass | `doc_manager.views.DocumentView` | views.py 5–23 |
| Hook | `DocumentView.get` | views.py 8–23 |

Evidence: `View.dispatch` looks up the handler named after the HTTP method. The app supplies only `get`.

### P2. Strategy (GoF behavioral), 2 instances

**2a. "Pluggable extension validator"**

| Role | Participant | Location |
|---|---|---|
| Context | `ContentTypeRestrictedFileField` (Django `Field.run_validators` iterates `self.validators`) | models.py 18–54 |
| Strategy | not separately declared (callable protocol) | — |
| ConcreteStrategy | `django.core.validators.FileExtensionValidator` | used at models.py 28 |

Evidence: `kwargs['validators'] = [FileExtensionValidator(['pdf','html'])]` (28) is passed to `super().__init__` (29).

**2b. "Upload widget swap"**

| Role | Participant | Location |
|---|---|---|
| Context | `django.forms.FileField` (the form field the admin builds) | Django |
| Strategy | `django.forms.widgets.Widget` | Django |
| ConcreteStrategy | `django.forms.widgets.FileInput` | admin.py 23 |
| Configurator | `DocumentAdmin.formfield_overrides` | admin.py 21–25 |

Evidence: `ModelAdmin.formfield_for_dbfield` matches `FileField` in the field's MRO, so the override also applies to the subclass. It then injects `FileInput` in place of the default `ClearableFileInput`.

### P3. Information Expert (GRASP), 2 instances

| Instance | Expert | Location | Evidence |
|---|---|---|---|
| 3a. "Document publishes itself" | `DocumentModel.publish`, `DocumentModel.filename` | models.py 85–88, 90–91 | They use only the model's own fields (`published`, `pub_date`, `file_obj`). |
| 3b. "Single-published invariant" | `DocumentManager.set_published`, `DocumentManager.published` | models.py 57–68 | The table-level object owns the "only one published" rule (67) and then delegates to `obj.publish()` (68). |

### P4. Controller (GRASP), 2 instances

| Instance | Controller | Location | Evidence |
|---|---|---|---|
| 4a. "Publish use-case controller" | `DocumentAdmin.changeform_view` → `DocumentAdmin.make_published` | admin.py 32–59 | Receives the `_make_published` POST (49) and delegates to `self.model.objects.set_published` (35). |
| 4b. "Show-published-document controller" | `DocumentView.get` | views.py 8–23 | Receives the visitor request, delegates to `objects.published()` (10) and builds a `FileResponse`. |

### P5. Active Record (architecture, Fowler), 1 instance: "Self-saving document"

| Role | Participant | Location |
|---|---|---|
| Active Record | `doc_manager.models.DocumentModel` (base `django.db.models.Model`) | models.py 71–91 |

Evidence: the domain method `publish` persists itself through `self.save()` (88). Fields map directly to columns (72–78).

### P6. Model–View–Template (architecture), 1 instance: "Document MVT"

| Role | Participant | Location |
|---|---|---|
| Model | `DocumentModel`, `DocumentManager` | models.py 57–91 |
| View | `DocumentView`, `DocumentAdmin` | views.py 5–23, admin.py 12–59 |
| Template | `admin_change_form_documents.html` (extends `admin/change_form.html`) | template 1–15 |
| Controller (URL dispatch) | not separately declared (Django) | — |

### P7. Post/Redirect/Get (architecture, web pattern), 1 instance: "Publish then redirect"

| Role | Participant | Location |
|---|---|---|
| POST handler | `DocumentAdmin.changeform_view` | admin.py 49–51 |
| Redirect | `django.http.HttpResponseRedirect` | admin.py 52 |

Evidence: after the state-changing POST, the view returns a redirect to `request.get_full_path()` instead of rendering a page.

### P8. Custom Manager (framework idiom), 1 instance: "Publication manager"

| Role | Participant | Location |
|---|---|---|
| Manager base | `django.db.models.Manager` | Django |
| Custom manager | `doc_manager.models.DocumentManager` | models.py 57–68 |
| Attachment | `DocumentModel.objects = DocumentManager()` | models.py 79 |

Evidence: table-level queries `published()` and `set_published()` are used by both the view (views.py 10) and the admin (admin.py 35).

### P9. Abstract Base Model (framework idiom), 1 instance: "Reusable document schema"

| Role | Participant | Location |
|---|---|---|
| Abstract model | `DocumentModel` (`Meta.abstract = True`) | models.py 71–91, 81–83 |
| Concrete model | not separately declared in `doc_manager` (the project supplies it) | — |

Evidence: `abstract = True` (82) means no table is created for this class. Fields, `ordering` and the manager are inherited by project subclasses.

## 2. Rejected candidates

| Candidate | Reason |
|---|---|
| Singleton | "One published document" is a data invariant enforced by a query, not a single instance of a class. |
| Factory Method / Simple Factory (`DocumentView.get`) | An inline `if/elif` only changes `content_type`; the class created is always `FileResponse`. |
| Decorator (`@csrf_protect_m`, admin.py 42) | A Python function wrapper supplied by Django; there are no Component or Decorator object roles in the app. |
| Command (`make_published`) | It has an admin-action signature but is not registered in `actions`; it is called directly. |
| Facade (`set_published`) | Two ORM calls do not hide a subsystem; this is already covered by P3b and P8. |
| Repository / Table Data Gateway | The manager returns Active Record objects; "Custom Manager" is the more accurate name. |
| Proxy (`FieldFile` behind `file_obj`) | Django internal; the app declares nothing. |
| Observer | There are no signals or receivers; `message_user` only stores a message. |
| Template Method via `model = None` (admin.py 18, views.py 6) | This is a configuration attribute, not an algorithm hook. On `ModelAdmin` it is also redundant, because `admin.register` passes the model to `__init__`. |
| Template-level Template Method (`{% extends %}`) | Not Python code; it is counted only as the Template role in P6. |
| AppConfig idiom (apps.py) | Purely declarative; no hook such as `ready()` is overridden. |
| GRASP Creator | No app class creates domain objects. |
| Front Controller | This is Django's URL resolver; no app code takes part. |

## 3. Totals

| Measure | Count |
|---|---|
| Distinct pattern types | **9** (Template Method, Strategy, Information Expert, Controller, Active Record, MVT, PRG, Custom Manager, Abstract Base Model) |
| Instances | **14** (3 + 2 + 2 + 2 + 1 + 1 + 1 + 1 + 1) |
| Concrete participant classes | **14** in total: 5 app classes (`ContentTypeRestrictedFileField`, `DocumentManager`, `DocumentModel`, `DocumentAdmin`, `DocumentView`) and 9 Django classes (`models.FileField`, `Manager`, `Model`, `ModelAdmin`, `View`, `FileExtensionValidator`, `FileInput`, `forms.FileField`, `HttpResponseRedirect`). `Widget` acts as an abstract Strategy role and is not counted. |