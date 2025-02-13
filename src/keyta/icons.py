from dataclasses import dataclass


@dataclass
class Icons:
    clone = 'fa-solid fa-copy'
    delete = 'fa-solid fa-trash-can'
    delete_rel = 'fa-solid fa-trash'
    exec_log = 'fa-regular fa-file-lines'
    exec_pass = 'fa-solid fa-circle-check'
    exec_fail = 'fa-solid fa-circle-xmark'
    exec_start = 'fa-solid fa-circle-play'
    exec_settings = 'fa-solid fa-gear'
    kw_call_parameters = 'fa-solid fa-list'
    library_import_args = 'fa-solid fa-list'
    library_update = 'fa-solid fa-circle-arrow-up'
    library_setting_reset = 'fa-solid fa-rotate-left'
    kw_call_drag_handle = 'fa-solid fa-sort'
    save = 'fa-regular fa-floppy-disk'
