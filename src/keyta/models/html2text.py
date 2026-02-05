from html.parser import HTMLParser


class HTML2Text(HTMLParser):
    def __init__(self, *, convert_charrefs = True):
        self.texts = []
        super().__init__(convert_charrefs=convert_charrefs)

    def handle_data(self, data):
        self.texts.append(data)

    def get_text(self):
        return '\n'.join(self.texts)

    @classmethod
    def parse(cls, html: str) -> str:
        html_parser = HTML2Text()
        html_parser.feed(html)

        return html_parser.get_text()
