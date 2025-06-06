import json

from django import forms
from django.contrib import messages, admin
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.windows.admin import QuickAddMixin
from keyta.apps.windows.models import WindowQuickAdd, WindowSystemRelation
from keyta.widgets import ModelSelect2AdminWidget, link, BaseSelect

from .models import System


class Windows(QuickAddMixin, BaseTabularInline):
    model = WindowSystemRelation
    form = forms.modelform_factory(
        WindowSystemRelation,
        fields=['window'],
        labels={
            'window': _('Maske')
        }
    )
    quick_add_field = 'window'
    quick_add_model = WindowQuickAdd
    verbose_name = _('Maske')
    verbose_name_plural = _('Masken')

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('window__name')

    def has_change_permission(self, request, obj=None):
        return False

    def quick_add_url_params(self, request: HttpRequest, url_params: dict):
        system_id = request.resolver_match.kwargs['object_id']
        system = System.objects.get(pk=system_id)
        tab_url = system.get_tab_url(getattr(self, 'tab_name', None))

        return {
            'systems': system_id,
            'ref': request.path + tab_url
        }


@admin.register(System)
class SystemAdmin(BaseAdmin):
    list_display = ['name', 'description']

    fields = ['name', 'description', 'library']
    inlines = [Windows]

    def autocomplete_name(self, name: str, request: HttpRequest):
        return json.dumps([
            name
            for name in
            self.model.objects.values_list('name', flat=True)
            .filter(name__icontains=name)
        ])

    def formfield_for_dbfield(self, db_field, request: HttpRequest, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'library':
            field.widget = BaseSelect(_('Bibliothek auswählen'))

        if db_field.name == 'attach_to_system':
            field.widget = ModelSelect2AdminWidget(
                search_fields=['name__icontains'],
                attrs={
                    'data-placeholder': _('Aktion auswählen'),
                    'style': 'width: 95%'
                })
            
            system_id = request.resolver_match.kwargs['object_id']
            field.queryset = (
                field.queryset.actions()
                .filter(systems__in=[system_id])
                .filter(setup_teardown=True)
            )

        return field

    def get_fields(self, request, obj=None):
        system: System = obj

        if system:
            return self.fields + ['attach_to_system']

        return self.fields

    def get_inlines(self, request, obj):
        system: System = obj

        if system:
            return self.inlines

        return []

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        system: System = obj

        add_attach_to_running_system = link(
            '/actions/action/add/',
            _('erstelle'),
            new_page=True,
            query_parameters={
                'setup_teardown': True,
                'systems': system.pk
            },
            styles={
                'color': 'white !important'
            }
        )

        if not change:
            message_level = messages.get_level(request)
            messages.set_level(request, messages.INFO)
            messages.info(
                request,
                mark_safe(
                    _('Falls zutreffend, ') + add_attach_to_running_system + _(' die Aktion zur Anbindung an das System')
                )
            )
            messages.set_level(request, message_level)
