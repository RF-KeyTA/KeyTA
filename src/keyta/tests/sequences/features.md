# List view

- Sequences can be filtered by:
  - System
  - Window

- Sequences can be searched by name

- The link to a Sequence works

# Add view

- A new Sequence can be added

# Change view

## Tabs: General, Parameters, Steps, Return Value, Execution

### General

- A change to a form field is saved automatically

### Parameters

- Parameters can be:
  - Added: saved automatically
  - Deleted: redirect to the Parameters tab
  - Sorted: saved automatically

### Steps

- Steps can be:
  - Added: saved automatically
  - Deleted: redirect to the Steps tab
  - Sorted: saved automatically

- Only actions from the window can be called

- If a step has no parameters the Values icon is shown in order to define a return value
- If a step has missing parameters the Values icon is pink

#### Keyword Call

Inlines: Parameters (if applicable), Return values

- A keyword call parameter can be:
  - a parameter of the calling keyword (if any)
  - a previous return value (if any)
  - user input

- Return values can be added/deleted

### Return Value

- If any step has a return value it can be chosen as the return value of the Sequence


### Execution

- If the Sequence has parameters:
  - they can be configured in the Execution tab
  - if they are incomplete the icon for the Values is pink

- In the settings:
  - The libraries imported by the actions from the steps are included
  - Libraries that have settings can be configured
  - The action for attaching to a system can be selected and (de)activated
  - If the setup action has parameters:
    - If they are incomplete the icon for the Values is pink
  - In the setup call:
    - The link to the documentation of the keyword works
    - There are no fields, only the Parameters inline
    - Then only choices for the parameters are:
      - user input
      - window-independent variables

- When the execution is started it aborts if any of the following is true:
  - the call parameters are incomplete
  - the parameters of the setup are incomplete
  - the parameters of a step are incomplete


## Buttons: Delete, Clone

- Cloning the Sequence produces an identical Sequence with the suffix Copy
- Deleting a Sequence works
