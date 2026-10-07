import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test import RequestFactory, TestCase, override_settings
from doc_manager.views import DocumentVersionView
from tests.models import TestModel

MEDIA_ROOT = tempfile.mkdtemp()


class TestVersionView(DocumentVersionView):
    model = TestModel


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class DocumentVersionViewTestClass(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def add_version(self, name):
        return TestModel.objects.create(
            file_obj=SimpleUploadedFile(name, b'content')
        )

    def get_page(self, pk):
        request = RequestFactory().get('/see_document/%s/' % pk)
        response = TestVersionView.as_view()(request, pk=pk)
        response.close()
        return response

    def test_old_version(self):
        old = self.add_version('policy_2022.html')
        TestModel.objects.set_published(old.pk)
        new = self.add_version('policy_2023.pdf')
        TestModel.objects.set_published(new.pk)
        self.assertEqual(self.get_page(old.pk)['Content-Type'], 'text/html')

    def test_draft_gives_404(self):
        draft = self.add_version('policy_draft.pdf')
        with self.assertRaises(Http404):
            self.get_page(draft.pk)

    def test_unknown_version_gives_404(self):
        with self.assertRaises(Http404):
            self.get_page(999)
