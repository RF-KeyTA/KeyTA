from dataclasses import dataclass


@dataclass
class Icons:
    action:str = 'fa-solid fa-cubes-stacked'
    clone: str = 'fa-solid fa-copy'
    delete: str = 'fa-solid fa-trash-can'
    delete_rel: str = 'fa-solid fa-trash'
    edit: str = 'fa-solid fa-pencil'
    exec_fail: str = 'fa-solid fa-circle-xmark'
    exec_log: str = 'fa-regular fa-file-lines'
    exec_pass: str = 'fa-solid fa-circle-check'
    exec_settings: str = 'fa-solid fa-gear'
    exec_start: str = 'fa-solid fa-circle-play'
    kw_call_drag_handle: str = 'fa-solid fa-sort'
    kw_call_parameters: str = 'fa-solid fa-list'
    library: str = 'fa-solid fa-robot'
    library_import_args: str = 'fa-solid fa-list'
    library_update: str = 'fa-solid fa-circle-arrow-up'
    preview: str = 'fa-solid fa-image'
    reset_default_value: str = 'fa-solid fa-rotate-left'
    resource: str = 'fa-solid fa-key'
    save: str = 'fa-regular fa-floppy-disk'
    sequence: str = 'fa-solid fa-arrows-turn-to-dots'
    system: str = 'fa-solid fa-shapes'
    testcase: str = 'fa-solid fa-list-check'
    variable: str = 'fa-solid fa-arrow-up-right-from-square'
    window: str = 'fa-solid fa-layer-group'
