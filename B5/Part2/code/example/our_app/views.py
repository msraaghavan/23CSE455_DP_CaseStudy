from doc_manager.views import DocumentView, DocumentVersionView

from .models import OurModel


class OurView(DocumentView):
    model = OurModel


class OurVersionView(DocumentVersionView):
    model = OurModel
