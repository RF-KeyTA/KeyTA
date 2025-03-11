from itertools import groupby

import django
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper, get_select2_language
from django.forms.models import ModelChoiceIterator
from django.utils.safestring import mark_safe

from django_select2.forms import ModelSelect2Widget


def link(url: str, title: str, new_page: bool = False, query_parameters: dict[str, str]={}):
    if query_parameters:
        url = url + '?' + '&'.join(
                f'{key}={value}' 
                for key, value 
                in query_parameters.items()
            )

    if new_page:
        return mark_safe(
            '<a href="%s" target="_blank">%s</a>'
            % (url, title)
        )
    else:
        return mark_safe(
            '<a href="%s">%s</a>'
            % (url, title)
        )


class Icon:
    def __init__(self, css_class: str, styles: dict[str, str]=None):
        self.tag = 'i'
        self.attrs =  {
            'class': css_class,
            'style': {'font-size': '36px'} | (styles or {})
        }
        self.body = []

    def __str__(self):
        def style_to_css(style: dict):
            return '; '.join([
                f'{name}: {value}'
                for name, value
                in style.items()
            ])

        def attrs_to_string(attrs: dict) -> str:
            return ' '.join([
                f'{name}="{value}"'
                for name, value
                in attrs.items()
            ])

        def html_to_string(html: list) -> str:
            if not html:
                return ''

            tag, attrs, body = html
            return f'<{tag} {attrs}>{html_to_string(body)}</{tag}>'

        attrs = attrs_to_string({
            **self.attrs,
            'style': style_to_css(self.attrs['style'])
        })

        return html_to_string([self.tag, attrs, self.body])


def bold(text: str):
    return f"<b>{text}</b>"


def open_link_in_modal(url: str, title: str):
    return mark_safe(
        '<a class="related-widget-wrapper-link view-related" href="%s">%s</a>'
        % (url, title)
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


class KeywordCallSelect(BaseSelect):
    template_name = 'admin/keywordcall/select.html'

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        index = str(index) if subindex is None else "%s_%s" % (index, subindex)
        option_attrs = (
            self.build_attrs(self.attrs, attrs) if self.option_inherits_attrs else {}
        )

        if value is None:
            option_attrs.update({'disabled': 'true'})

        if selected:
            option_attrs.update(self.checked_attribute)

        if "id" in option_attrs:
            option_attrs["id"] = self.id_for_label(option_attrs["id"], index)

        return {
            "name": name,
            "value": value,
            "label": label,
            "selected": selected,
            "index": index,
            "attrs": option_attrs,
            "type": self.input_type,
            "template_name": self.option_template_name,
            "wrap_label": True,
        }


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


class Select2MultipleWidget(ModelSelect2MultipleAdminWidget):
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
    def __init__(self, widget, related_url, url_params, **kwargs) -> None:
            self.related_url = related_url
            if url_params:
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
            context['url_params'] = self.url_params
            return context
    
    def get_related_url(self, info, action, *args):
        return self.related_url
