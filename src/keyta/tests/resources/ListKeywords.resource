*** Settings ***
Documentation    Keywords that create lists


*** Keywords ***
Two-element list
    [Documentation]    Returns a list containing the two arguments passed
    [Arguments]    ${Arg 1}    ${Arg 2}

    VAR    @{List}    ${Arg 1}    ${Arg 2}

    RETURN    ${List}
