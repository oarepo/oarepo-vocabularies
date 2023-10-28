import re

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service

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
        {"all": [{"hierarchy": {"ancestors_or_self": {"title": ["English"]}}, "text": "English", "value": \""""
        )
        in remove_ws(edit_page.text)
    )
