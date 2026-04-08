from django import forms
from django.contrib import admin
from django.forms.utils import ErrorDict, ErrorList
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField

from ..models import TestData, TestCase


class TestDataFormset(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.testcase: TestCase = kwargs.get('instance')

    def clean(self):
        for form in self.extra_forms:
            name = form.cleaned_data.get('name')

            if self.testcase.testdata.filter(name=name).exists():
                form._errors = ErrorDict()
                form._errors['name'] = ErrorList([
                    _('Testdaten mit diesem Namen sind bereits vorhanden.')
                ])


class TestDataInline(DeleteRelatedField, BaseTabularInline):
    model = TestData
    fields = ['user', 'name', 'last_update_field', 'download', 'upload']
    formset = TestDataFormset
    readonly_fields = ['last_update_field', 'download']
    template = 'testdata_inline_tabular.html'

    @admin.display(description='')
    def download(self, testdata: TestData):
        return testdata.get_download_icon()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'name':
            field.widget.attrs['style'] = 'width: 100%'

        if db_field.name == 'user':
            field.initial = request.user.id
            field.widget = forms.HiddenInput()

        return field

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        @admin.display(description='')
        def upload(self, testdata: TestData):
            if request.user == testdata.user:
                return testdata.get_file_input() + testdata.get_upload_icon()

            return '-'

        TestDataInline.upload = upload

        return readonly_fields + ['upload']

    @admin.display(description=_('Letzte Aktualisierung'))
    def last_update_field(self, testdata: TestData):
        return testdata.get_last_update_field()
