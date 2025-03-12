from django.utils.translation import gettext as _

from keyta.models.testcase import AbstractTestCase


class TestCase(AbstractTestCase):
    def robot_documentation(self):
        return super().plaintext_documentation()

    class Meta(AbstractTestCase.Meta):
        verbose_name = _('Testfall')
        verbose_name_plural = _('Testfälle')
