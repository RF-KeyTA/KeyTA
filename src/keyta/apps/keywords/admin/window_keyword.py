from django.http import HttpRequest

from keyta.admin.list_filters import SystemListFilter, WindowListFilter

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
    list_filter = [
        ('systems', SystemListFilter),
        ('windows', WindowListFilter)
    ]

    change_form_template = 'window_keyword_change_form.html'

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_protected_objects(self, obj):
        keyword: WindowKeyword = obj
        return keyword.uses.filter(execution__isnull=True)
