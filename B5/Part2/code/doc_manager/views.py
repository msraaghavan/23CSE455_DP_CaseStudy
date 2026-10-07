from django.views import View
from django.http import Http404, FileResponse

from .models import FILE_TYPES


class DocumentView(View):
    model = None

    def get_document(self):
        """Returns the document to show: the published one."""
        return self.model.objects.published()

    def get(self, request, *args, **kwargs):
        """Returns the file of the document chosen by get_document()."""
        document_model = self.get_document()
        if document_model is None:
            raise Http404
        file = document_model.file_obj
        if file is None:
            raise Http404
        extension = document_model.filename().rsplit('.', 1)[-1].lower()
        if extension not in FILE_TYPES:
            raise Http404
        return FileResponse(file, as_attachment=False,
                            content_type=FILE_TYPES[extension])


class DocumentVersionView(DocumentView):
    """Shows an older version, chosen by its id in the URL (pk).
    Drafts that were never published stay hidden."""

    def get_document(self):
        return self.model.objects.filter(
            pk=self.kwargs['pk'], pub_date__isnull=False
        ).first()
