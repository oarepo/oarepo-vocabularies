from types import SimpleNamespace
from invenio_records_resources.services.base import ServiceItemResult, ServiceListResult
from invenio_records_resources.services.records.results import RecordList


class RORListResultV2(RecordList):
    """List of ROR API search result items."""

    @property
    def total(self):
        """Get total number of hits."""
        return self._results.get("number_of_results", None)

    @property
    def aggregations(self):
        """Get the search result aggregations."""
        return None

    @property
    def hits(self):
        """Iterator over the hits."""
        for record in self._results["hits"]:
            record = SimpleNamespace(**record)
            # Project the record
            projection = self._schema.dump(
                record,
                context=dict(
                    identity=self._identity,
                    record=record,
                ),
            )

            projection = self.to_vocabulary_item(projection)

            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(
                    self._identity, record
                )
            if self._nested_links_item:
                for link in self._nested_links_item:
                    link.expand(self._identity, record, projection)

            yield projection

    @staticmethod
    def to_vocabulary_item(hit):
        ror_id = hit.pop("id")
        names = hit.pop("names")
        # The name of the organization shown as the main heading of the
        # organization’s record in the ROR user interface.
        # Each record must have exactly 1 name with type = ror_display.
        display_name = {
            n.get("lang") or "en": n["value"]
            for n in names
            if "ror_display" in n["types"]
        }

        # Alternative name of the organization in other languages than
        # display name.
        alt_names = {
            n.get("lang") or "en": n["value"]
            for n in names
            if "label" in n["types"]
            and (n["lang"] and n["lang"] not in display_name.keys())
        }
        props = {**hit}

        # Acronyms or initialisms for the organization name.
        acronyms = [a["value"] for a in names if "acronym" in a["types"]]
        if acronyms:
            props.update({"acronyms": acronyms})

        res = {
            "id": ror_id,
            "title": {**display_name, **alt_names},
            "props": props,
        }
        return res

    def to_dict(self):
        """Return result as a dictionary."""
        hits = list(self.hits)

        res = {
            "hits": {
                "hits": hits,
                "total": self.total,
            }
        }

        if self._params:
            if self._links_tpl:
                res["links"] = self._links_tpl.expand(self._identity, self.pagination)

        return res


class RORItemV2(ServiceItemResult):
    """Single ROR v2 API search result item."""

    def __init__(
        self,
        service,
        identity,
        record,
        errors=None,
        links_tpl=None,
        schema=None,
        expandable_fields=None,
        expand=False,
        nested_links_item=None,
    ):
        """Constructor."""
        pass
