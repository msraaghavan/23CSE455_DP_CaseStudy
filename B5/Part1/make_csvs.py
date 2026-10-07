"""Builds the pattern CSV files of Part 1 and Part 2.

Writes:  Part1/patterns.csv          (original code)
         Part1/Pattern_count.csv     (counts for the original code)
         Part2/pattern_evalution.csv (original code + after Change 1, 2, 3)
         Part2/Pattern_count.csv     (counts for all four versions)
File names follow the "Complete repository hierarchy" of the instructions.

The pattern records are written once, in the table INSTANCES below.
Line ranges are never typed by hand: the app's classes/methods are found in the saved
code with Python's ast module, and Django's with the inspect module (Django 4.1.13).

Run from the B5 folder:   python Part1/make_csvs.py
"""
import ast
import csv
import inspect
import os
from collections import Counter

import django
from django.contrib.admin import options
from django.core import validators
from django.db.models import fields as model_fields
from django.forms import boundfield, widgets
from django.forms import fields as form_fields
from django.views.generic import base

VERSIONS = {
    "original": "data/code",
    "after_change1": "Part2/changes/Change1/code",
    "after_change2": "Part2/changes/Change2/code",
    "after_change3": "Part2/code",
}

DJANGO = {  # name used in the CSV -> Django object
    "django.views.View": base.View,
    "View.dispatch": base.View.dispatch,
    "django.contrib.admin.ModelAdmin": options.ModelAdmin,
    "ModelAdmin._changeform_view": options.ModelAdmin._changeform_view,
    "ModelAdmin.get_form": options.ModelAdmin.get_form,
    "BaseModelAdmin.get_readonly_fields": options.BaseModelAdmin.get_readonly_fields,
    "BaseModelAdmin.formfield_for_dbfield": options.BaseModelAdmin.formfield_for_dbfield,
    "Field.run_validators": model_fields.Field.run_validators,
    "Field.clean": model_fields.Field.clean,
    "django.core.validators.FileExtensionValidator": validators.FileExtensionValidator,
    "django.forms.FileField": form_fields.FileField,
    "BoundField.as_widget": boundfield.BoundField.as_widget,
    "django.forms.widgets.Widget": widgets.Widget,
    "django.forms.widgets.FileInput": widgets.FileInput,
}

# One record per pattern instance.  A role is (role name, symbol, note).
# symbol = "file.py:Name" for app code, a DJANGO key, or None (not separately declared).
INSTANCES = {
    "Published Document Page": {
        "pattern": "Template Method",
        "roles": [
            ("AbstractClass", "django.views.View", ""),
            ("TemplateMethod", "View.dispatch", "fixed recipe: call the method named after the HTTP verb, else 405"),
            ("PrimitiveOperation", None, "get(): not separately declared in View, dispatch finds it by name"),
            ("ConcreteClass", "views.py:DocumentView", ""),
            ("ConcreteOperation", "views.py:DocumentView.get", "returns the file of the document"),
            ("ConcreteClass", "views.py:DocumentVersionView", "from Change 2: inherits DocumentView.get"),
        ],
        "evidence": "Problem: every page must answer GET and refuse other HTTP methods in the same way. "
                    "Django's View.dispatch is the fixed recipe: it calls the method named after the HTTP verb "
                    "and otherwise returns 405. The app fills in only the get step: DocumentView.get finds the "
                    "published document and returns its file. Proof: data/test_result/probe_test.py "
                    "test_1_* (dispatch called get once; a POST got 405).",
    },
    "Admin Read-only Fields": {
        "pattern": "Template Method",
        "roles": [
            ("AbstractClass", "django.contrib.admin.ModelAdmin", ""),
            ("TemplateMethod", "ModelAdmin._changeform_view", "builds the edit page and calls get_readonly_fields"),
            ("TemplateMethod", "ModelAdmin.get_form", "builds the form and calls get_readonly_fields"),
            ("Hook (default)", "BaseModelAdmin.get_readonly_fields", ""),
            ("ConcreteClass", "admin.py:DocumentAdmin", ""),
            ("ConcreteHook", "admin.py:DocumentAdmin.get_readonly_fields", "locks fields of saved documents"),
        ],
        "evidence": "Problem: the admin edit page is built by a long fixed recipe; the app only needs to say "
                    "which fields are locked. ModelAdmin._changeform_view and ModelAdmin.get_form call "
                    "self.get_readonly_fields(request, obj); DocumentAdmin overrides this hook so that a saved "
                    "document shows add_date, pub_date and published as read-only. Proof: "
                    "tests/test_admin.py test_get_readonly_fields; probe test_2_admin_recipe_calls_the_hook.",
    },
    "Upload File Checks": {
        "pattern": "Strategy",
        "roles": [
            ("Context", "Field.run_validators", "loops over self.validators and calls each one, called by Field.clean"),
            ("Context (subclass)", "models.py:ContentTypeRestrictedFileField", "clean() calls super().clean()"),
            ("Context (subclass)", "models.py:ContentTypeRestrictedFileField.clean", ""),
            ("Strategy", None, "not separately declared: any callable validator(value) that raises ValidationError"),
            ("ConcreteStrategy", "django.core.validators.FileExtensionValidator", ""),
            ("Client", "models.py:ContentTypeRestrictedFileField.__init__", "creates the strategy and plugs it in"),
            ("Configuration", "models.py:FILE_TYPES", "from Change 1: the allowed extensions"),
        ],
        "evidence": "Problem: uploads must be checked by rules that can be swapped without changing the field. "
                    "Django's Field.run_validators loops over self.validators and calls each one the same way "
                    "(validator(value)). ContentTypeRestrictedFileField.__init__ plugs in a FileExtensionValidator "
                    "for pdf and html. Proof: probe test_3_* (the field holds the validator; it rejects test.txt "
                    "with code invalid_extension; swapping in another validator changes the rule).",
    },
    "Upload Widget Choice": {
        "pattern": "Strategy",
        "roles": [
            ("Context", "django.forms.FileField", "draws itself through its widget"),
            ("Context", "BoundField.as_widget", "calls widget.render(...)"),
            ("Strategy", "django.forms.widgets.Widget", ""),
            ("ConcreteStrategy", "django.forms.widgets.FileInput", ""),
            ("Client", "admin.py:DocumentAdmin.formfield_overrides", "chooses FileInput for every FileField"),
            ("Client", "BaseModelAdmin.formfield_for_dbfield", "applies formfield_overrides"),
            ("Configuration", "models.py:FILE_TYPES", "from Change 1: the accept value"),
        ],
        "evidence": "Problem: the admin should use a plain upload box instead of Django's default one. A form "
                    "field draws itself through its widget object (BoundField.as_widget calls widget.render), and "
                    "widgets are interchangeable. DocumentAdmin.formfield_overrides makes "
                    "BaseModelAdmin.formfield_for_dbfield use FileInput (with an accept list) for every FileField. "
                    "Proof: probe test_4_* (widget is FileInput; without the override Django uses AdminFileWidget).",
    },
    "Document Choice Step": {
        "pattern": "Template Method",
        "roles": [
            ("AbstractClass", "views.py:DocumentView", "also gives the default step: the published version"),
            ("TemplateMethod", "views.py:DocumentView.get", "recipe: get_document(), 404 if none, pick type, send file"),
            ("PrimitiveOperation", "views.py:DocumentView.get_document", "default: the published version"),
            ("ConcreteClass", "views.py:DocumentVersionView", ""),
            ("ConcreteOperation", "views.py:DocumentVersionView.get_document", "the published-at-some-time version with the id from the URL"),
        ],
        "evidence": "Problem: show any saved version without copying the file-sending code. DocumentView.get is "
                    "now a fixed recipe: get_document(), 404 if none, pick the content type, send the file. "
                    "DocumentVersionView overrides only get_document() (the version with this id, if it was ever "
                    "published). Proof: tests/test_version_view.py (old version shown; draft and unknown id give 404) "
                    "and tests/test_views.py.",
    },
}

# What happened to each instance in each version: (status, change description).
EVOLUTION = {
    "original": {name: ("baseline", "Original code.") for name in
                 ["Published Document Page", "Admin Read-only Fields", "Upload File Checks", "Upload Widget Choice"]},
    "after_change1": {
        "Published Document Page": ("modified", "DocumentView.get looks the content type up in FILE_TYPES instead of "
                                    "an if/elif chain, compares in lower case and gives 404 for unknown types. Roles unchanged."),
        "Admin Read-only Fields": ("preserved", "Not changed (lines moved by a new import)."),
        "Upload File Checks": ("modified", "The ConcreteStrategy FileExtensionValidator is now built from the new "
                               "FILE_TYPES table and also allows txt."),
        "Upload Widget Choice": ("modified", "FileInput's accept value now comes from FILE_TYPES and is a "
                                 "comma-separated string (before: a Python list that browsers ignore)."),
    },
    "after_change2": {
        "Published Document Page": ("extended", "New ConcreteClass DocumentVersionView; it inherits DocumentView.get, "
                                    "which now accepts the URL arguments."),
        "Admin Read-only Fields": ("preserved", "Not changed."),
        "Upload File Checks": ("preserved", "Not changed."),
        "Upload Widget Choice": ("preserved", "Not changed."),
        "Document Choice Step": ("newly_introduced", "Extract Method moved 'which document?' into "
                                 "DocumentView.get_document(); DocumentVersionView overrides it. This new "
                                 "collaboration lives inside Published Document Page."),
    },
    "after_change3": {
        "Published Document Page": ("preserved", "Not changed."),
        "Admin Read-only Fields": ("modified", "The hook DocumentAdmin.get_readonly_fields also returns file_obj "
                                   "for a version that has been published."),
        "Upload File Checks": ("preserved", "Not changed."),
        "Upload Widget Choice": ("preserved", "Not changed."),
        "Document Choice Step": ("preserved", "Not changed."),
    },
}


def app_range(folder, symbol):
    """'views.py:DocumentView.get' -> 'data/code/doc_manager/views.py:14-26' (None if absent)."""
    file_name, dotted = symbol.split(":")
    path = f"{folder}/doc_manager/{file_name}"
    with open(path, encoding="utf-8") as f:
        nodes = ast.parse(f.read()).body
    node = None
    for part in dotted.split("."):
        node = next((n for n in nodes if getattr(n, "name", None) == part
                     or (isinstance(n, ast.Assign) and n.targets[0].id == part)), None)
        if node is None:
            return None
        nodes = getattr(node, "body", [])
    return f"{path}:{node.lineno}-{node.end_lineno}"


def django_range(name):
    obj = DJANGO[name]
    lines, start = inspect.getsourcelines(obj)
    path = inspect.getsourcefile(obj).replace(os.sep, "/").split("site-packages/")[1]
    return f"Django {django.get_version()} {path}:{start}-{start + len(lines) - 1}"


USED = {}  # (version, instance) -> [(role, symbol)], for the counts printed below


def record(version, name):
    folder = VERSIONS[version]
    roles, places, used = [], [], []
    for role, symbol, note in INSTANCES[name]["roles"]:
        if symbol is None:
            roles.append(f"{role}={note}")
            continue
        where = django_range(symbol) if symbol in DJANGO else app_range(folder, symbol)
        if where is None:            # symbol does not exist yet in this version
            continue
        label = symbol.split(":")[-1]
        roles.append(f"{role}={label}" + (f" ({note})" if note else ""))
        places.append(f"{label}: {where}")
        used.append((role, label))
    USED[version, name] = used
    return {
        "source_version": version,
        "pattern_name": INSTANCES[name]["pattern"],
        "pattern_type": "Behavioral (GoF)",
        "instance_name": name,
        "participant_roles": "; ".join(roles),
        "source_locations": "; ".join(places),
        "intent_and_evidence": INSTANCES[name]["evidence"],
    }


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)


evolution, counts = [], []
for version, statuses in EVOLUTION.items():
    for name, (status, description) in statuses.items():
        evolution.append({**record(version, name), "status_after_change": status,
                          "change_description": description})
    current = [n for n, (s, _) in statuses.items() if s != "removed"]
    per_pattern = Counter(INSTANCES[n]["pattern"] for n in current)
    for pattern, number in sorted(per_pattern.items()):
        counts.append({"source_version": version, "summary": "per_pattern",
                       "pattern_name": pattern, "count": number})
    counts.append({"source_version": version, "summary": "total_pattern_types",
                   "pattern_name": "", "count": len(per_pattern)})
    counts.append({"source_version": version, "summary": "total_pattern_instances",
                   "pattern_name": "", "count": len(current)})

    # numbers for the report: concrete classes and unique participant symbols
    used = [pair for n in current for pair in USED[version, n]]
    symbols = {symbol for _, symbol in used}
    concrete = {symbol for role, symbol in used if role in ("ConcreteClass", "ConcreteStrategy")}
    print(f"{version}: instances={len(current)} types={len(per_pattern)} "
          f"concrete classes={len(concrete)} {sorted(concrete)} unique symbols={len(symbols)}")

write("Part1/patterns.csv", [{k: v for k, v in r.items() if k not in ("status_after_change", "change_description")}
                             for r in evolution if r["source_version"] == "original"])
write("Part1/Pattern_count.csv", [row for row in counts if row["source_version"] == "original"])
write("Part2/pattern_evalution.csv", evolution)
write("Part2/Pattern_count.csv", counts)
print("wrote Part1/patterns.csv, Part1/Pattern_count.csv, Part2/pattern_evalution.csv, Part2/Pattern_count.csv")
