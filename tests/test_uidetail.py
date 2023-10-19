import re

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service


def remove_ws(x):
    return re.sub(r"\s+", "", x)


def test_uidetail(
    client, app, db, cache, lang_type, lang_data, vocab_cf, fake_manifest
):
    lang_object = vocab_service.create(system_identity, lang_data)
    detail_page = client.get("/vocabularies/languages/eng")
    assert detail_page.status_code == 200
    print(detail_page.text)
    assert (
        remove_ws(
            """  
        <dt>vocabulary.akey</dt>
        <dd>avalue</dd>"""
        )
        in remove_ws(detail_page.text)
    )
    print(detail_page.text)
