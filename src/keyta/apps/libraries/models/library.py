import re
import urllib.parse
import xml.dom.minidom

from django.db import models
from django.utils.translation import gettext_lazy as _

from jinja2 import Template

from keyta.apps.keywords.models import Keyword, KeywordDocumentation
from keyta.models.keyword_source import KeywordSource
from keyta.widgets import open_link_in_modal


class Library(KeywordSource):
    version = models.CharField(
        max_length=255
    )
    init_doc = models.TextField(
        verbose_name=_('Einrichtung')
    )
    # JSON representation of a dict
    typedocs = models.TextField(
        default='{}'
    )

    ROBOT_LIBRARIES = {
        'BuiltIn',
        'Collections',
        'DateTime',
        'Dialogs',
        'OperatingSystem',
        'Process',
        'Remote',
        'Screenshot',
        'String',
        'Telnet',
        'XML'
    }

    @property
    def has_parameters(self):
        return self.kwargs.exists()

    def import_keywords(self, libdoc_dict: dict, typedocs: dict[str, dict]):
        super().import_keywords(libdoc_dict, typedocs)

        self.documentation = self.replace_links(self.documentation, typedocs, heading_links=False)
        self.save()

        for kw in self.keywords.all():
            kw.documentation = self.replace_links(kw.documentation, typedocs, heading_links=True)
            kw.save()

    def is_library(self):
        return True

    def replace_links(self, docstring: str, lib_typedocs: dict[str, dict], heading_links=False):
        def replace_link(match: re.Match):
            link_str = match.group(0)
            link = xml.dom.minidom.parseString(link_str).getElementsByTagName('a')[0]
            href: str = link.attributes['href'].value

            if href.startswith('http'):
                link.attributes['target'] = '_blank'
                return link.toxml()

            if href == '#Keywords':
                tab_name =  self.get_tab_url(Keyword._meta.verbose_name_plural).removeprefix('#')
                link.attributes['onclick'] = f"document.querySelector('a[aria-controls={tab_name}]').click()"
                return link.toxml()

            if href.startswith('#type-'):
                link.attributes['href'] = href.replace('type-', '')
                link.attributes['onclick'] = f'bsShowModal("{link.attributes["href"].value}")'
                return link.toxml()

            if href.startswith('#'):
                kw_name: str = ' '.join(href.removeprefix('#').split('%20'))

                if keyword_doc := (
                    KeywordDocumentation.objects.filter(library__name=self.name, name__iexact=kw_name).first() or
                    KeywordDocumentation.objects.filter(resource__name=self.name, name__iexact=kw_name).first()
                ):
                    return open_link_in_modal(keyword_doc.get_admin_url(), keyword_doc.name)

                if heading_links:
                    heading_ids = set(re.findall(r'<h\d id=\"([^"]*)\"', self.documentation))

                    if urllib.parse.unquote(href.lstrip('#')) in heading_ids:
                        link.attributes['href'] = self.get_admin_url() + href
                        link.attributes['target'] = '_blank'
                        return link.toxml()

            return link.toxml()

        typedocs = [
            typedoc
            for type_ in re.findall(r'"#type-(\w+)"', docstring)
            if (typedoc := lib_typedocs.get(type_))
        ]

        template = """
        {% for typedoc in typedocs %}
        <div id="{{ typedoc.name }}" class="modal" tabindex="-1" role="dialog">
            {{ typedoc.doc }}
        </div>
        {% endfor %}
        """

        typedocs = Template(template).render({
            'typedocs': typedocs
        })

        return re.sub(
            r'<a[^>]*>[^<]*</a>',
            replace_link,
            docstring
        ) + typedocs

    class Meta(KeywordSource.Meta):
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_library_name')
        ]
        verbose_name = _('Bibliothek')
        verbose_name_plural = _('Bibliotheken')


class LibraryInitDocumentation(Library):
    class Meta:
        proxy = True
