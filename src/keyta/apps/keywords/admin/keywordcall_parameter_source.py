from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import KeywordCallParameterSource


@admin.register(KeywordCallParameterSource)
class KeywordCallParameterSourceAdmin(BaseAdmin):
    """
    This admin is necessary for the delete confirmation page
    """
