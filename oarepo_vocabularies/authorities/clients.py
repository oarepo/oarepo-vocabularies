import logging
import idutils
import requests
from urllib.parse import quote_plus
from invenio_records_resources.pagination import Pagination
from requests.exceptions import RequestException
from invenio_records_rest.errors import SearchPaginationRESTError
from werkzeug.exceptions import BadRequest

HTTP_OK = requests.codes["ok"]

logger = logging.getLogger("oarepo-vocabularies")


class RORClientV2(object):
    """ROR v2 API client wrapper.

    ROR REST API client that allows users to retrieve,
    search, and filter the organizations indexed in ROR.
    """

    def __init__(
        self, url=None, testing=False, timeout=None, page_size=None, min_query_length=1
    ):
        self.api_url = url or "https://api.ror.org/v2/organizations"
        self.min_query_length = min_query_length
        self.testing = testing
        if self.testing:
            self.api_url = "https://api.dev.ror.org/v2/organizations"

        self.timeout = timeout or 10000
        self.page_size = page_size or 20

    def quick_search(self, params, **kwargs):
        """Search for ROR records matching the querystring.

        Performs a "quick search" of only the names and external_ids fields in ROR.
        Works best for the following purposes:

        - Keyword-based searching for organization names
        - Form field auto-suggests / typeaheads
        - Searching for exact matches of an organization name
        - Searching for external identifiers
        """
        query, page, size = (
            params.get("q"),
            params.get("page", 1),
            # Size param is not implemented by the API & fixed to 20 items per page
            self.page_size,
        )

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

        return requests.get(record_url).json()

    def __repr__(self):
        """Create string representation of object."""
        return "<RORClientV2: {0}>".format(self.api_url)
