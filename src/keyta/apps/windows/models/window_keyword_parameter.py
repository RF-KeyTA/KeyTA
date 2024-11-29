from apps.keywords.models import KeywordParameter, KeywordParameterType


class WindowKeywordParameter(KeywordParameter):
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.type = KeywordParameterType.ARG
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        proxy = True
        verbose_name = 'Parameter'
        verbose_name_plural = 'Parameter'
