import math
from oarepo_vocabularies.authorities.clients import RORClientV2
from oarepo_vocabularies.authorities.service import AuthorityService
from invenio_records_resources.pagination import Pagination


class RORService(AuthorityService):
    
    def __init__(self, url=None):
        self.client = RORClientV2(url)

    def search(self, *, query=None, page=1, size=10, **kwargs):
        affiliations = []
        total = 0
        pagination = Pagination(size, page, )

        for offset in range(n_api_pages, 0, -1):
            # the offset is the page offset from the last page we need to fetch,
            # i.e. we fetch api_page e.g. 2, 3, 4 as offset is decreases with each iteration
            api_page = math.ceil(page * size_ratio) - offset + 1

            params = {"query": query, "page": api_page}
            response_json = fetch_json(self.search_url, params=params)
            total = response_json["number_of_results"]

            affiliations += [
                self.convert_ror_record(hit) for hit in response_json["items"]
            ]

        # make sure we don't return elements beyond the last page
        if page > get_last_page(total, size):
            hits = empty_hits(total, page)
        else:
            hits = affiliations

        # construct the return object
        start_pos = start_pos_api_page(page, size, api_size)
        hits = hits[start_pos : start_pos + size]
        links = make_links(
            query, page, size, total, vocabulary_type="affiliations", **kwargs
        )
        return hit_dict(hits, total, links)

    def get(self, item_id, **kwargs):
        if not item_id.startswith("ror:"):
            raise KeyError(f'item_id, "{item_id}", is not a ROR id')
        response_json = fetch_json(f"{self.get_url}{item_id[4:]}")
        return self.convert_ror_record(response_json)

    @staticmethod
    def convert_ror_record(hit):
        aff_entry = {
            "id": f"ror:{hit['id'].split('/')[-1]}",
            "title": {"en": hit["name"]},
            "props": {
                "city": hit["addresses"][0]["city"],
                "country": hit["country"]["country_name"],
            },
        }
        state = hit["addresses"][0].get("state")
        if state:
            aff_entry["props"]["state"] = state
        return aff_entry
