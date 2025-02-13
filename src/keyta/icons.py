from dataclasses import dataclass


@dataclass
class Icons:
    delete: str = 'fa-solid fa-trash'
    exec_log: str = 'fa-regular fa-file-lines'
    exec_pass: str = 'fa-solid fa-circle-check'
    exec_fail: str = 'fa-solid fa-circle-xmark'
    exec_start: str = 'fa-solid fa-circle-play'
    exec_settings: str = 'fa-solid fa-gear'
    kw_call_parameters: str = 'fa-solid fa-list'
    library_import_args: str = 'fa-solid fa-list'
    library_update: str = 'fa-solid fa-circle-arrow-up'
    library_setting_reset: str = 'fa-solid fa-rotate-left'
