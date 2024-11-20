import logging

from flask import current_app
import os
import idutils
from oarepo_vocabularies.authorities.providers import AuthorityProvider

from orcid import PublicAPI as PublicAPI




logger = logging.getLogger("oarepo-vocabularies.providers.orcid")

class ORCIDClient(PublicAPI):
    """Inherits from PublicAPI directly.
    
    Implements get_record and quick_search methods.
    """

    def __init__(self, institution_key, institution_secret, testing=False, timeout=None):
        self.timeout = timeout or 10000
        super(ORCIDClient, self).__init__(institution_key, institution_secret, testing, timeout)

    def get_record(self, access_token, orcid_id):
        """
        HEADER: Accept: application/orcid+json
        HEADER: Authorization: Bearer
        METHOD: GET
        URL: https://pub.orcid.org/v3.0/[ORCID iD]/record
        """

        return self.read_record_public(orcid_id, 'record', access_token)

        
class ORCIDProvider(AuthorityProvider):
    IGNORED_AFFILIATIONS = ["path", "last-modified-date", "fundings", "peer-reviews", "works"]
    
    def __init__(self, url=None, testing=False, **kwargs):
        try:
            client_id = current_app.config["ORCID_CLIENT_ID"]
            client_secret = current_app.config["ORCID_CLIENT_SECRET"]
        except RuntimeError:
            client_id = os.environ["INVENIO_ORCID_CLIENT_ID"]
            client_secret = os.environ["INVENIO_ORCID_CLIENT_SECRET"]
        except KeyError:
            raise KeyError("ORCID_CLIENT_ID and ORCID_CLIENT_SECRET must be set in the configuration or as environment variables.")
        self.orcid_client = ORCIDClient(client_id, client_secret, testing, **kwargs)
        

    def search(self, identity, params, **kwargs):
        params = params or {}
        access_token = self.orcid_client.get_search_token_from_orcid()

        page = params.get("page", 1)
        page_size = params.get("page_size", 20)
        start = (page - 1) * page_size

        results = self.orcid_client.search(params.get("q", ""), method="edismax", start=start, rows=page_size, access_token=access_token)

        total = results.get("num-found")

        orcids = [result['orcid-identifier']['path'] for result in results.get("result")]

        records = [self.orcid_client.get_record(access_token, orcid) for orcid in orcids]

        items = [self.to_vocabulary_item(record) for record in records]

        return items, total

    

    def get(self, identity, item_id, **kwargs):
        if not idutils.is_orcid(item_id):
            raise AssertionError(f"{item_id} is not a valid ORCID identifier.")
        
        access_token = self.orcid_client.get_search_token_from_orcid()
        
        orcid_id = idutils.normalize_orcid(item_id)

        record = self.orcid_client.get_record(access_token, orcid_id)
        
        if record is None:
            raise KeyError(f"ORCID record {item_id} not found.")
        
        return self.to_vocabulary_item(record)
    
    @staticmethod
    def get_affiliations(activities_summary):
        affiliations = []
        
        for key, activity in activities_summary.items():
            if key in ORCIDProvider.IGNORED_AFFILIATIONS:
                continue
            
            if key == "educations":
                summary_type = "education-summary"
                
            if key == "employments":
                summary_type = "employment-summary"
                
            for affiliation in activity.get(summary_type, []):
                organization = affiliation.get("organization", {})
                organization_name = organization.get("name", "")
                try:
                    organization_id = organization.get("disambiguated-organization", {}).get("disambiguated-organization-identifier", "")
                    id_source = organization.get("disambiguated-organization", {}).get("disambiguation-source", "")
                    new_affiliation = {"name": organization_name, "id": f"{id_source}:{organization_id}"}
                except AttributeError:
                    new_affiliation = {"name": organization_name, "id": "N/A"}
                
                if new_affiliation not in affiliations:
                    affiliations.append(new_affiliation)
        
        return affiliations
    
    @staticmethod
    def to_vocabulary_item(orcid_item):
        orcid_id = idutils.normalize_orcid(orcid_item.get("orcid-identifier", {}).get("path", ""))

        # Personal information
        person = orcid_item.get("person", {})

        if person.get("name", {}).get("family-name") is None or person.get("name", {}).get("given-names") is None:
            return None
        
        given_name = person.get("name", {}).get("given-names", {}).get("value", "")
        family_name = person.get("name", {}).get("family-name", {}).get("value", "")
        name = f"{given_name} {family_name}"

        # Keywords (tags)
        tags = []

        keywords = person.get("keywords", {}).get("keyword", [])
        for keyword in keywords:
            tags.append(keyword.get("content", ""))
            
        # Affiliations
        activities_summary = orcid_item.get("activities-summary", {})

        affiliations = ORCIDProvider.get_affiliations(activities_summary)

        return {
            "$schema": "local://name-v1.0.0.json",
            "tags": tags,
            "scheme": "ORCID",
            "name": name,
            "given_name": given_name,
            "family_name": family_name,
            "identifiers": [{"identifier": orcid_id, "scheme": "ORCID"}],
            "affiliations": affiliations
        }
    