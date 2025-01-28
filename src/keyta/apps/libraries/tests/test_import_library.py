import re
import urllib.parse
import xml.dom.minidom

from django.test import TestCase as DjangoTest

from keyta.widgets import open_link_in_modal
from ..management.commands.import_library import replace_links
from ..models import Library, LibraryKeyword


class LibraryImportTests(DjangoTest):
    longMessage = True

    def test_replace_keyword_links(self):
        lib_docstring = """
        <h2 id=\"Browser, Context and Page\">Browser, Context and Page</h2>
        """

        kw_docstring = """
        use the keywords <a href=\"#Log\" class=\"name\">Log</a> 
        or <a href=\"#Log%20Many\" class=\"name\">Log Many</a>
        
        the <a href=\"http://robotframework.org/robotframework/latest/libraries/DateTime.html\">DateTime</a> library
        
        <li><a href=\"#Browser%2C%20Context%20and%20Page\" class=\"name\">Browser, Context and Page</a></li>
        """

        lib = Library(name='Test Library', documentation=lib_docstring)
        lib.save()
        kw1 = LibraryKeyword(library=lib, name='Log')
        kw1.save()
        kw2 = LibraryKeyword(library=lib, name='Log Many')
        kw2.save()

        docstring_with_links = replace_links(kw_docstring, lib)

        links = [
            xml.dom.minidom.parseString(link_str).getElementsByTagName('a')[0]
            for link_str in re.findall(r'<a[^>]*>[^<]*</a>', kw_docstring)
        ]

        heading_ids = set(re.findall(r'<h\d id=\"([^"]*)\"', lib.documentation))

        for link in links:
            href: str = link.attributes['href'].value
            text: str = link.firstChild.nodeValue

            if href.startswith('http'):
                link.attributes['target'] = '_blank'
                self.assertTrue(link.toxml() in docstring_with_links)

            if href.startswith('#'):
                if kw := LibraryKeyword.objects.filter(name=text).first():
                    kw_link = open_link_in_modal(kw.get_docadmin_url(), kw.name)
                    self.assertTrue(kw_link in docstring_with_links)

                if urllib.parse.unquote(href.lstrip('#')) in heading_ids:
                    self.assertTrue(lib.get_admin_url() + href in docstring_with_links)
