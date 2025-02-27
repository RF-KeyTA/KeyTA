from django import forms
from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.actions.models import ActionQuickAdd
from keyta.apps.keywords.models import KeywordWindowRelation
from keyta.apps.sequences.models import SequenceQuickAdd
from keyta.forms.baseform import form_with_select
from keyta.widgets import CustomRelatedFieldWidgetWrapper

from apps.variables.models import (
    VariableQuickAdd,
    VariableSchemaQuickAdd,
    VariableWindowRelation
)
from apps.windows.models import Window, WindowDocumentation, WindowSchemaRelation


class QuickAddMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == self.quick_add_field:
            app = self.quick_add_model._meta.app_label
            model = self.quick_add_model._meta.model_name
            quick_add_url = reverse('admin:%s_%s_add' % (app, model))   

            field.widget = self.wrap_related_field_widget(
                field.widget,
                quick_add_url,
                self.quick_add_url_params(request)
            )

        return field

    def quick_add_url_params(self, request: HttpRequest):
        window_id = request.resolver_match.kwargs['object_id']
        window = Window.objects.get(pk=window_id)
        system_id = window.systems.first().pk

        return {
            'windows': window_id,
            'systems': system_id
        }

    def wrap_related_field_widget(self, widget, quick_add_url, quick_add_url_params):
        wrapped_widget = CustomRelatedFieldWidgetWrapper(
            widget,
            quick_add_url,
            quick_add_url_params
        )
        wrapped_widget.attrs.update({
            'data-placeholder': _('Klicke auf das Plus-Symbol'),
            'data-width': '95%',
            'disabled': True,
        })

        return wrapped_widget


class WindowKeywordInline(BaseTabularInline):
    model = KeywordWindowRelation
    readonly_fields = ['systems']
    
    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .prefetch_related('keyword')
            .order_by('keyword__name')
        )

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    @admin.display(description=_('Systeme'))
    def systems(self, obj: KeywordWindowRelation):
        return ', '.join(obj.keyword.systems.values_list('name', flat=True))


class Actions(QuickAddMixin, WindowKeywordInline):
    form = forms.modelform_factory(
        KeywordWindowRelation,
        fields=['keyword'],
        labels={
            'keyword': _('Aktion')
        }
    )
    quick_add_field = 'keyword'
    quick_add_model = ActionQuickAdd
    verbose_name = _('Aktion')
    verbose_name_plural = _('Aktionen')

    def get_queryset(self, request):
        return super().get_queryset(request).actions()


class Sequences(QuickAddMixin, WindowKeywordInline):
    form = forms.modelform_factory(
        KeywordWindowRelation,
        fields=['keyword'],
        labels={
            'keyword': _('Sequenz')
        }
    )
    quick_add_field = 'keyword'
    quick_add_model = SequenceQuickAdd
    verbose_name = _('Sequenz')
    verbose_name_plural = _('Sequenzen')

    def get_queryset(self, request):
        return super().get_queryset(request).sequences()


class Variables(QuickAddMixin, BaseTabularInline):
    model = VariableWindowRelation
    form = forms.modelform_factory(
        VariableWindowRelation,
        fields=['variable'],
        labels={
            'variable': _('Referenzwert')
        }
    )
    quick_add_field = 'variable'
    quick_add_model = VariableQuickAdd
    readonly_fields = ['systems']
    verbose_name = _('Referenzwert')
    verbose_name_plural = _('Referenzwerte')

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .exclude(variable__in_list__isnull=False)
            .order_by('variable__name')
    )

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def quick_add_url_params(self, request: HttpRequest):
        window_id = request.resolver_match.kwargs['object_id']
        window = Window.objects.get(pk=window_id)
        system_id = window.systems.first().pk

        query_params = {
            'windows': window_id,
            'systems': system_id
        }

        if schema := window.schemas.first():
            return query_params | {'schema': schema.pk}

        return  query_params

    @admin.display(description=_('System'))
    def systems(self, obj):
        return ', '.join(obj.variable.systems.values_list('name', flat=True))


class Schemas(QuickAddMixin, BaseTabularInline):
    model = WindowSchemaRelation
    form = forms.modelform_factory(
        WindowSchemaRelation,
        fields=['variableschema'],
        labels={
            'variableschema': _('Schema')
        }
    )

    quick_add_field = 'variableschema'
    quick_add_model = VariableSchemaQuickAdd

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def quick_add_url_params(self, request: HttpRequest):
        window_id = request.resolver_match.kwargs['object_id']

        return {
            'windows': window_id,
        }


class BaseWindowAdmin(BaseAdmin):
    list_display = ['system_list', 'name', 'description']
    list_display_links = ['name']
    list_filter = ['systems']
    ordering = ['name']
    search_fields = ['name']
    search_help_text = _('Name')

    @admin.display(description=_('Systeme'))
    def system_list(self, window: Window):
        return list(window.systems.values_list('name', flat=True))

    fields = ['systems', 'name', 'description', 'documentation']
    form = form_with_select(
        Window,
        'systems',
        _('System hinzufügen'),
        select_many=True
    )
    inlines = [
        Actions,
        Sequences,
        Variables,
        Schemas
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        if '_to_field' in request.GET:
            window_doc = WindowDocumentation.objects.get(id=object_id)
            return HttpResponseRedirect(window_doc.get_admin_url())

        return super().change_view(request, object_id, form_url, extra_context)

    def get_inlines(self, request, obj):
        if not obj:
            return []

        return self.inlines
