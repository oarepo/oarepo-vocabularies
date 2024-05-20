import logging
import requests
from urllib.parse import quote_plus
from invenio_records_resources.pagination import Pagination
from requests.exceptions import RequestException, JSONDecodeError
from invenio_records_rest.errors import SearchPaginationRESTError

HTTP_OK = requests.codes["ok"]

logger = logging.getLogger("oarepo-vocabularies")


class RORClientV2(object):
    """ROR v2 API client wrapper.

    ROR REST API client that allows users to retrieve,
    search, and filter the organizations indexed in ROR.
    """

    def __init__(self, url=None, testing=False, timeout=None, page_size=None):
        self.api_url = url or "https://api.ror.org/v2/organizations"
        self.testing = testing
        if self.testing:
            self.api_url = "https://api.dev.ror.org/v2/organizations"

        self.timeout = timeout or 10000
        self.page_size = page_size or 20

    def quick_search(self, query, page=1, size=10):
        """Search for ROR records matching the querystring.

        Performs a "quick search" of only the names and external_ids fields in ROR.
        Works best for the following purposes:

        - Keyword-based searching for organization names
        - Form field auto-suggests / typeaheads
        - Searching for exact matches of an organization name
        - Searching for external identifiers
        """
        headers = {"Accept": "application/json;charset=UTF-8"}
        current_page = Pagination(self.page_size, page, size)
        print(query, page, size)
        query_params = {"query": quote_plus(query), "page": current_page.page}

        if not current_page.valid():
            raise SearchPaginationRESTError(
                description=f"The requested page #{page} is outside the range of available pages",
            )

        try:
            search_result = requests.get(
                self.api_url,
                timeout=self.timeout,
                headers=headers,
                params=query_params,
            ).json()
            return search_result
        except (RequestException, JSONDecodeError) as e:
            logger.exception("ROR API query failed: %s", e)
            raise e

    def __repr__(self):
        """Create string representation of object."""
        return "<RORClientV2: {0}>".format(self.api_url)
