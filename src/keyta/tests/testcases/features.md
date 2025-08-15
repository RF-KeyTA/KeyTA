# List view

- Test Cases can be filtered by System

- Test Cases can be searched by Name

- Test Cases are sorted by name alphabetically


# Add form

- A Test Case can be added


# Change form

- A change to the name or the systems is saved automatically

- A Test Case can be exported to a .robot file
    - Only if it has no incomplete test steps (missing keyword or missing arguments)

- A Test Case can be duplicated. The copy is identical except for:
    - The name has the suffix Copy
    - The Execution result is not set
    - There is no Execution log

- A Test Case can be deleted

## Steps

- When adding a step only a Window can be selected. All other fields are grayed out

- Also a "+" has been added to allow the creation of a Window form the Testcases section

- After creating a Step a Sequence or Resource keyword and a Reference Value can be selected

- If the step has parameters the icon Values allows setting their values and also the return value

- If the parameters are not set the Values icon is pink

- If the parameters are set the Values icon is blue

- If the parameters are set and the called keyword changes, the current parameters and return value are deleted

- If a Reference Value is selected, the fields of its associated schema can be referenced in the parameter values

- If a Reference Value is selected and then removed, the references to its schema fields are also removed from the parameter values

- If a keyword is selected and the window is changed, the keyword, its parameters and return value and the reference value are deleted

- If a Reference Value of type LIST is selected the generated RF code consists of a FOR loop that iterates over the element of the list and in each iteration calls the selected keyword

- Next to the Window there is an arrow icon that when clicked shows a modal with the following tabs:
    - General: shows the documentation
    - Resources: add/remove Resources
    - Actions: quickly add a new action
    - Sequences: quickly add a new sequence
    - Reference Values: quickly add a reference value
    - Templates: quickly add a Template for use in a Reference Value

- If the keyword comes from a Resource next to it there is an arrow icon that when clicked shows a modal with the tab General, which shows its documentation

- If the keyword is a Sequence next to it there is an arrow icon that when clicked shows a modal with the following tabs:
    - General: shows its documentation
    - Parameters: add/remove/edit parameters
    - Steps: add/remove/edit the sequence steps
    - Return Value: add/remove the Sequence return value

- If a Reference Value is selected next to it there is an arrow icon that when clicked shows a modal where its values can be edited


## Execution

- Only shown when there is at least one step

- Clicking the Settings button shows a modal with the following inlines:


### Libraries

- Lists the Libraries used in the test
- Allows configuring the init parameters of each library used


### Resource Imports

- Lists the Resources used in the test


### Test Setup

- An Action can be selected
- If the Action has parameters their values can be set
- If the Action is changed the parameters are now the ones of the new action
- The Action can be deactivated


### Test Teardown

- An Action can be selected
- If the Action has parameters their values can be set
- If the Action is changed the parameters are now the ones of the new action
- The Action can be deactivated


- Clicking the Execute button the test case is executed by RF only if:
    - No step is incomplete (missing Keyword)
    - All step parameters are set
    - All parameters of the test setup and teardown are set

- When the execution finishes:
    - the Result is set to PASS (green icon) or FAIL (red icon)
    - the Log icon opens the RF log
