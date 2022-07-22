..
    Copyright (C) 2022 National Library of Technology, Prague.

    OARepo-Vocabularies is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.


REST API Docs
=============

CRUD
----

The CRUD works the same way as the regular CRUD operation.
The examples below are based upon the default invenio vocabulary
model, if you use a custom model, please update the schema accordingly.

Create a record
^^^^^^

.. code-block:: json

    // POST /v/universities/

    {
      "id": "uct",
      "title": {
        "en": "University of Chemistry and Technology, Prague"
      }
    }

Then you can either:

.. code-block:: json

    // POST /v/universities/

    {
      "id": "uct/fcht",
      "title": {
        "en": "Faculty of Chemical Technology"
      }
    }

Or:

.. code-block:: json

    // POST /v/universities/uct

    {
      "id": "fcht",
      "title": {
        "en": "Faculty of Chemical Technology"
      }
    }

Update a record
^^^^^^^^^^^^^^^

.. code-block:: json

    // PUT /v/universities/uct

    {
      "id": "uct",
      "title": {
        "en": "University of Chemistry and Technology, Prague"
      }
    }

Delete a record
^^^^^^^^^^^^^^^

.. code-block:: json

    // DELETE /v/universities/uct

Search
------

A traditional invenio search works for vocabularies as well,
both q-based and json based.

.. code-block:: json

    // GET /v/universities?q=Prague

   {
      "hits": [
          {...}
      ]
   }


Get record ancestors
--------------------

GET the item using `?hierarchy=ancestors` query:

.. code-block:: json

    // GET /v/universities/uct/fcht?hierarchy=ancestors

   {
      "id": "uct/fcht",
      "title": {
        "en": "Faculty of Chemical Technology"
      },
      "ancestors": [
          {
            "id": "uct",
            "title": {
              "en": "University of Chemistry and Technology, Prague"
            }
          }
      ]
   }

*Note*: this call os not paginated.

Get record children
-------------------

GET the item using `?hierarchy=children` query:

.. code-block:: json

    // GET /v/universities/uct

   {
        "id": "uct",
        "title": {
            "en": "University of Chemistry and Technology, Prague"
        }
        "children": [
            {
                "id": "uct/fcht",
                "title": {
                    "en": "Faculty of Chemical Technology"
                },
            }
        ]
   }

*Note*: this call os not paginated. If you need paginated children,
just create a direct search, that is:

``GET /v/universities?hierarchy_path:uct&hierarchy_level:2``

This will search any records with hierarchy starting with uct
and having level 2, that is all direct children.

Get descendants
---------------

Descendants work the same way as children does, but the "children"
property will be present on the children as well.

.. code-block:: json

    // GET /v/universities/uct
    // header: Accept: application/json+descendants

   {
        "id": "uct",
        "title": {
            "en": "University of Chemistry and Technology, Prague"
        }
        "children": [
            {
                "id": "uct/fcht",
                "title": {
                    "en": "Faculty of Chemical Technology"
                },
                "children": [
                     {
                        "id": "uct/fcht/ich",
                        // department of inorganic chemistry
                     }
                ]
            }
        ]
   }

*Note*: this call os not paginated. If you need paginated children,
just create a direct search, that is:

``GET /v/universities?hierarchy_path:uct``

This will search any records with hierarchy starting with uct
and having level 2, that is all direct children.


Field selection
---------------
