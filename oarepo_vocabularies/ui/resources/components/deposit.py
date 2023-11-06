import inspect
import json

import marshmallow
from flask import current_app
from flask_babelex import get_locale
from invenio_records import Record
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_vocabularies.proxies import current_service as vocabulary_service

from oarepo_vocabularies.records.api import find_vocabulary_relations
from oarepo_vocabularies.services.ui_schema import VocabularyI18nStrUIField

try:
    pass
except ImportError:
    pass


class DepositI18nHierarchySchema(marshmallow.Schema):
    title = marshmallow.fields.List(VocabularyI18nStrUIField())


class VocabularyPrefetchSchema(marshmallow.Schema):
    title = VocabularyI18nStrUIField(data_key="text")
    hierarchy = marshmallow.fields.Nested(
        DepositI18nHierarchySchema, data_key="hierarchy"
    )


class DepositVocabularyOptionsComponent(ServiceComponent):
    """
    This component is used in deposit form of normal records. For small vocabularies,
    it provides their values so that they might be displayed in, for example, a combo.
    """

    always_included_vocabularies = []

    def form_config(
        self, *, form_config, resource, record, view_args, identity, **kwargs
    ):
        """
        Adds vocabularies to the form config as in:
        ```
        "vocabularies": {
            "languages": {
              "definition": {...} # from INVENIO_VOCABULARY_TYPE_METADATA
              "all": [{"value": "...", "text": "..."}],
              "featured": [{"value": "...", "text": "..."}]
            },
            "bigVocabulary: {
                "definition": {...} # from INVENIO_VOCABULARY_TYPE_METADATA
                "url": "..."
            },
          }
        ```

        The vocabularies which should be handled this way are configured
        inside invenio.cfg:

        ```
        INVENIO_VOCABULARY_TYPE_METADATA = {
            "languages": {
                "dump_options": True,
                # more configuration here
            }
        ```
        """
        if not isinstance(record, Record):
            record_cls = resource.api_service.config.record_cls
            record = record_cls({})

        form_config.setdefault("vocabularies", {})

        if current_app.config.get("VOCABULARIES_LANGUAGES_DISABLED"):
            return

        vocabulary_config = current_app.config.get(
            "INVENIO_VOCABULARY_TYPE_METADATA", {}
        )

        used_vocabularies = [
            vocab_field.vocabulary_type
            for vocab_field in find_vocabulary_relations(record)
        ]

        for v in self.always_included_vocabularies:
            if v not in used_vocabularies:
                used_vocabularies.append(v)

        (
            vocabularies_to_prefetch,
            form_config_vocabularies,
        ) = self.create_form_config_vocabularies(
            vocabulary_config, used_vocabularies=used_vocabularies
        )

        form_config["vocabularies"] = form_config_vocabularies
        schema = VocabularyPrefetchSchema(context={"locale": get_locale()})
        for prefetched_item in self.prefetch_vocabulary_items(
            identity, vocabularies_to_prefetch
        ):
            by_type = form_config_vocabularies[prefetched_item["type"]]
            returned_item = {
                "value": prefetched_item["id"],
                **schema.dump(prefetched_item),
            }
            by_type["all"].append(returned_item)
            if "featured" in prefetched_item.get("tags", []):
                by_type["featured"].append(returned_item)

    @staticmethod
    def prefetch_vocabulary_items(identity, vocabularies_to_prefetch):
        if vocabularies_to_prefetch:
            yield from vocabulary_service.scan(
                identity,
                params={
                    "type": vocabularies_to_prefetch,
                    "sort": "title",
                    "source": [
                        "title",
                        "hierarchy.title",
                        "uuid",
                        "version_id",
                        "created",
                        "updated",
                        "pid",
                        "type",
                        "id",
                        "tags",
                    ],
                    "size": 1000,
                },
                # this needs the ScanningOrderComponent to be installed, otherwise does not sort
                preserve_order=True,
            )

    @staticmethod
    def create_form_config_vocabularies(
        vocabulary_config,
        used_vocabularies,
    ):
        form_config_vocabularies = {}
        vocabularies_to_prefetch = []
        for vocabulary_type in used_vocabularies:
            vocabulary_definition = vocabulary_config.get(vocabulary_type, {})
            form_config_vocabularies[vocabulary_type] = {
                "definition": json.loads(
                    json.dumps(vocabulary_definition, default=json_default)
                )
            }
            if vocabulary_definition.get("dump_options"):
                vocabularies_to_prefetch.append(vocabulary_type)
                form_config_vocabularies[vocabulary_type]["all"] = []
                form_config_vocabularies[vocabulary_type]["featured"] = []
            else:
                # TODO: use vocabulary service config and prefix???
                form_config_vocabularies[vocabulary_type][
                    "url"
                ] = f"/api/vocabularies/{vocabulary_type}"
        return vocabularies_to_prefetch, form_config_vocabularies


def json_default(x):
    if hasattr(x, "name"):
        return x.name
    if inspect.isclass(x):
        return x.__name__
    return type(x).__name__
