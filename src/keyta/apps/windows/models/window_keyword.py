from apps.keywords.models import Keyword


class WindowKeyword(Keyword):
    class Meta:
        proxy = True
