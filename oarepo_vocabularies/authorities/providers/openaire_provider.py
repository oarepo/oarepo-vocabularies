import base64
import logging
import os
from flask import current_app
import idutils
import requests

from oarepo_vocabularies.authorities.providers.base import AuthorityProvider


logger = logging.getLogger("oarepo-vocabularies.providers.openaire")

class OpenAIREClient(object):
    
    def __init__(self, client_id, client_secret, url=None, testing=False, timeout=None, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret
        self.testing = testing 
        self.timeout = timeout or 10000
        
    def get_token(self):
        url = "https://aai.openaire.eu/oidc/token"
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status() 
            return response.json().get("access_token")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")
    
    def quick_search(self, access_token, search_query="", page=1, page_size=20 ):
        url = "https://api.openaire.eu/search/projects?format=json"
        if not access_token:
            return {}
        headers = {
            "Authorization": f"Bearer {access_token.strip()}"
        }
        
        if not search_query or search_query == "":
            return {}
        
        params = {
            "name": search_query,
            "page": page,
            "size": page_size
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error response: {response.status_code}")
            print(f"Response content: {response.text}")
        response.raise_for_status()
        return response.json()
    
    def get_record(self, item_id, access_token):
        url = f"https://api.openaire.eu/search/projects?openaireProjectID={item_id}&format=json"
        
        headers = {
            "Authorization": f"Bearer {access_token.strip()}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
            
    
class OpenAIREProvider(AuthorityProvider):
    
    def __init__(self, url=None, testing=False, **kwargs):
        try:
            client_id = current_app.config["OPENAIRE_CLIENT_ID"]
            client_secret = current_app.config["OPENAIRE_CLIENT_SECRET"]
        except RuntimeError:
            client_id = os.environ["INVENIO_OPENAIRE_CLIENT_ID"]
            client_secret = os.environ["INVENIO_OPENAIRE_CLIENT_SECRET"]
        except KeyError:
            raise KeyError("OPENAIRE_CLIENT_ID and OPENAIRE_CLIENT_SECRET must be set in the configuration or as environment variables.")
        self.openaire_client = OpenAIREClient(client_id, client_secret, url, testing, **kwargs)
        
    def search(self, identity, params, **kwargs):
        params = params or {}
        access_token = self.openaire_client.get_token()
        
        response = self.openaire_client.quick_search(
            access_token=access_token,
            search_query=params.get("q", ""),
            page=params.get("page", 1),
            page_size=params.get("page_size", 20)
        )
        
        results = response.get("response", {})
        
        if not results:
            return [], 0
        
        items = [self.to_vocabulary_item(openaire_item) for openaire_item in results.get("results", []).get("result", [])]
        total = OpenAIREProvider.dict_get(results, "header", "total", "$")

        
        return items, total
        

    
    def get(self, identity, item_id, **kwargs):
        
        access_token = self.openaire_client.get_token()
        
        record = self.openaire_client.get_record(item_id, access_token)
        
        if record is None:
            raise KeyError(f"OpenAIRE record {item_id} not found.")
        
        return self.to_vocabulary_item(record.get("response", {}))
    
    @staticmethod
    def dict_get(d, *args, default={}):
        """ Iteratively reach for a key in a nested dictionary """
        for path in args:
            if not isinstance(d, dict) or path not in d:
                return default
            d = d[path]
        return d
    
    @staticmethod
    def get_program_from_funding(funding_tree):
        """ Explicitly search for the first program in the funding tree """
        if funding_tree == []:
            return "N/A"
        if isinstance(funding_tree, list):
            funder_info = funding_tree[0].items()        
        else:
            funder_info = funding_tree.items()
            
        for _, value in funder_info:
            if isinstance(value, dict):
                if "parent" in value and value["parent"] is not None:
                    for _, value in value["parent"].items():
                        if "class" in value:
                            return value["class"]["$"]
                if "class" in value:
                    return value["class"]["$"]
                
        return "N/A"
    
    @staticmethod
    def to_vocabulary_item(record):
        
        # Parse the record
        header = record.get("header", {})
        metadata = record.get("metadata", {})
        entity = metadata.get("oaf:entity", {})
        project = entity.get("oaf:project", {})
        
        try:
            relations = project.get("rels", {}).get("rel", [])
        except KeyError:
            relations = {}
        except AttributeError:
            relations = {}
        
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
        
        identifiers.append({
            "identifier": header.get("dri:objIdentifier", {}).get("$", ""),
            "scheme": "dri:objIdentifier"
        })
        
        identifiers.append({
            "identifier": project.get("originalId", {}).get("$", ""),
            "scheme": "openaire:originalId"
        })
        
        # Number (code), title (with locale) and acronym
        number = project.get("code", {}).get("$", "")
        title = {
            header.get("locale", {}).get("$", "en")[:2]: project.get("title", {}).get("$", "")
        }
        acronym = project.get("acronym", {}).get("$", "")
        
        
        # Funder and according program
        funding = project.get("fundingtree", [])
        try:
            funder = {
                "id": OpenAIREProvider.dict_get(funding, "funder", "id", "$"),
                "name": OpenAIREProvider.dict_get(funding, "funder", "name", "$"),
            }
        except IndexError:
            funder = {}
        except KeyError:
            funder = {}
        
        program = OpenAIREProvider.get_program_from_funding(funding)
        
        # Subjects and organizations
        subjects = []
        
        subject_list = project.get("subject", [])
        
        if not isinstance(subject_list, list) and subject_list is not None:
            subject_list = [subject_list]
        
        for subject in subject_list:
            subjects.append({
                "id": subject.get("@classid", ""),
                "subject": subject.get("$", "")
            })
                
        organizations = []
        for relation in relations:
            try:
                relation_to = relation.get("to", "")
                organizations.append({
                    "scheme": relation_to.get("@scheme", ""),
                    "id": relation_to.get("$", ""),
                    "organization": relation.get("legalname", {}).get("$", "")
                })
            except AttributeError:
                organizations.append({})
        
        result = {
            "$schema": "local://awards/award-v1.0.0.json",
            "tags": tags,
            "identifiers": identifiers,
            "number": number,
            "title": title,
            "funder": funder,
            "acronym": acronym,
            "program": program,
            "subjects": subjects,
            "organizations": organizations
        }
        
        #print(result)
        return result