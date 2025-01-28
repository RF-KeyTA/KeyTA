from django.utils.translation import gettext as _

from keyta.models.testcase import AbstractTestCase


class TestCase(AbstractTestCase):
    class Meta:
        verbose_name = _('Testfall')
        verbose_name_plural = _('Testfälle')
