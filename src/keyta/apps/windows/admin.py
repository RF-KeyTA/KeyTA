from django import forms
from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_admin import BaseAdmin, BaseQuickAddAdmin, QuickAddMixin, BaseDocumentationAdmin
from keyta.admin.base_inline import BaseTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.admin.field_documentation import DocumentationField
from keyta.admin.list_filters import SystemListFilter
from keyta.apps.actions.models import ActionQuickAdd
from keyta.apps.keywords.models import KeywordWindowRelation
from keyta.apps.resources.admin import ResourceImportsInline
from keyta.apps.resources.models import Resource, ResourceImport
from keyta.apps.sequences.models import SequenceQuickAdd
from keyta.apps.variables.models import (
    VariableQuickAdd,
    VariableSchemaQuickAdd,
    VariableWindowRelation
)
from keyta.forms.baseform import form_with_select, BaseForm
from keyta.widgets import Icon, open_link_in_modal

from .models import (
    Window,
    WindowDocumentation,
    WindowQuickChange,
    WindowSchemaRelation, WindowQuickAdd,
)


class WindowQuickAddMixin(QuickAddMixin):
    def quick_add_url_params(self, request: HttpRequest, url_params: dict):
        window_id = request.resolver_match.kwargs['object_id']
        window = Window.objects.get(pk=window_id)
        system_id = window.systems.first().pk
        tab_url = window.get_tab_url(getattr(self, 'tab_name', None))

        # ref has to be the last key in the dictionary in order for the form
        # fields to be automatically filled with the values in the query params
        return {
            'windows': window_id,
            'systems': system_id,
            **url_params,
            'ref': request.path + tab_url
        }


class WindowKeywordInline(BaseTabularInline):
    model = KeywordWindowRelation
    readonly_fields = ['systems']
    
    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .prefetch_related('keyword')
            .order_by('keyword__name')
        )

    @admin.display(description=_('Systeme'))
    def systems(self, obj: KeywordWindowRelation):
        return ', '.join(obj.keyword.systems.values_list('name', flat=True))


class Resources(DeleteRelatedField, ResourceImportsInline):
    fk_name = 'window'
    fields = ['resource']
    form = form_with_select(
        ResourceImport,
        'resource',
        _('Ressource auswählen')
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        window: Window = obj

        imported_resources = (
            self.get_queryset(request)
            .filter(window_id=window.pk)
            .values_list('resource_id', flat=True)
        )
        resource_field = formset.form.base_fields['resource']
        resource_field.queryset = resource_field.queryset.exclude(id__in=imported_resources)

        return formset

    def get_max_num(self, request, obj=None, **kwargs):
        return Resource.objects.count()


class Actions(WindowQuickAddMixin, WindowKeywordInline):
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


class Actions(WindowQuickAddMixin, WindowKeywordInline):
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


class Sequences(WindowQuickAddMixin, WindowKeywordInline):
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


class Variables(WindowQuickAddMixin, BaseTabularInline):
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

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .exclude(variable__in_list__isnull=False)
            .order_by('variable__name')
    )

    def quick_add_url_params(self, request: HttpRequest, url_params: dict):
        window_id = request.resolver_match.kwargs['object_id']
        window = Window.objects.get(pk=window_id)

        if schema := window.schemas.first():
            return super().quick_add_url_params(request, {'schema': schema.pk})

        return {}

    @admin.display(description=_('Systeme'))
    def systems(self, obj):
        return ', '.join(obj.variable.systems.values_list('name', flat=True))


class Schemas(WindowQuickAddMixin, BaseTabularInline):
    model = WindowSchemaRelation
    form = form_with_select(
        WindowSchemaRelation,
        'variableschema',
        'Placeholder',
        labels={
            'variableschema': _('Datenvorlage')
        },
        can_add_related=True
    )
    quick_add_field = 'variableschema'
    quick_add_model = VariableSchemaQuickAdd


class WindowForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        systems = self.cleaned_data.get('systems')
        window_systems = [
            system.name
            for system in self.initial.get('systems', [])
        ]

        if system := systems.exclude(name__in=window_systems).filter(windows__name=name).first():
            raise forms.ValidationError(
                {
                    "name": _(f'Eine Maske mit diesem Namen existiert bereits im System "{system}"')
                }
            )


@admin.register(Window)
class WindowAdmin(DocumentationField, BaseAdmin):
    list_display = ['name', 'preview', 'system_list']
    list_display_links = ['name']
    list_filter = [
        ('systems', SystemListFilter),
    ]
    list_per_page = 10
    search_fields = ['name']
    search_help_text = _('Name')

    @admin.display(description=_('Vorschau'))
    def preview(self, window: Window):
        return open_link_in_modal(
            WindowDocumentation.objects.get(id=window.pk).get_admin_url(),
            str(Icon(settings.FA_ICONS.preview, {'font-size': '18px'}))
        )

    fields = ['systems', 'name', 'description']
    form = form_with_select(
        Window,
        'systems',
        _('System hinzufügen'),
        form_class=WindowForm,
        select_many=True
    )
    inlines = [
        Actions,
        Sequences,
        Variables,
    ]

    @admin.display(description=_('Systeme'))
    def system_list(self, window: Window):
        return ', '.join(
            window.systems.values_list('name', flat=True)
        )

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        if 'quick_change' in request.GET:
            window = WindowQuickChange.objects.get(pk=object_id)
            return HttpResponseRedirect(window.get_admin_url())

        if 'view' in request.GET:
            window_doc = WindowDocumentation.objects.get(id=object_id)
            return HttpResponseRedirect(window_doc.get_admin_url())

        return super().change_view(request, object_id, form_url, extra_context)

    def get_inlines(self, request, obj):
        if not obj:
            return []

        if Resource.objects.count():
            return [Resources] + self.inlines + [Schemas]
        else:
            return self.inlines + [Schemas]

    def has_delete_permission(self, request, obj=None):
        window: Window = obj

        if window and window.sequences.exists():
            return False

        return super().has_delete_permission(request, obj)


@admin.register(WindowDocumentation)
class WindowDocumentationAdmin(BaseDocumentationAdmin):
    fields = []


@admin.register(WindowQuickAdd)
class WindowQuickAddAdmin(BaseQuickAddAdmin):
    fields = ['systems', 'name']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field.widget = forms.MultipleHiddenInput()

        return field


@admin.register(WindowQuickChange)
class WindowQuickChangeAdmin(WindowAdmin):
    fields = []
    readonly_fields = ['documentation']

    def get_inlines(self, request, obj):
        inlines = [Actions, Sequences, Variables, Schemas]

        if Resource.objects.count():
            return [Resources] + inlines

        return inlines

    def has_delete_permission(self, request, obj=None):
        return False
