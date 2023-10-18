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

## Authorities

It is possible to provide authority sources for vocabularies.
Configuration:

```python
VOCABULARY_TYPE_METADATA = {
    "funding": {    # vocabulary of funding
        "name": {
            "en": "Funding"
        },
        "authority": FundingService
    }
}
```

where:

```python
from oarepo_vocabularies.authorities import AuthorityService

class FundingService(AuthorityService):
    def search(self, query=None, page=1, size=10, **kwargs):
        # performs an API and returns a listing 
        # of serialized vocabulary items, for example:
        return {
            'hits': {
                'total': 2,
                'hits': [
                    {"id": "03zsq2967", "title": {"en": "Funding 1"}},
                    {"id": "a4gfhtt56", "title": {"en": "Funding 2"}}
                ]
            },
            # optional pagination links here
        }
    def get(self, item_id, *, uow, value, **kwargs):
        # performs lookup by id and returns vocabulary metadata
        
        # in this example:
        return next(x for x in self.search()['hits']['hits'] if x['id'] == item_id)
```

## Ordering

To support other than English ordering, `sort` custom field has been added to the vocabulary api. This
custom field automatically populates `sort.<lang>` mapping property for each language specified in the
configuration:

```python
# invenio.cfg
from oarepo_runtime.cf.icu import ICUSortCF

OAREPO_VOCABULARIES_SORT_CF = [ICUSortCF("cs", "czech", "title.cs")]
```