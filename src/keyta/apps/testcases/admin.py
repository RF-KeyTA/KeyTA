from django.contrib import admin

from apps.testcases.models import TestCase
from keyta.views.testcase import BaseTestCaseAdmin


@admin.register(TestCase)
class TestCaseAdmin(BaseTestCaseAdmin):
    pass
