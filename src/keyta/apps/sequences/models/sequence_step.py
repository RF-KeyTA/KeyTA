from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models import KeywordCall


class SequenceStep(KeywordCall):
    class Meta:
        proxy = True
        verbose_name = _('Schritt')
        verbose_name_plural = _('Schritte')
