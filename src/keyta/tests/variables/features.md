# List view

- Reference Values can be filtered by System and by Window

- Reference Values can be searched by name

- Reference Values are sorted by name alphabetically


# Add form

- A Reference Value can be created
    - At least one name-value pair has to be provided


# Change form

- A change to the name or the systems is saved automatically


## General
- Removing the only System will result in a notification and won't be saved.
- Creating a new Variable with mandatory fields: System, Name, Type (Art)


## Values

- A change to the name or the value is saved automatically

- A name-value pair can be added

- Each name must be unique


## Delete
- A Variable can be deleted:
- a) If deleting the object does not cause consistency problems: >> "Durch das Löschen von Referenzwert "..." würden keine weiteren Objekte gelöscht. Möchten Sie fortfahren?" >> Ja // Nein

- b) If deleting the object would result in the deletion of other objects: >> "Das Löschen von Referenzwert "..." würde das Löschen der folgenden verknüpften Objekten als Folge haben. Möchten Sie fortfahren?" >> Ja // Nein

- c) If deleting the object is not possible for consistency reasons: >> "Das Löschen von Referenzwert "..." ist nicht möglich, da es die folgenden Verknüpfungen zerstören würde" >> OK
