from django.views import View
from django.http import Http404, FileResponse

from .models import FILE_TYPES


class DocumentView(View):
    model = None

    def get(self, request):
        """Returns currently published file."""
        document_model = self.model.objects.published()
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
