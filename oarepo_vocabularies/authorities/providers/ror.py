import logging
from urllib.parse import quote_plus

import idutils
import requests
from oarepo_vocabularies.authorities.providers import AuthorityProvider
from requests.exceptions import RequestException
from werkzeug.exceptions import BadRequest

logger = logging.getLogger("oarepo-vocabularies.providers.ror")


class RORClientV2(object):
    """ROR v2 API client wrapper.

    ROR REST API client that allows users to retrieve,
    search, and filter the organizations indexed in ROR.
    """

    def __init__(self, url=None, testing=False, timeout=None, min_query_length=1):
        self.api_url = url or "https://api.ror.org/v2/organizations"
        self.min_query_length = min_query_length
        self.testing = testing
        if self.testing:
            self.api_url = "https://api.dev.ror.org/v2/organizations"

        self.timeout = timeout or 10000

    def quick_search(self, query="", page=1, **kwargs):
        """Search for ROR records matching the querystring.

        Performs a "quick search" of only the names and external_ids fields in ROR.
        Works best for the following purposes:

        - Keyword-based searching for organization names
        - Form field auto-suggests / typeaheads
        - Searching for exact matches of an organization name
        - Searching for external identifiers
        """
        if not query or len(query) < self.min_query_length:
            return {"items": [], "number_of_results": 0}

        headers = {"Accept": "application/json;charset=UTF-8"}
        query_params = {"query": quote_plus(query), "page": page}

        try:
            search_result = requests.get(
                self.api_url,
                timeout=self.timeout,
                headers=headers,
                params=query_params,
                **kwargs,
            ).json()
            return search_result
        except RequestException as e:
            logger.exception("ROR API query failed: %s", e)
            raise e

    def get_record(self, item_id, **kwargs):
        """Fetch a ROR record metadata by a given ROR PID.

        :param identity: User's identity
        :param item_id: ROR PID identifier value
        :return: Any
        """
        if not idutils.is_ror(item_id):
            raise BadRequest("{item_id} is not a valid ROR identifier.")

        pid = idutils.normalize_ror(item_id)

        record_url = f"{self.api_url}/{quote_plus(pid)}"

        response = requests.get(record_url, **kwargs)

        if response.status_code == 404:
            return None

        return response.json()

    def __repr__(self):
        """Create string representation of object."""
        return "<RORClientV2: {0}>".format(self.api_url)


class RORProviderV2(AuthorityProvider):

    def __init__(self, url=None, testing=False, **kwargs):
        self.ror_client = RORClientV2(url, testing, **kwargs)

    def search(self, identity, params, **kwargs):
        params = params or {}

        results = self.ror_client.quick_search(
            query=params.get("q", ""), page=params.get("page", 1), **kwargs
        )

        items = [self.to_vocabulary_item(ror_item) for ror_item in results.get("items")]
        total = results.get("number_of_results")

        return items, total, 20

    def get(self, identity, item_id, **kwargs):
        assert item_id.startswith("ror:")
        record = self.ror_client.get_record(item_id[4:])

        if not record:
            raise KeyError(item_id)

        return self.to_vocabulary_item(record)

    @staticmethod
    def to_vocabulary_item(ror_record):
        ror_id = idutils.normalize_ror(ror_record.get("id"))
        display_name = {}
        alt_names = {}
        acronyms = []
        other_names = []

        for n in ror_record.get("names"):
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

        locations = [
            f"{l['geonames_details']['name']}, {l['geonames_details']['country_name']}"
            for l in ror_record.get("locations", [])
        ]

        return {
            "id": f"ror:{ror_id}",
            "title": {**display_name, **alt_names},
            "tags": ror_record.get("types", []),
            "props": {
                "acronyms": ", ".join(acronyms),
                "otherNames": ", ".join(other_names),
                "locations": "; ".join(locations),
            },
            # NOTE: Requires RelatedURICF Vocabulary custom field enabled.
            "relatedURI": {"ror": idutils.to_url(ror_id, "ror", "https")}
        }
