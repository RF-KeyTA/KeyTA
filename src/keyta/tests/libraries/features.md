# Add a library

- A library can be added by name, except when it was already imported
- A library with the name "test" must not be allowed to be added. (Message: ""test" ist keine Robot Framework Bibliothek")

# List view

- A library can be updated if the installed and imported versions differ

# Change view

Tabs: General, Keywords, Settings (if applicable)

- A library can be deleted

## General

- Anchor links work
- Cross-refs to keywords work
- External links are opened in a new window/tab
- Typehints work (for example: "Scope" in Browser library)

## Keywords

- The link to the keyword documentation works

## Settings

- A change to a value is saved automatically
- The default value can be restored
- The value is a number of listbox-options

## Delete

- A Library can be deleted: 

- a) If deleting the object does not cause consistency problems: >> "Durch das Löschen von Bibliothek "..." würden keine weiteren Objekte gelöscht. Möchten Sie fortfahren?" >> Ja // Nein

- b) If deleting the object would result in the deletion of other objects: >> "Das Löschen von Bibliothek "..." würde das Löschen der folgenden verknüpften Objekten als Folge haben. Möchten Sie fortfahren?" >> Ja // Nein

- c) If deleting the object is not possible for consistency reasons: >> "Das Löschen von Bibliothek "..." ist nicht möglich, da es die folgenden Verknüpfungen zerstören würde" >> OK
