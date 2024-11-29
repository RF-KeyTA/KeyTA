from django.apps import AppConfig


class TestCaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.testcases'
    verbose_name = 'Testfälle'
