from invenio_records_resources.services.records.components import ServiceComponent


class ScanningOrderComponent(ServiceComponent):
    def scan(self, identity, search, params):
        if params.get("preserve_order"):
            return search.params(preserve_order=True)
        return search
