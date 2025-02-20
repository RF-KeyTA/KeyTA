from django.contrib import admin

from keyta.admin.testcase import BaseTestCaseAdmin

from .models import TestCase


@admin.register(TestCase)
class TestCaseAdmin(BaseTestCaseAdmin):
    change_form_template = 'change_form.html'
    pass
