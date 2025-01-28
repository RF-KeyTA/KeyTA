from django.contrib import admin

from keyta.admin.testcase import BaseTestCaseAdmin

from apps.testcases.models import TestCase


@admin.register(TestCase)
class TestCaseAdmin(BaseTestCaseAdmin):
    pass
