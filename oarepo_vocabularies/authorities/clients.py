import json
import requests
from urllib.parse import quote_plus, urljoin
from invenio_records_resources.pagination import Pagination
from requests import JSONDecodeError

HTTP_OK = requests.codes["ok"]


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

    def quick_search(self, query, size=10):
        """Search for ROR records matching the querystring.

        Performs a "quick search" of only the names and external_ids fields in ROR.
        Works best for the following purposes:

        - Keyword-based searching for organization names
        - Form field auto-suggests / typeaheads
        - Searching for exact matches of an organization name
        - Searching for external identifiers
        """
        headers = {"Accept": "application/json;charset=UTF-8"}
        query_params = {"query": quote_plus(query)}
        current_page = Pagination(self.page_size, 1, size)

        with requests.Session() as session:
            while current_page and current_page.valid():
                query_params["page"] = current_page.page

                try:
                    hits = session.get(
                        self.api_url,
                        timeout=self.timeout,
                        headers=headers,
                        params=query_params,
                    ).json()
                except ConnectionError as e:

                    yield []

                for item in hits["items"]:
                    yield item

                results_count = hits["number_of_results"]
                if results_count < self.page_size:
                    break

                current_page = current_page.next_page if current_page.has_next else None

    def __repr__(self):
        """Create string representation of object."""
        return "<RORClientV2: {0}>".format(self.api_url)
