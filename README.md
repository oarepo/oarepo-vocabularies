# OARepo taxonomies

This is an extension of invenio vocabularies that allows:

* Use the vocabularies with custom fields
* Treat vocabulary items as hierarchy

## Installation

Add `oarepo-runtime`, `oarepo-taxonomies` to your virtualenv an set up the following in your `invenio.cfg`:

```python
from oarepo_taxonomies.services.config import TaxonomiesConfig
from oarepo_taxonomies.resources.config import TaxonomiesResourceConfig

VOCABULARIES_SERVICE_CONFIG = TaxonomiesConfig
VOCABULARIES_RESOURCE_CONFIG = TaxonomiesResourceConfig
```
