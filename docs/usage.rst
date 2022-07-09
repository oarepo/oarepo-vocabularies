..
    Copyright (C) 2022 National Library of Technology, Prague.

    OARepo-Vocabularies is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.


Usage
=====

Vocabulary record structure
---------------------------

This library builds upon the vocabulary record structure defined in
invenio-vocabularies (not in the contrib part).

It can be used as-is if the properties defined there are sufficient
or one can extend the model to add custom properties.

The built-in properties are:

* `title`: an object where keys are two-letter language code and value the title
* `description`: an object where keys are two-letter language code and value the description
* `icon`: a string with icon name
* `tags`: an array of tags (strings)
* `props`: an object with any keys and values of type string

The built-in structure also requires that the persistent identifiers
itself represent a hierarchical slug, for example:

* `uct` - University of Chemistry and Technology, Prague
* `uct/fcht` - Faculty of Chemical Technology at the University of Chemistry and Technology


