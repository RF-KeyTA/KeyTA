import re
import urllib.parse
import xml.dom.minidom
from abc import abstractmethod

from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models import Keyword, KeywordParameter, KeywordDocumentation
from keyta.rf_import.import_keywords import args_table, get_default_value
from keyta.widgets import open_link_in_modal

from .base_model import AbstractBaseModel


class KeywordSource(AbstractBaseModel):
    name = models.CharField(
        max_length=255, 
        verbose_name=_('Name')
    )
    documentation = models.TextField(
        verbose_name=_('Dokumentation')
    )

    def __str__(self):
        return self.name

    def import_keywords(self, libdoc_json):
        keyword_names = set()
        deprecated_keywords = set()

        keyword: dict
        for keyword in libdoc_json["keywords"]:
            name = keyword["name"]

            if keyword.get('deprecated', False):
                deprecated_keywords.add(name)
                continue

            keyword_names.add(name)

            kw_args = {}

            if self.is_library():
                kw_args['library'] = self
            else:
                kw_args['resource'] = self

            kw, created = Keyword.objects.update_or_create(**{
                **kw_args,
                'name': name,
                'defaults': {
                    'args_doc': args_table(keyword["args"]),
                    'documentation': keyword["doc"],
                    'short_doc': keyword['shortdoc']
                }
            })

            kwarg_names = set()
            for idx, arg, in enumerate(keyword["args"]):
                name = arg["name"]
                if not name:
                    continue

                if arg["required"]:
                    KeywordParameter.create_arg(
                        keyword=kw,
                        name=name,
                        position=idx
                    )
                else:
                    if arg["kind"] == 'VAR_POSITIONAL':
                        KeywordParameter.create_arg(
                            keyword=kw,
                            name=name,
                            position=idx,
                            is_list=True
                        )
                    else:
                        kwarg_names.add(name)
                        default_value = get_default_value(
                            arg["defaultValue"],
                            arg["kind"]
                        )
                        KeywordParameter.create_kwarg(
                            keyword=kw,
                            name=name,
                            default_value=default_value,
                            position=idx
                        )

            for kwarg in kw.parameters.kwargs():
                if kwarg.name not in kwarg_names:
                    kwarg.delete()

        self.documentation = self.replace_links(self.documentation, heading_links=False)
        self.save()

        for kw in self.keywords.all():
            if ((kw.name in deprecated_keywords or
                 kw.name not in keyword_names) and
                    not kw.uses.exists()):
                kw.delete()
                continue

            kw.documentation = self.replace_links(kw.documentation)
            kw.save()

    @abstractmethod
    def is_library(self) -> bool:
        pass

    def replace_links(self, docstring: str, heading_links=True):
        heading_ids = set(re.findall(r'<h\d id=\"([^"]*)\"', self.documentation))

        def replace_link(match: re.Match):
            link_str = match.group(0)
            link = xml.dom.minidom.parseString(link_str).getElementsByTagName('a')[0]
            href: str = link.attributes['href'].value
            text: str = link.firstChild.nodeValue

            if href.startswith('http'):
                link.attributes['target'] = '_blank'
                return link.toxml()

            if href.startswith('#'):
                if keyword_doc := (
                    KeywordDocumentation.objects.filter(library__name=self.name, name__iexact=text).first() or
                    KeywordDocumentation.objects.filter(resource__name=self.name, name__iexact=text).first()
                ):
                    return open_link_in_modal(keyword_doc.get_admin_url(), keyword_doc.name)

                if heading_links and urllib.parse.unquote(href.lstrip('#')) in heading_ids:
                    link.attributes['href'] = self.get_admin_url() + href
                    link.attributes['target'] = '_blank'
                    return link.toxml()

            return link.toxml()

        return re.sub(
            r'<a[^>]*>[^<]*</a>',
            replace_link,
            docstring
        )

    class Meta:
        abstract = True
        ordering = ['name']
