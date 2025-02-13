from dataclasses import dataclass


@dataclass
class Icons:
    delete: str = 'fa-solid fa-trash'
    exec_log: str = 'fa-regular fa-file-lines'
    exec_start: str = 'fa-solid fa-circle-play'
    exec_settings: str = 'fa-solid fa-gear'
    kw_call_parameters: str = 'fa-solid fa-list'
    library_import_args: str = 'fa-solid fa-list'
