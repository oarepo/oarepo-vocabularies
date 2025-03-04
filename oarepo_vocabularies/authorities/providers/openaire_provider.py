import base64
import logging
from flask import current_app
import requests

from oarepo_vocabularies.authorities.providers.base import AuthorityProvider


logger = logging.getLogger("oarepo-vocabularies.providers.openaire")


class OpenAIREClient(object):

    def __init__(
        self, client_id, client_secret, url=None, testing=False, timeout=None, **kwargs
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.testing = testing
        self.timeout = timeout or 10000

    def _get_token(self):
        url = "https://aai.openaire.eu/oidc/token"
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )

        headers = {"Authorization": f"Basic {encoded_credentials}"}

        data = {"grant_type": "client_credentials"}

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            logger.error(f"Other error occurred: {err}")

    def quick_search(self, access_token, search_query="", page=1, page_size=20):
        url = "https://api.openaire.eu/search/projects?format=json"
        if not access_token:
            return {}
        headers = {"Authorization": f"Bearer {access_token.strip()}"}

        if not search_query or search_query == "":
            return {}

        params = {"name": search_query, "page": page, "size": page_size}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            logger.error(f"Error response: {response.status_code}")
            logger.error(f"Response content: {response.text}")
        response.raise_for_status()
        return response.json()

    def get_record(self, item_id, access_token):
        url = f"https://api.openaire.eu/search/projects?openaireProjectID={item_id}&format=json"

        headers = {"Authorization": f"Bearer {access_token.strip()}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


class OpenAIREProvider(AuthorityProvider):

    _cached_token = None

    def __init__(self, url=None, testing=False, **kwargs):
        self.openaire_client = OpenAIREClient(
            current_app.config["OPENAIRE_CLIENT_ID"],
            current_app.config["OPENAIRE_CLIENT_SECRET"],
            url,
            testing,
            **kwargs,
        )

    def get_access_token(self):
        if self._cached_token is None:
            self._cached_token = self.openaire_client._get_token()
        return self._cached_token

    def search(self, identity, params, **kwargs):
        params = params or {}
        access_token = self.get_access_token()

        response = self.openaire_client.quick_search(
            access_token=access_token,
            search_query=params.get("q", ""),
            page=params.get("page", 1),
            page_size=params.get("page_size", 20),
        )

        results = response.get("response", {})

        if not results:
            return [], 0

        items = [
            self.to_vocabulary_item(openaire_item)
            for openaire_item in results.get("results", []).get("result", [])
        ]
        total = OpenAIREProvider.dict_get(results, "header", "total", "$")

        return items, total

    def get(self, identity, item_id, **kwargs):

        access_token = self.get_access_token()

        record = self.openaire_client.get_record(item_id, access_token)

        if record is None:
            raise KeyError(f"OpenAIRE record {item_id} not found.")

        return self.to_vocabulary_item(record.get("response", {}))

    @staticmethod
    def dict_get(d, *args, default={}):
        """Iteratively reach for a key in a nested dictionary"""
        for path in args:
            if not isinstance(d, dict) or path not in d:
                return default
            d = d[path]
        return d

    @staticmethod
    def get_program_from_funding(funding_tree):
        """Explicitly search for the first program in the funding tree"""

        if not funding_tree:
            return "N/A"

        funder_info = (
            funding_tree[0].items()
            if isinstance(funding_tree, list)
            else funding_tree.items()
        )

        for _, value in funder_info:
            program = OpenAIREProvider._extract_program(value)
            if program:
                return program

        return "N/A"

    @staticmethod
    def _extract_program(value):
        """Helper function to extract program from a value"""
        if isinstance(value, dict):
            if "parent" in value and value["parent"]:
                program = OpenAIREProvider._extract_program(value["parent"])
                if program:
                    return program.get("class", {}).get("$", "N/A")

            return value.get("class", {}).get("$", "N/A")

        return None

    @staticmethod
    def to_vocabulary_item(record):
        # Parse the record
        header = record.get("header", {})
        metadata = record.get("metadata", {})
        entity = metadata.get("oaf:entity", {})
        project = entity.get("oaf:project", {})

        rels = project.get("rels")
        if isinstance(rels, dict):
            relations = rels.get("rel", [])
        else:
            relations = []

        # If there is only one relation, convert it to a list
        if not isinstance(relations, list):
            relations = [relations]

        # Tags (keywords)
        keywords = project.get("keywords", "")

        if isinstance(keywords, dict):
            keywords = keywords.get("$", "")
        tags = keywords.split(",")

        # Identifiers
        identifiers = []

        identifiers.append(
            {
                "identifier": header.get("dri:objIdentifier", {}).get("$", ""),
                "scheme": "dri:objIdentifier",
            }
        )

        identifiers.append(
            {
                "identifier": project.get("originalId", {}).get("$", ""),
                "scheme": "openaire:originalId",
            }
        )

        # Number (code), title (with locale) and acronym
        number = project.get("code", {}).get("$", "")
        title = {
            header.get("locale", {})
            .get("$", "en")[:2]: project.get("title", {})
            .get("$", "")
        }
        acronym = project.get("acronym", {}).get("$", "")

        # Funder and according program
        funding = project.get("fundingtree", [])

        funder = {
            "id": OpenAIREProvider.dict_get(funding, "funder", "id", "$") or "",
            "name": OpenAIREProvider.dict_get(funding, "funder", "name", "$") or "",
        }

        program = OpenAIREProvider.get_program_from_funding(funding)

        # Subjects and organizations
        subjects = []

        subject_list = project.get("subject", [])

        if not isinstance(subject_list, list) and subject_list:
            subject_list = [subject_list]

        for subject in subject_list:
            if subject and isinstance(subject, dict):
                subjects.append(
                    {"id": subject.get("@classid", ""), "subject": subject.get("$", "")}
                )

        organizations = []

        for relation in relations:

            relation_to = relation.get("to", "")
            organizations.append(
                {
                    "scheme": relation_to.get("@scheme", ""),
                    "id": relation_to.get("$", ""),
                    "organization": relation.get("legalname", {}).get("$", ""),
                }
            )

        return {
            "$schema": "local://awards/award-v1.0.0.json",
            "tags": tags,
            "identifiers": identifiers,
            "number": number,
            "title": title,
            "funder": funder,
            "acronym": acronym,
            "program": program,
            "subjects": subjects,
            "organizations": organizations,
        }
