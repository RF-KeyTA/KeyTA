*** Settings ***
Documentation    Keywords that create dictionaries


*** Keywords ***
Dict with one key
    [Documentation]    Returns a dictionary with the given key and value
    [Arguments]    ${key}    ${value}

    VAR    &{Dict}    ${key}=${value}

    RETURN    ${Dict}
