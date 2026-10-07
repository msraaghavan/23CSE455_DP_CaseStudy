import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test import RequestFactory, TestCase, override_settings
from doc_manager.views import DocumentView
from tests.models import TestModel

MEDIA_ROOT = tempfile.mkdtemp()


class TestView(DocumentView):
    model = TestModel


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class DocumentViewTestClass(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def publish(self, name):
        doc = TestModel.objects.create(
            file_obj=SimpleUploadedFile(name, b'content')
        )
        TestModel.objects.set_published(doc.pk)
        return doc

    def get_page(self):
        request = RequestFactory().get('/see_document/')
        response = TestView.as_view()(request)
        response.close()
        return response

    def test_pdf_document(self):
        self.publish('policy.pdf')
        self.assertEqual(self.get_page()['Content-Type'], 'application/pdf')

    def test_html_document(self):
        self.publish('policy.html')
        self.assertEqual(self.get_page()['Content-Type'], 'text/html')

    def test_nothing_published(self):
        with self.assertRaises(Http404):
            self.get_page()

    def test_txt_document(self):
        self.publish('notice.txt')
        self.assertEqual(self.get_page()['Content-Type'], 'text/plain')

    def test_capital_letters_extension(self):
        self.publish('POLICY.PDF')
        self.assertEqual(self.get_page()['Content-Type'], 'application/pdf')

    def test_other_file_type_gives_404(self):
        self.publish('program.exe')
        with self.assertRaises(Http404):
            self.get_page()
