# List View

- A new Window can be created

- Windows can be filterd by system

- Windows can be searched by name

- Each window has a preview icon. When clicking the icon the documentation is shown in a modal.


# Change form

- A Window has the tabs:

  - General
  - Templates
  - Resources
  - Actions
  - Sequences
  - Reference Values



## General

- A Window is not allowed to have no System (trying to remove the last System will result in a notification and it won't be saved)
- A Window can be deleted (only if there is no Sequence attached to it)

## Templates

- In the Templates tab a template can be created by adding another template and clicking on the plus icon

    - A template must define at least one field

- When a field is added/deleted it is added/deleted to/from all the Reference Values that use the template

- Field names must be unique

- When the fields are reordered the form is automatically saved. The current order is reflected in all the Reference Values that use the template

- When renaming a field the form is automatically saved. The current field names are reflected in all the Reference Values that use the template

- When renaming the template the form is automatically saved


## Resources

- In the Resources tab a Resource can be imported only once

- When a Resource Import is added/deleted, its keywords are (un)available for use in:

   - Every Test Step that refers to the Window
   - Every Sequence in the Window

- A Resource Import cannot be deleted if a keyword from the Resource is called by a test step or a sequence


## Actions

- In the Actions tab an Action can be added to the window by adding another action and clicking on the plus icon


## Sequences

- In the Sequences tab a Sequence can be added to the window by adding another sequence and clicking on the plus icon


## Reference Values

- In the Reference Values tab a Reference Value can be added to the window by adding another reference value and clicking on the plus icon

   - The available templates are the ones associated with the Window
   
   - A Reference Value with Quantity "One instance" can be added

   - A Reference Value with Quantity "Several instances" can be added
