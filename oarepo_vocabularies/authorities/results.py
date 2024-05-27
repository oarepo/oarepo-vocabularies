from copy import deepcopy
from types import SimpleNamespace

from invenio_records_resources.pagination import Pagination
from invenio_records_resources.services.records.results import RecordList, RecordItem


def to_vocabulary_item(ror_record):
    projection = deepcopy(ror_record)

    ror_id = projection.pop("id")
    names = projection.pop("names")
    display_name = {}
    alt_names = {}
    acronyms = []
    other_names = []

    for n in names:
        if "ror_display" in n["types"]:
            # The name of the organization shown as the main heading of the
            # organization’s record in the ROR user interface.
            # Each record must have exactly 1 name with type = ror_display.
            display_name = {n.get("lang") or "en": n["value"]}
        elif "label" in n["types"] and (
            n["lang"] and n["lang"] not in display_name.keys()
        ):
            # Alternative names in other languages
            alt_names[n.get("lang")] = n["value"]
        elif "acronym" in n["types"]:
            # Acronyms or initialisms for the organization name.
            acronyms.append(n["value"])
        else:
            other_names.append(n["value"])

    types = projection.pop("types", [])
    links = [f"{l['type']}:{l['value']}" for l in projection.pop("links", [])]
    locations = [
        f"{l['geonames_details']['name']}, {l['geonames_details']['country_name']}"
        for l in projection.pop("locations", [])
    ]

    props = {**projection}

    if acronyms:
        props.update({"acronyms": ", ".join(acronyms)})
    if other_names:
        props.update({"otherNames": ", ".join(other_names)})
    if types:
        props.update({"types": ", ".join(types)})
    if links:
        props.update({"links": ", ".join(links)})
    if locations:
        props.update({"locations": "; ".join(locations)})

    res = {
        "id": ror_id,
        "title": {**display_name, **alt_names},
        "props": props,
    }
    return res


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
    def pagination(self):
        """Create a pagination object."""
        return Pagination(
            self._params["size"],
            self._params.get("page", 1),
            self.total,
        )

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

            projection = to_vocabulary_item(projection)

            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(
                    self._identity, record
                )
            if self._nested_links_item:
                for link in self._nested_links_item:
                    link.expand(self._identity, record, projection)

            yield projection

    def to_dict(self):
        """Return result as a dictionary."""
        hits = list(self.hits)

        res = {
            "hits": {
                "hits": hits,
                "total": self.total,
            }
        }

        if self._params and self._links_tpl:
            res["links"] = self._links_tpl.expand(self._identity, self.pagination)

        return res


class RORItemV2(RecordItem):
    """Single ROR v2 API search result item."""

    @property
    def links(self):
        """Get links for this result item."""
        return self._links_tpl.expand(self._identity, self._obj)

    @property
    def data(self):
        """Property to get the record."""
        if self._data:
            return self._data

        self._data = self._schema.dump(
            self._obj,
            context=dict(
                identity=self._identity,
                record=self._record,
            ),
        )

        self._data = to_vocabulary_item(self._data)

        if self._links_tpl:
            self._data["links"] = self.links

        if self._nested_links_item:
            for link in self._nested_links_item:
                link.expand(self._identity, self._record, self._data)

        return self._data

    @property
    def _obj(self):
        """Return the object to dump."""
        return SimpleNamespace(**self._record)

    @property
    def id(self):
        """Get the record id."""
        return self._obj.id
