from .keyword_return_value import KeywordReturnValue


class WindowKeywordReturnValue(KeywordReturnValue):
    class Meta:
        proxy = True
        verbose_name = KeywordReturnValue._meta.verbose_name
        verbose_name_plural = KeywordReturnValue._meta.verbose_name_plural
