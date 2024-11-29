import enum


class ErrorType(str, enum.Enum):
    CALL_PARAMS = 'call_params'
    STEPS = 'steps'
    SETTINGS = 'settings'
    SYSTEM = 'system'


class ValidationError(dict, enum.Enum):
    INCOMPLETE_CALL_PARAMS = {
        'error': 'Die Aufrufparameter sind unvollständig',
        'type': ErrorType.CALL_PARAMS
    }
    INCOMPLETE_STEP_PARAMS = {
        'error': 'Die Parameter der Schritte sind unvollständig',
        'type': ErrorType.STEPS
    }
    INCOMPLETE_ATTACH_TO_SYSTEM_PARAMS = {
        'error': 'Die Parameter der Anbindung ans laufende System sind unvollständig',
        'type': ErrorType.SETTINGS
    }
    INCOMPLETE_TEST_SETUP_PARAMS = {
        'error': 'Die Parameter der Testvorbereitung sind unvollständig',
        'type': ErrorType.SETTINGS
    }
    INCOMPLETE_TEST_TEARDOWN_PARAMS = {
        'error': 'Die Parameter der Testnachbereitung sind unvollständig',
        'type': ErrorType.SETTINGS
    }
    NO_ATTACH_TO_SYSTEM = {
        'error': 'Die Anbindung ans laufende System muss gepflegt werden',
        'type': ErrorType.SYSTEM
    }
