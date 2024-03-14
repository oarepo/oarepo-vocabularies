from pathlib import Path

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service
from oarepo_runtime.datastreams.fixtures import FixturesCallback, load_fixtures

from oarepo_vocabularies.records.api import Vocabulary
from tests.test_uidetail import remove_ws


def test_uiedit(
    client_with_credentials,
    app,
    db,
    cache,
    lang_type,
    lang_data,
    vocab_cf,
    fake_manifest,
    search_clear,
):
    for _id in range(100):
        vocab_service.create(
            system_identity,
            {
                **lang_data,
                "id": str(_id),
            },
        )
    Vocabulary.index.refresh()
    edit_page = client_with_credentials.get("/vocabularies/languages/1/edit")
    assert edit_page.status_code == 200
    print(edit_page.text)
    assert (
        remove_ws(
            """  
        {"all": [{"element_type": "leaf", "hierarchy": {"ancestors": [], "title": ["English"]}, "props": {"akey": "avalue"}, "text": "English", "value": \""""
        )
        in remove_ws(edit_page.text)
    )


def test_uiedit_locale(
    client_with_credentials,
    app,
    db,
    cache,
    vocab_cf,
    fake_manifest,
    reset_babel,
    search_clear,
):
    load_fixtures(Path(__file__).parent / "icudata", callback=FixturesCallback())
    Vocabulary.index.refresh()

    reset_babel()
    edit_page = client_with_credentials.get(
        "/vocabularies/languages/en/edit", headers=[("Accept-Language", "cs")]
    )
    print(edit_page.text)
    assert (
        remove_ws(
            """  
"languages": {"all": [
{"element_type": "leaf", "hierarchy": {"ancestors": [], "title": ["Angli\\u010dtina"]}, "text": "Angli\\u010dtina", "value": "en"}, 
{"element_type": "leaf", "hierarchy": {"ancestors": [], "title": ["\\u010ce\\u0161tina"]}, "text": "\\u010ce\\u0161tina", "value": "cs"}
        """
        )
        in remove_ws(edit_page.text)
    )

    reset_babel()
    edit_page = client_with_credentials.get(
        "/vocabularies/languages/en/edit", headers=[("Accept-Language", "en")]
    )
    assert (
        remove_ws(
            """  
"languages": {"all": [
{"element_type": "leaf", "hierarchy": {"ancestors": [], "title": ["Czech"]}, "text": "Czech", "value": "cs"}, 
{"element_type": "leaf", "hierarchy": {"ancestors": [], "title": ["English"]}, "text": "English", "value": "en"}            
"""
        )
        in remove_ws(edit_page.text)
    )
