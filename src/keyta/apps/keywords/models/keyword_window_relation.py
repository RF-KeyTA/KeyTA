from django.db import models

from .keyword import Keyword, KeywordType


class KeywordWindowRelation(Keyword.windows.through):
    def __str__(self):
        return f'{self.window} -> {self.keyword}'

    class QuerySet(models.QuerySet):
        def actions(self):
            return self.filter(keyword__type=KeywordType.ACTION)

        def sequences(self):
            return self.filter(keyword__type=KeywordType.SEQUENCE)

    objects = QuerySet.as_manager()

    class Meta:
        auto_created = True
        proxy = True
