from invenio_records_resources.services.records.components import ServiceComponent


class KeepVocabularyIdComponent(ServiceComponent):
    def update(self, identity, data=None, record=None, **kwargs):
        if "id" not in data:
            data["id"] = record["id"]
