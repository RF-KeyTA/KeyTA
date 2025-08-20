# List view

- Actions can be filtered by:
  - System
  - Window
  - Setup/Teardown

- Actions can be searched by name

- The link to an Action works

# Add view

- A new action can be added

# Change view

- An action can be deleted

## Tabs: General, Windows, Libraries, Parameters, Steps, Return Value, Execution

### General

- A change to a form field is saved automatically
- Removing the last System will result in a notification and won't be saved.
  
### Windows

- An action can be (un)linked with a Window
- The only choices are windows that have not been associated with the Action

### Libraries

- A library can be imported, unless it is already imported

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

- Only keywords from the imported libraries can be chosen

- If a step has no parameters the Values icon is shown in order to define a return value
- If a step has missing parameters the Values icon is pink
- If the parameters are set the Values icon is blue

#### Keyword Call

Fields: Documentation, Condition (optional)

- The link to the documentation works
- The condition can be set and unset

Inlines: Parameters (if applicable), Return values

- A keyword call parameter can be:
  - a parameter of the calling keyword (if any)
  - a previous return value (if any)
  - user input

- Return values can be added/deleted

### Return Value

- If any step has a return value it can be chosen as the return value of the action


### Execution

- If the keyword has parameters:
  - they can be configured in the execution
  - if they are incomplete the icon for the Values is pink
  - If the parameters are set the Values icon is blue

- In the settings:
  - The libraries imported by the action are included
  - Libraries that have settings can be configured
  - The action for attaching to a system can be selected and (de)activated
  - If the setup action has parameters:
    - If they are incomplete the icon for the Values is pink
    - If the parameters are set the Values icon is blue
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


## Buttons: Delete, Clone, Save

- Cloning the Action produces an identical Action with the suffix Copy
- Deleting an action works
      - a) If deleting the object does not cause consistency problems:
         >> "Durch das Löschen von Aktion "..." würden keine weiteren Objekte gelöscht. Möchten Sie fortfahren?"
         >> Ja   //    Nein
      - b) 
- Trying to Save an empty Action will result in a notification and the Action won't be saved.
