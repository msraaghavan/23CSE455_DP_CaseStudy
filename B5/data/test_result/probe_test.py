"""Probe tests for Part 1: small checks that prove the pattern roles we claim.

They run against the ORIGINAL code (data/code) and do not change it.
Run from the folder B5/data/code:
    python ../test_result/probe_test.py
"""
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.getcwd())                       # data/code
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")

import django  # noqa: E402

django.setup()

from django.contrib.admin.sites import AdminSite  # noqa: E402
from django.core.exceptions import FieldError, ValidationError  # noqa: E402
from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: E402
from django.core.validators import FileExtensionValidator  # noqa: E402
from django.test import RequestFactory, TestCase, override_settings  # noqa: E402

from doc_manager.models import ContentTypeRestrictedFileField  # noqa: E402
from doc_manager.views import DocumentView  # noqa: E402
from tests.admin import TestAdmin  # noqa: E402
from tests.models import TestModel  # noqa: E402
from tests.test_admin import FakeUser  # noqa: E402
from tests.test_models import TestValue  # noqa: E402

MEDIA = tempfile.mkdtemp()


class PageView(DocumentView):          # same as example/our_app/views.py
    model = TestModel


@override_settings(MEDIA_ROOT=MEDIA)
class ProbeTests(TestCase):

    def publish(self, name, content=b"hello"):
        doc = TestModel.objects.create(file_obj=SimpleUploadedFile(name, content))
        TestModel.objects.set_published(doc.pk)
        return doc

    # Instance 1 - Template Method "Published Document Page"
    def test_1_dispatch_calls_the_get_step(self):
        self.publish("policy.html")
        request = RequestFactory().get("/see_document/")
        with mock.patch.object(PageView, "get", wraps=PageView().get) as step:
            response = PageView.as_view()(request)
        self.assertEqual(step.call_count, 1)          # dispatch() called our get()
        self.assertEqual(response["Content-Type"], "text/html")
        response.close()

    def test_1_dispatch_refuses_other_methods(self):
        response = PageView.as_view()(RequestFactory().post("/see_document/"))
        self.assertEqual(response.status_code, 405)    # fixed part of the recipe

    # Instance 2 - Template Method "Admin Edit Page Rules"
    def test_2_admin_recipe_calls_the_hook(self):
        admin = TestAdmin(model=TestModel, admin_site=AdminSite())
        request = RequestFactory().get("")
        request.user = FakeUser()
        with mock.patch.object(TestAdmin, "get_readonly_fields",
                               wraps=admin.get_readonly_fields) as hook:
            response = admin.changeform_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(hook.call_count, 1)    # Django asked our hook

    # Instance 3 - Strategy "Upload File Checks"
    def test_3_field_holds_a_validator_strategy(self):
        field = ContentTypeRestrictedFileField(upload_to="documents/")
        names = [type(v).__name__ for v in field.validators]
        self.assertEqual(names, ["FileExtensionValidator"])
        self.assertEqual(field.validators[0].allowed_extensions, ["pdf", "html"])

    def test_3_the_strategy_rejects_txt(self):
        field = ContentTypeRestrictedFileField(upload_to="documents/")
        with self.assertRaises(ValidationError) as error:
            field.clean(TestValue("test.txt", "text/plain", 10), "")
        self.assertEqual(error.exception.error_list[0].code, "invalid_extension")

    def test_3_swapping_the_strategy_changes_the_rule(self):
        field = ContentTypeRestrictedFileField(upload_to="documents/")
        field._validators = [FileExtensionValidator(["txt"])]      # swap it
        with self.assertRaises(ValidationError) as error:
            field.clean(TestValue("test.pdf", "application/pdf", 10), "")
        self.assertEqual(error.exception.error_list[0].code, "invalid_extension")

    # Instance 4 - Strategy "Upload Widget Choice" (found by the Part 1 LLM run)
    def test_4_admin_swaps_the_upload_widget(self):
        admin = TestAdmin(model=TestModel, admin_site=AdminSite())
        form = admin.get_form(RequestFactory().get(""))
        widget = form.base_fields["file_obj"].widget
        self.assertEqual(type(widget).__name__, "FileInput")       # chosen by the app
        self.assertIn("application/pdf", str(widget.attrs["accept"]))

    def test_4_without_the_choice_django_uses_its_default_widget(self):
        class PlainAdmin(TestAdmin):
            formfield_overrides = {}
        admin = PlainAdmin(model=TestModel, admin_site=AdminSite())
        form = admin.get_form(RequestFactory().get(""))
        self.assertEqual(type(form.base_fields["file_obj"].widget).__name__, "AdminFileWidget")

    # Findings (not patterns): two small bugs in the original code
    def test_finding_admin_search_uses_a_wrong_field_name(self):
        admin = TestAdmin(model=TestModel, admin_site=AdminSite())
        self.assertEqual(admin.search_fields, ["file"])   # the field is file_obj
        with self.assertRaises(FieldError):              # typing in the search box
            admin.get_search_results(None, TestModel.objects.all(), "policy")

    def test_finding_view_crashes_for_other_file_types(self):
        self.publish("notes.txt")            # saved without form validation
        request = RequestFactory().get("/see_document/")
        with self.assertRaises(UnboundLocalError):
            PageView.as_view()(request)


if __name__ == "__main__":
    from django.conf import settings
    from django.test.utils import get_runner

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    failures = get_runner(settings)(verbosity=2).run_tests(["probe_test"])
    shutil.rmtree(MEDIA, ignore_errors=True)
    sys.exit(bool(failures))
