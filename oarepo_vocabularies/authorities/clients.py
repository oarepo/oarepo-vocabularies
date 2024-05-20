import json
import requests
from urllib.parse import urlencode, urljoin

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
           self.api_url = 'https://api.dev.ror.org/v2/organizations'

        self.timeout = timeout or 10000
        self.page_size = page_size or 20

    def quick_search(self, query):
        """Search for ROR records matching the querystring.

        Performs a "quick search" of only the names and external_ids fields in ROR.
        Works best for the following purposes:

        - Keyword-based searching for organization names
        - Form field auto-suggests / typeaheads
        - Searching for exact matches of an organization name
        - Searching for external identifiers
        """
        headers = {"Accept": "application/json;charset=UTF-8"}
        search_url = f"{self.api_url}?{urlencode(('query', query))}"
    
        search_result = json.loads(
            requests.get(search_url, timeout=self.timeout, headers=headers)
        )

    def __repr__(self):
        """Create string representation of object."""
        return "<RORClientV2: {0}>".format(self.url)
