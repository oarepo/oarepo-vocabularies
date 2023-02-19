# OARepo vocabularies

This is an extension of invenio vocabularies that allows:

* Use the vocabularies with custom fields
* Treat vocabulary items as hierarchy

## Installation

Add `oarepo-runtime`, `oarepo-vocabularies` to your virtualenv an set up the following in your `invenio.cfg`:

```python
from oarepo_vocabularies.services.config import VocabulariesConfig
from oarepo_vocabularies.resources.config import VocabulariesResourceConfig

VOCABULARIES_SERVICE_CONFIG = VocabulariesConfig
VOCABULARIES_RESOURCE_CONFIG = VocabulariesResourceConfig
```

## Documentation

See [NRP documentation](https://narodni-repozitar.github.io/developer-docs/docs/technology/invenio/nrp-toolchain/plugins/vocabularies) for more details.
