from django.contrib import admin, messages
from django.contrib.admin.options import (
                                            unquote,
                                            csrf_protect_m,
                                            HttpResponseRedirect,
                                            )
from django.utils.translation import gettext as _
from django.forms.widgets import FileInput
from django.db.models import FileField

from .models import FILE_TYPES


class DocumentAdmin(admin.ModelAdmin):
    """Admin class for publishing documents with a 'Publish' button."""
    exclude = ('pub_date', 'published')
    change_form_template = 'admin_change_form_documents.html'
    list_display = ('filename', 'add_date', 'pub_date', 'published')
    ordering = ['-published', 'pub_date']
    model = None
    search_fields = ['file']
    list_filter = ['add_date']
    formfield_overrides = {
        FileField: {
            'widget': FileInput(attrs={'accept': ','.join(FILE_TYPES.values())})
        },
    }

    def get_readonly_fields(self, request, obj=None):
        if obj:
            fields = self.readonly_fields + ('add_date', 'pub_date', 'published')
            if obj.pub_date:
                # once published, the file is history: upload a new version
                fields += ('file_obj',)
            return fields
        return self.readonly_fields

    def make_published(self, request, document):
        """Publishes the given document."""
        if document:
            self.model.objects.set_published(document.pk)
            self.message_user(request, _(
                "Document published"), messages.SUCCESS)
        else:
            self.message_user(request, _(
                "Document not published"), messages.ERROR)

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='',
                        extra_context=None):
        """
        If method is POST publishes document with id equal to object_id
        and if method is GET redirects to admin view of document.
        """
        if request.method == 'POST' and '_make_published' in request.POST:
            obj = self.get_object(request, unquote(object_id))
            self.make_published(request, obj)
            return HttpResponseRedirect(request.get_full_path())

        return admin.ModelAdmin.changeform_view(
            self, request,
            object_id=object_id,
            form_url=form_url,
            extra_context=extra_context,
        )
