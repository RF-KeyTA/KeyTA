from django.http import HttpRequest

from ..models import WindowKeyword
from .keyword import KeywordAdmin


class WindowKeywordAdminMixin:
    def save_model(self, request: HttpRequest, obj, form, change):
        super().save_model(request, obj, form, change)
        keyword: WindowKeyword = obj

        if not change:
            form.save_m2m()

        if not getattr(keyword, 'execution', None):
            keyword.create_execution(request.user)


class WindowKeywordAdmin(WindowKeywordAdminMixin, KeywordAdmin):
    list_display = ['name', 'short_doc']
    list_filter = ['systems', 'windows']

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return super().changeform_view(request, object_id, form_url, extra_context)
