import logging

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.translation import gettext as _

from apps.actions.models import Action
from apps.common.admin.base_admin import (
    BaseDocumentationAdmin,
    BaseAdminWithDoc
)
from apps.common.forms.baseform import form_with_select
from apps.keywords.models import KeywordType
from apps.sequences.models import Sequence
from apps.variables.models import Variable

from ..models import Window, WindowDocumentation

logger = logging.getLogger('django')


class Actions(admin.TabularInline):
    model = Action.windows.through
    extra = 0
    max_num = 0
    verbose_name = _('Aktion')
    verbose_name_plural = _('Aktionen')

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return (
            queryset
            .prefetch_related('keyword')
            .filter(keyword__type=KeywordType.ACTION)
        )

    def has_change_permission(self, request, obj=None) -> bool:
        return False


class Sequences(admin.TabularInline):
    model = Sequence.windows.through
    extra = 0
    max_num = 0
    verbose_name = _('Sequenz')
    verbose_name_plural = _('Sequenzen')

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return (
            queryset
            .prefetch_related('keyword')
            .filter(keyword__type=KeywordType.SEQUENCE)
        )


class Variables(admin.TabularInline):
    model = Variable.windows.through
    extra = 0
    max_num = 0
    verbose_name = _('Referenzwert')
    verbose_name_plural = _('Referenzwerte')

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(Window)
class WindowAdmin(BaseAdminWithDoc):
    list_display = ['system_list', 'name', 'description']
    list_display_links = ['name']
    list_filter = ['systems']
    ordering = ['name']
    search_fields = ['name']
    search_help_text = _('Name')

    @admin.display(description=_('Systeme'))
    def system_list(self, obj: Window):
        return list(obj.systems.values_list('name', flat=True))

    fields = ['systems', 'name', 'description']
    form = form_with_select(
        Window,
        'systems',
        _('System hinzufügen'),
        True
    )
    inlines = [
        Actions,
        Sequences,
        Variables
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="",
                    extra_context=None):
        if '_to_field' in request.GET:
            window = Window.objects.get(id=object_id)
            return HttpResponseRedirect(window.get_docadmin_url())

        return super().change_view(request, object_id, form_url, extra_context)

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.fields + ['documentation']
        else:
            return self.fields + ['read_documentation']

    def get_inlines(self, request, obj):
        if not obj:
            return []

        return self.inlines

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return self.fields + ['read_documentation']


@admin.register(WindowDocumentation)
class WindowDocumentationAdmin(BaseDocumentationAdmin):
    pass
