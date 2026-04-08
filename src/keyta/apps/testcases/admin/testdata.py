from django.contrib import admin
from django.http import HttpResponse, FileResponse, JsonResponse

from keyta.admin.base_admin import BaseAdmin
from keyta.apps.executions.errors import ValidationError

from ..models import TestData
from ..models.testdata import get_excel_file_path, TestDataError


@admin.register(TestData)
class TestDataAdmin(BaseAdmin):
    def change_view(self, request, object_id, form_url="", extra_context=None):
        if 'export' in request.GET:
            pk = request.resolver_match.kwargs['object_id']
            testdata = TestData.objects.get(pk=pk)
            excel_file_path = testdata.export_to_excel()

            return FileResponse(
                open(excel_file_path, 'rb'),
                as_attachment=True,
                filename=excel_file_path.name
            )

        if 'last_update' in request.GET:
            pk = request.resolver_match.kwargs['object_id']

            # The extra form of a formset has pk=None
            if pk != 'None':
                return HttpResponse(TestData.objects.get(pk=pk).get_last_update_field())

            return HttpResponse('')

        if 'upload_icon' in request.GET:
            pk = request.resolver_match.kwargs['object_id']

            # The extra form of a formset has pk=None
            if pk != 'None':
                return HttpResponse(TestData.objects.get(pk=pk).get_upload_icon())

            return HttpResponse('')

        if request.method == 'PUT':
            pk = request.resolver_match.kwargs['object_id']
            testdata = TestData.objects.get(pk=pk)
            excel_file_path = get_excel_file_path(testdata.name)

            with open(excel_file_path, 'wb') as file:
                file.write(request.body)
                file.close()

            try:
                testdata.import_from_excel(excel_file_path, testdata.get_metadata())
                return JsonResponse({})
            except TestDataError:
                return JsonResponse(ValidationError.INVALID_EXCEL_FILE)

        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)
