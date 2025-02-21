from html.parser import HTMLParser

from django.conf import settings


class HTML2Text(HTMLParser):
    def __init__(self, *, convert_charrefs = True):
        self.texts = []
        super().__init__(convert_charrefs=convert_charrefs)

    def handle_data(self, data):
        self.texts.append(data)

    def get_text(self):
        return '\n'.join(self.texts)


class DocumentationMixin:
    def plaintext_documentation(self):
        html_parser = HTML2Text()
        html_parser.feed(self.documentation)
        return html_parser.get_text()

    def robot_documentation(self):
        return settings.BASE_URL + self.get_admin_url()
