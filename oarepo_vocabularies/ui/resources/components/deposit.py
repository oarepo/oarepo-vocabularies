import inspect
import json
from typing import Any, Dict

from flask import current_app
from invenio_records import Record
from oarepo_ui.resources.components import UIResourceComponent

from oarepo_vocabularies.proxies import current_ui_vocabulary_cache
from oarepo_vocabularies.records.api import find_vocabulary_relations


class DepositVocabularyOptionsComponent(UIResourceComponent):
    """
    This component is used in deposit form of normal records. For small vocabularies,
    it provides their values so that they might be displayed in, for example, a combo.
    """

    always_included_vocabularies = []

    def form_config(self, *, form_config, api_record, view_args, identity, **kwargs):
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
        if not isinstance(api_record, Record):
            record_cls = self.resource.api_service.config.record_cls  # noqa
            api_record = record_cls({})

        form_config.setdefault("vocabularies", {})

        if current_app.config.get("VOCABULARIES_LANGUAGES_DISABLED"):
            return

        vocabulary_config = current_app.config.get(
            "INVENIO_VOCABULARY_TYPE_METADATA", {}
        )

        used_vocabularies = self._get_used_vocabularies(api_record)

        (
            vocabularies_to_prefetch,
            form_config_vocabularies,
        ) = self.create_form_config_vocabularies(
            vocabulary_config, used_vocabularies=used_vocabularies
        )

        form_config["vocabularies"] = form_config_vocabularies
        self._prefetch_vocabularies_to_form_config(
            form_config_vocabularies, vocabularies_to_prefetch, identity
        )

        for vocabularies in form_config["vocabularies"].values():
            if "all" in vocabularies:
                for voc in vocabularies["all"]:
                    for _voc in vocabularies["all"]:
                        if voc["value"] in _voc["hierarchy"]["ancestors"]:
                            voc["element_type"] = "parent"
                            break
                    if "element_type" not in voc:
                        voc["element_type"] = "leaf"

    def _get_used_vocabularies(self, api_record):
        used_vocabularies = [
            vocab_field.vocabulary_type
            for vocab_field in find_vocabulary_relations(api_record)
        ]
        for v in self.always_included_vocabularies:
            if v not in used_vocabularies:
                used_vocabularies.append(v)
        return used_vocabularies

    def _prefetch_vocabularies_to_form_config(
        self, form_config_vocabularies, vocabularies_to_prefetch, identity
    ):
        prefetched_vocabularies: Dict[str, Dict[str, Any]]
        prefetched_vocabularies = current_ui_vocabulary_cache.get(
            vocabularies_to_prefetch
        )
        for vocabulary_type, items in prefetched_vocabularies.items():
            for item_id, item in items.items():
                by_type = form_config_vocabularies[vocabulary_type]
                returned_item = {
                    "value": item_id,
                    **item,
                }
                by_type["all"].append(returned_item)
                if "featured" in returned_item.get("tags", []):
                    by_type["featured"].append(returned_item)

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
