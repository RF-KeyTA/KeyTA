import json
import logging

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.actions.models import Action, WindowAction
from apps.common.admin.base_admin import (
    BaseDocumentationAdmin,
    BaseAdminWithDoc
)
from apps.common.forms.baseform import form_with_select
from apps.keywords.models import KeywordType
from apps.sequences.models import Sequence, WindowSequence
from apps.variables.models import Variable, WindowVariable

from ..models import Window, WindowDocumentation

logger = logging.getLogger('django')


class CustomRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):
    def __init__(self, related_url, system_id, window_id, *args, **kwargs) -> None:
            self.related_url = related_url
            self.system_id = system_id
            self.window_id = window_id
            super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
            context = super().get_context(name, value, attrs)
            context['url_params'] += f'&systems={self.system_id}&windows={self.window_id}'
            return context
    
    def get_related_url(self, info, action, *args):
        return self.related_url


def related_field_widget_factory(related_url, system_id, window_id, base_widget):
    return CustomRelatedFieldWidgetWrapper(
        related_url,
        system_id,
        window_id,
        base_widget.widget,
        base_widget.rel,
        base_widget.admin_site
    )


class AddInline(admin.TabularInline):
    def formfield_for_dbfield(self, db_field, request: HttpRequest, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == self.related_field_name:
            window_id = request.resolver_match.kwargs['object_id']
            window = Window.objects.get(pk=window_id)
            system_id = window.systems.first().pk

            field.widget = related_field_widget_factory(
                self.related_field_widget_url(),
                system_id,
                window_id,
                field.widget
            )
            field.widget.can_change_related = False
            field.widget.can_view_related = False
            field.widget.attrs.update({
                'data-placeholder': _('Klicke auf das Plus-Symbol'),
                'disabled': True
            })

        return field

    def related_field_widget_url(self):
        app = self.related_model._meta.app_label
        model = self.related_model._meta.model_name

        return reverse('admin:%s_%s_add' % (app, model))


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

    related_model = WindowAction
    related_field_name = 'keyword'

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return (
            queryset
            .prefetch_related('keyword')
            .filter(keyword__type=KeywordType.ACTION)
            .order_by('keyword__name')
        )

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

    related_model = WindowSequence
    related_field_name = 'keyword'

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return (
            queryset
            .prefetch_related('keyword')
            .filter(keyword__type=KeywordType.SEQUENCE)
            .order_by('keyword__name')
        )


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

    related_model = WindowVariable
    related_field_name = 'variable'

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return (
            queryset
            .order_by('variable__name')
        )

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
        select_many=True
    )
    inlines = [
        Actions,
        Sequences,
        Variables
    ]

    def autocomplete_name(self, name: str):
        return json.dumps([
            '%s (%s)' % (name, systems)
            for name, systems in
            self.model.objects.values_list('name', 'systems__name')
            .filter(name__icontains=name)
        ])

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
