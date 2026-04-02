import enum

from django.utils.translation import gettext_lazy as _


class ErrorType(str, enum.Enum):
    CALL_PARAMS = 'call_params'
    STEPS = 'steps'
    SETTINGS = 'settings'
    SYSTEM = 'system'
    TEST_DATA = 'test_data'


class ValidationError(dict, enum.Enum):
    INCOMPLETE_CALL_PARAMS = {
        'error': _('Die Aufrufparameter (Werte) sind unvollständig.'),
        'type': ErrorType.CALL_PARAMS
    }
    INCOMPLETE_STEP = {
        'error': _('Die Schritte sind unvollständig.'),
        'type': ErrorType.STEPS
    }
    INCOMPLETE_STEP_PARAMS = {
        'error': _('Die Parameter (Werte) der Schritte sind unvollständig.'),
        'type': ErrorType.STEPS
    }
    INCOMPLETE_ATTACH_TO_SYSTEM_PARAMS = {
        'error': _('Die Parameter (Werte) der Anbindung ans laufende System (unter Einstellungen) sind unvollständig.'),
        'type': ErrorType.SETTINGS
    }
    INCOMPLETE_TEST_SETUP_PARAMS = {
        'error': _('Die Parameter (Werte) der Testvorbereitung (unter Einstellungen) sind unvollständig.'),
        'type': ErrorType.SETTINGS
    }
    INCOMPLETE_TEST_TEARDOWN_PARAMS = {
        'error': _('Die Parameter (Werte) der Testnachbereitung (unter Einstellungen) sind unvollständig.'),
        'type': ErrorType.SETTINGS
    }
    INVALID_EXCEL_FILE = {
        'error': _('Die Tabellen in der Excel-Datei entsprechen nicht den Parametern der Testschritte.'),
        'type': ErrorType.TEST_DATA
    }
    INVALID_TESTDATA = {
        'error': _('Die ausgewählten Testdaten entsprechen nicht den Parametern der Testschritte.'),
        'type': ErrorType.TEST_DATA
    }
    NO_ATTACH_TO_SYSTEM = {
        'error': _('Die Anbindung ans laufende System muss in den Einstellungen gepflegt werden.'),
        'type': ErrorType.SYSTEM
    }
    NO_STEPS = {
        'error': _('Die Schritte sind leer.'),
        'type': ErrorType.STEPS
    }
