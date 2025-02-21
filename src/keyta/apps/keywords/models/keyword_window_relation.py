from .keyword import Keyword


class KeywordWindowRelation(Keyword.windows.through):
    class Meta:
        auto_created = True
        proxy = True
