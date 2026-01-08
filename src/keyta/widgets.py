from itertools import groupby
from typing import Optional

import django
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.forms import Widget, CheckboxSelectMultiple
from django.forms.models import ModelChoiceIterator
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django_select2.forms import ModelSelect2Widget

from keyta.apps.systems.models import System


def attrs_to_string(attrs: dict) -> str:
    return ' '.join([
        f'{name}="{value}"'
        for name, value
        in attrs.items()
    ])


def html_to_string(tag, attrs, body) -> str:
    return f'<{tag} {attrs_to_string(attrs)}>{body}</{tag}>'


def style_to_css(style: dict):
    return '; '.join([
        f'{name}: {value}'
        for name, value
        in style.items()
    ])


def url_query_parameters(query_parameters: dict):
    return '&'.join(
        f'{key}={value}'
        for key, value
        in query_parameters.items()
    )


def link(
    url: str,
    title: str,
    new_page: bool=False,
    query_parameters: Optional[dict]=None,
    styles: Optional[dict]=None,
    attrs: Optional[dict]=None
):
    if query_parameters:
        url = url + '?' + url_query_parameters(query_parameters)

    local_attrs = {
        'href': url
    }

    if new_page:
        local_attrs.update({'target': '_blank'})

    if styles:
        local_attrs['style'] = style_to_css(styles)

    return mark_safe(html_to_string('a', local_attrs | (attrs or {}), title))


class Icon:
    def __init__(self, css_class: str, styles: dict[str, str]=None, title=None):
        self.tag = 'i'
        self.attrs = {
            'class': css_class,
            'style': {'font-size': '36px'} | (styles or {})
        }
        if title:
            self.attrs['title'] = title
        self.body = ''

    def __str__(self):
        return html_to_string(
            self.tag,
            self.attrs | {'style': style_to_css(self.attrs['style'])},
            self.body
        )


def bold(text: str):
    return f"<b>{text}</b>"


def open_link_in_modal(url: str, title: str, attrs: dict|None=None):
    return mark_safe(
        '<a class="related-widget-wrapper-link view-related" %s>%s</a>'
        % (attrs_to_string({'href': url} | (attrs or {})), title)
    )


class BaseSelect(forms.Select):
    """
    A select widget with default configuration
    """

    def __init__(self, placeholder: str, attrs=None, choices=()):
        default_attrs = {
            'data-width': '100%',
            'data-placeholder': placeholder
        } | (attrs or {})

        super().__init__(default_attrs, choices)

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if value is None:
            option['attrs'].update({'disabled': 'true'})

        return option

    @property
    def i18n_name(self):
        """Name of the i18n file for the current language."""
        if django.VERSION < (4, 1):
            from django.contrib.admin.widgets import \
                SELECT2_TRANSLATIONS
            from django.utils.translation import get_language

            return SELECT2_TRANSLATIONS.get(get_language())
        else:
            from django.contrib.admin.widgets import \
                get_select2_language

            return get_select2_language()

    @property
    def media(self):
        return forms.Media(
            js=(
                "vendor/select2/js/select2.min.js",
                f"{settings.SELECT2_I18N_PATH}/{self.i18n_name}.js",
                "admin/js/jquery.init.js"
            )
        )


class BaseSelectMultiple(BaseSelect):
    """
    A select widget with default configuration
    """

    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)

    def value_omitted_from_data(self, data, files, name):
        # An unselected <select multiple> doesn't appear in POST data, so it's
        # never known if the value is actually omitted.
        return False


class CheckboxSelectMultipleSystems(CheckboxSelectMultiple):
    template_name = 'checkbox_select_systems.html'

    def create_option(
        self,
        name,
        value,
        label,
        selected,
        index,
        subindex=None,
        attrs=None,
    ):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if hasattr(self, 'in_use') and selected and value in self.in_use:
            option['attrs'].update({'onClick': 'return false'})

        return option

    def optgroups(self, name, value, attrs=None):
        orig_optgroups = super().optgroups(name, value, attrs)
        optgroups = {}

        for _group, options, _index in orig_optgroups:
            option = options[0]
            system: System = option['value'].instance
            optgroups[system.name] = {
                'options': [option],
                'name': system.name,
            }

        return optgroups.items()


class ModelSelect2AdminWidget(ModelSelect2Widget):
    def __init__(self, attrs=None, **kwargs):
        super().__init__(
            attrs={
                'data-allow-clear': 'false',
                'data-minimum-input-length': 0,
                'data-placeholder': kwargs.get('placeholder'),
                'data-width': '100%',
                'data-style': 'width: 100%',
                'style': 'width: 95%'
            } | (attrs if attrs else {}),
            **kwargs
        )

    @property
    def media(self):
        return forms.Media(
            js=(
                "vendor/select2/js/select2.min.js",
                f"{settings.SELECT2_I18N_PATH}/{self.i18n_name}.js",
                "admin/js/jquery.init.js",
                "django_select2/django_select2.js"
            )
        )


class ModelSelect2MultipleAdminWidget(ModelSelect2AdminWidget):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)

    def value_omitted_from_data(self, data, files, name):
        # An unselected <select multiple> doesn't appear in POST data, so it's
        # never known if the value is actually omitted.
        return False


class ManyToManySelectOneWidget(ModelSelect2MultipleAdminWidget):
    allow_multiple_selected = False


class GroupedChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield "", self.field.empty_label

        queryset = (
            self.queryset
            .prefetch_related(self.group_by)
            .order_by(self.group_by + '__name', 'name')
        )

        groups = groupby(queryset, key=lambda x: getattr(x, self.group_by))

        for group, keywords in groups:
            yield [
                group.name,
                [
                    (keyword.id, keyword.name)
                    for keyword in keywords
                ]
            ]


class GroupedByLibrary(GroupedChoiceIterator):
    group_by = 'library'


class GroupedByResource(GroupedChoiceIterator):
    group_by = 'resource'


class CustomRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):
    def __init__(self, widget, url, url_params: dict, htmx_attrs: Optional[dict]=None) -> None:
            self.htmx_attrs = htmx_attrs
            self.related_url = url
            self.url_params = '&'.join([
                f'{name}={value}'
                for name, value in url_params.items()
            ])

            super().__init__(
                widget.widget,
                widget.rel, 
                widget.admin_site
            )

    def get_context(self, name, value, attrs):
            context = super().get_context(name, value, attrs)
            context['htmx_attrs'] = self.htmx_attrs or {}
            context['url_params'] = self.url_params

            return context

    def get_related_url(self, info, action, *args):
        return self.related_url or super().get_related_url(info, action, *args)


class LabelWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return '<p>-</p>'


def quick_add_widget(widget, url, url_params):
    wrapped_widget = CustomRelatedFieldWidgetWrapper(
        widget,
        url,
        url_params
    )
    wrapped_widget.attrs.update({
        'data-placeholder': _('Klicke auf das Plus-Symbol'),
        'data-width': '95%',
        'disabled': True,
    })

    return wrapped_widget


def quick_change_widget(widget, url_params=None):
    wrapped_widget = CustomRelatedFieldWidgetWrapper(
        widget,
        None,
        {'quick_change': 1} | (url_params or {})
    )
    wrapped_widget.can_add_related = False
    wrapped_widget.can_change_related = True

    return wrapped_widget
