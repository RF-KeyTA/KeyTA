from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdminWithDoc
from keyta.admin.base_inline import AddInline
from keyta.apps.actions.models import Action, WindowAction
from keyta.apps.keywords.models import KeywordType
from keyta.apps.sequences.models import Sequence, WindowSequence
from keyta.forms.baseform import form_with_select

from apps.variables.models import Variable, WindowVariable
from apps.windows.models import Window


class Actions(AddInline):
    model = Action.windows.through
    extra = 0
    verbose_name = _('Aktion')
    verbose_name_plural = _('Aktionen')

    form = forms.modelform_factory(
        Action.windows.through,
        forms.ModelForm,
        ['keyword'],
        labels={
            'keyword': _('Aktion')
        }
    )

    related_field_name = 'keyword'
    related_field_model = WindowAction

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return (
            queryset
            .prefetch_related('keyword')
            .filter(keyword__type=KeywordType.ACTION)
            .order_by('keyword__name')
        )

    def related_field_widget_url_params(self, request):
        window_id = request.resolver_match.kwargs['object_id']
        window = Window.objects.get(pk=window_id)
        system_id = window.systems.first().pk

        return {
            'windows': window_id,
            'systems': system_id
        }

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return readonly_fields + ('system',)

    @admin.display(description=_('System'))
    def system(self, obj):
        return ', '.join(obj.keyword.systems.values_list('name', flat=True))

    def has_change_permission(self, request, obj=None) -> bool:
        return False


class Sequences(AddInline):
    model = Sequence.windows.through
    extra = 0
    verbose_name = _('Sequenz')
    verbose_name_plural = _('Sequenzen')

    form = forms.modelform_factory(
        Sequence.windows.through,
        forms.ModelForm,
        ['keyword'],
        labels={
            'keyword': _('Sequenz')
        }
    )

    related_field_name = 'keyword'
    related_field_model = WindowSequence

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return (
            queryset
            .prefetch_related('keyword')
            .filter(keyword__type=KeywordType.SEQUENCE)
            .order_by('keyword__name')
        )

    def related_field_widget_url_params(self, request):
        window_id = request.resolver_match.kwargs['object_id']
        window = Window.objects.get(pk=window_id)
        system_id = window.systems.first().pk

        return {
            'windows': window_id,
            'systems': system_id
        }

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return readonly_fields + ('system',)

    @admin.display(description=_('System'))
    def system(self, obj):
        return ', '.join(obj.keyword.systems.values_list('name', flat=True))

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


class Variables(AddInline):
    model = Variable.windows.through
    extra = 0
    verbose_name = _('Referenzwert')
    verbose_name_plural = _('Referenzwerte')

    form = forms.modelform_factory(
        Variable.windows.through,
        forms.ModelForm,
        ['variable'],
        labels={
            'variable': _('Referenzwert')
        }
    )

    related_field_name = 'variable'
    related_field_model = WindowVariable

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return (
            queryset
            .order_by('variable__name')
        )

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    @admin.display(description=_('System'))
    def system(self, obj):
        return ', '.join(obj.variable.systems.values_list('name', flat=True))

    def related_field_widget_url_params(self, request):
        window_id = request.resolver_match.kwargs['object_id']
        window = Window.objects.get(pk=window_id)
        system_id = window.systems.first().pk

        return {
            'windows': window_id,
            'systems': system_id
        }

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return readonly_fields + ('system',)


class BaseWindowAdmin(BaseAdminWithDoc):
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
        select_many=True
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
