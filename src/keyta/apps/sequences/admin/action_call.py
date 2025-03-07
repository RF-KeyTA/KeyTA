from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.apps.keywords.admin.keywordcall import (
    KeywordCallAdmin, 
    KeywordDocField, 
    ReturnValueField
)

from ..models import ActionCall


@admin.register(ActionCall)
class ActionCallAdmin(
    ReturnValueField,
    KeywordDocField,
    KeywordCallAdmin
):
    pass
