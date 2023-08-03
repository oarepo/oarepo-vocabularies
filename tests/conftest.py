# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""
import shutil
import sys
from pathlib import Path

from oarepo_vocabularies.ui.resources.config import InvenioVocabulariesUIResourceConfig
from oarepo_vocabularies.ui.resources.resource import InvenioVocabulariesUIResource
from oarepo_vocabularies.ui.resources.components import VocabulariesFormConfigComponent

# Monkey patch Werkzeug 2.1, needed to import flask_security.login_user
# Flask-Login uses the safe_str_cmp method which has been removed in Werkzeug
# 2.1. Flask-Login v0.6.0 (yet to be released at the time of writing) fixes the
# issue. Once we depend on Flask-Login v0.6.0 as the minimal version in
# Flask-Security-Invenio/Invenio-Accounts we can remove this patch again.
try:
    # Werkzeug <2.1
    from werkzeug import security

    security.safe_str_cmp
except AttributeError:
    # Werkzeug >=2.1
    import hmac

    from werkzeug import security

    security.safe_str_cmp = hmac.compare_digest


from collections import namedtuple

import pytest
from flask_principal import Identity, Need, UserNeed
from flask_security import login_user
from flask_security.utils import hash_password
from invenio_access.permissions import ActionUsers, any_user, system_process
from invenio_access.proxies import current_access
from invenio_accounts.proxies import current_datastore
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_app as _create_app
from invenio_cache import current_cache
from invenio_pidstore.models import PersistentIdentifier
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType

pytest_plugins = ("celery.contrib.pytest",)


@pytest.fixture(scope="module")
def h():
    """Accept JSON headers."""
    return {"accept": "application/json"}


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {}


@pytest.fixture(scope="module")
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["JSONSCHEMAS_HOST"] = "localhost"
    app_config["BABEL_DEFAULT_LOCALE"] = "en"
    app_config["I18N_LANGUAGES"] = [("da", "Danish")]
    app_config[
        "RECORDS_REFRESOLVER_CLS"
    ] = "invenio_records.resolver.InvenioRefResolver"
    app_config[
        "RECORDS_REFRESOLVER_STORE"
    ] = "invenio_jsonschemas.proxies.current_refresolver_store"

    # note: This line must always be added to the invenio.cfg file
    from oarepo_vocabularies.authorities.resources import (
        AuthoritativeVocabulariesResource,
        AuthoritativeVocabulariesResourceConfig,
    )
    from oarepo_vocabularies.resources.config import VocabulariesResourceConfig
    from oarepo_vocabularies.resources.vocabulary_type import (
        VocabularyTypeResource,
        VocabularyTypeResourceConfig,
    )
    from oarepo_vocabularies.services.config import (
        VocabulariesConfig,
        VocabularyTypeServiceConfig,
    )
    from oarepo_vocabularies.services.service import VocabularyTypeService

    app_config["VOCABULARIES_SERVICE_CONFIG"] = VocabulariesConfig
    app_config["VOCABULARIES_RESOURCE_CONFIG"] = VocabulariesResourceConfig

    app_config["OAREPO_VOCABULARIES_TYPE_SERVICE"] = VocabularyTypeService
    app_config["OAREPO_VOCABULARIES_TYPE_SERVICE_CONFIG"] = VocabularyTypeServiceConfig

    app_config["OAREPO_VOCABULARY_TYPE_RESOURCE"] = VocabularyTypeResource
    app_config["OAREPO_VOCABULARY_TYPE_RESOURCE_CONFIG"] = VocabularyTypeResourceConfig

    app_config["OAREPO_VOCABULARIES_AUTHORITIES"] = AuthoritativeVocabulariesResource
    app_config[
        "OAREPO_VOCABULARIES_AUTHORITIES_CONFIG"
    ] = AuthoritativeVocabulariesResourceConfig

    from invenio_records_resources.services.custom_fields.text import KeywordCF

    from tests.customfields import HintCF, NonPreferredLabelsCF, RelatedURICF

    app_config["OAREPO_VOCABULARIES_CUSTOM_CF"] = [
        KeywordCF("blah"),
        RelatedURICF("relatedURI"),
        HintCF("hint"),
        NonPreferredLabelsCF("nonpreferredLabels"),
    ]

    # disable redis cache
    app_config["CACHE_TYPE"] = "SimpleCache"  # Flask-Caching related configs
    app_config["CACHE_DEFAULT_TIMEOUT"] = 300

    app_config["INVENIO_VOCABULARY_TYPE_METADATA"] = {
        "languages": {
            "name": {
                "cs": "jazyky",
                "en": "languages",
            },
            "description": {
                "cs": "slovnikovy typ ceskeho jazyka.",
                "en": "czech language vocabulary type.",
            },
        },
        "licenses": {
            "name": {
                "cs": "license",
                "en": "licenses",
            },
            "description": {
                "cs": "slovnikovy typ licencii.",
                "en": "lincenses vocabulary type.",
            },
        },
    }

    app_config["OAREPO_UI_COMMON_LANGUAGES"] = ["es"]
    app_config["VOCABULARIES_LANGUAGES_DISABLED"] = False
    
    app_config["APP_THEME"] = ["semantic-ui"]
    app_config[
        "THEME_HEADER_TEMPLATE"
    ] = "oarepo_vocabularies_ui/test_header_template.html"
    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_app


@pytest.fixture(scope="module")
def identity_simple():
    """Simple identity fixture."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(Need(method="system_role", value="any_user"))
    return i


@pytest.fixture(scope="module")
def identity():
    """Simple identity to interact with the service."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(any_user)
    i.provides.add(system_process)
    return i


@pytest.fixture(scope="module")
def service(app):
    """Vocabularies service object."""
    return app.extensions["invenio-vocabularies"].service


@pytest.fixture()
def lang_type(db):
    """Get a language vocabulary type."""
    v = VocabularyType.create(id="languages", pid_type="lng")
    db.session.commit()
    return v


@pytest.fixture(scope="function")
def lang_data():
    """Example data."""
    return {
        "id": "eng",
        "title": {"en": "English", "da": "Engelsk"},
        "description": {"en": "English description", "da": "Engelsk beskrivelse"},
        "icon": "file-o",
        "props": {
            "akey": "avalue",
        },
        "tags": ["recommended"],
        "type": "languages",
    }


@pytest.fixture(scope="function")
def lang_data_child():
    """Example data."""
    return {
        "id": "eng.US",
        "title": {"en": "English (US)", "da": "Engelsk (US)"},
        "icon": "file-o",
        "type": "languages",
        "hierarchy": {"parent": "eng"},
    }


@pytest.fixture()
def lang_data2(lang_data):
    """Example data for testing invalid cases."""
    data = dict(lang_data)
    data["id"] = "new"
    return data


@pytest.fixture()
def example_record(db, identity, service, example_data):
    """Example record."""
    vocabulary_type_languages = VocabularyType(name="languages")
    vocabulary_type_licenses = VocabularyType(name="licenses")
    db.session.add(vocabulary_type_languages)
    db.session.add(vocabulary_type_licenses)
    db.session.commit()

    record = service.create(
        identity=identity,
        data=dict(**example_data, vocabulary_type_id=vocabulary_type_languages.id),
    )

    Vocabulary.index.refresh()  # Refresh the index
    return record


@pytest.fixture(scope="function")
def lang_data_many(lang_type, lang_data, service, identity):
    """Create many language vocabulary."""
    lang_ids = ["fr", "tr", "gr", "ger", "es"]
    data = dict(lang_data)

    for lang_id in lang_ids:
        data["id"] = lang_id
        service.create(identity, data)
    Vocabulary.index.refresh()  # Refresh the index
    return lang_ids


@pytest.fixture()
def user(app, db):
    """Create example user."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        _user = datastore.create_user(
            email="info@inveniosoftware.org",
            password=hash_password("password"),
            active=True,
        )
    db.session.commit()
    return _user


@pytest.fixture()
def role(app, db):
    """Create some roles."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        role = datastore.create_role(name="admin", description="admin role")

    db.session.commit()
    return role


@pytest.fixture()
def client_with_credentials(db, client, user, role):
    """Log in a user to the client."""
    current_datastore.add_role_to_user(user, role)
    action = current_access.actions["superuser-access"]
    db.session.add(ActionUsers.allow(action, user_id=user.id))

    login_user(user, remember=True)
    login_user_via_session(client, email=user.email)

    return client


# FIXME: https://github.com/inveniosoftware/pytest-invenio/issues/30
# Without this, success of test depends on the tests order
@pytest.fixture()
def cache():
    """Empty cache."""
    try:
        yield current_cache
    finally:
        current_cache.clear()


@pytest.fixture()
def vocab_cf(app, db, cache):
    from oarepo_runtime.cf.mappings import prepare_cf_indices

    prepare_cf_indices()


@pytest.fixture
def sample_records(app, db, cache, lang_type, lang_data, lang_data_child, vocab_cf):
    from invenio_access.permissions import system_identity
    from invenio_vocabularies.proxies import current_service as vocab_service

    parent = vocab_service.create(system_identity, lang_data)
    child_1 = vocab_service.create(
        system_identity,
        {
            "id": "eng.US",
            "title": {"en": "English (US)", "da": "Engelsk (US)"},
            "icon": "file-o",
            "type": "languages",
            "hierarchy": {"parent": "eng"},
        },
    )
    child_2 = vocab_service.create(
        system_identity,
        {
            "id": "eng.UK",
            "title": {"en": "English (UK)", "da": "Engelsk (UK)"},
            "icon": "file-o",
            "type": "languages",
            "hierarchy": {"parent": "eng"},
        },
    )
    grand_child_2_1 = vocab_service.create(
        system_identity,
        {
            "id": "eng.UK.S",
            "title": {"en": "English (UK, Scotland)", "da": "Engelsk (UK, Scotland)"},
            "icon": "file-o",
            "type": "languages",
            "hierarchy": {"parent": "eng.UK"},
        },
    )
    Vocabulary.index.refresh()
    TN = namedtuple("TN", "node,children")
    return [
        TN(
            parent.data,
            children=[
                TN(child_1.data, children=[]),
                TN(child_2.data, children=[TN(grand_child_2_1.data, children=[])]),
            ],
        )
    ]


@pytest.fixture()
def empty_licences(db):
    v = VocabularyType.create(id="licences", pid_type="lic")
    db.session.add(v)
    db.session.commit()

    return v


@pytest.fixture()
def affiliations_pids(db):
    def _upload(uuid):
        # One of the samples already exists and the other one is a completely new one.
        invenio_pid = PersistentIdentifier.create(
            pid_type="id",
            pid_value="invenioid1",
            object_type="object",
            object_uuid=uuid,
        )

        authvc_pid = PersistentIdentifier.create(
            pid_type="authvc",
            pid_value="authid1",
            object_type="object",
            object_uuid=uuid,
        )

        db.session.add(invenio_pid)
        db.session.add(authvc_pid)
        db.session.commit()

    return _upload


@pytest.fixture()
def mock_auth_getter_affilliations(mocker):
    """
    ROR-like samples.
    """
    mock = mocker.patch(
        "oarepo_vocabularies.authorities.ext.OARepoVocabulariesAuthorities.auth_getter"
    )

    mock.return_value = lambda q, page, size: [
        {
            "id": "https://ror.org/03zsq2967",
            "props": {
                "authoritative_id": "authid1",
                "name": "Association of Asian Pacific Community Health Organizations",
            },
        },
        {
            "id": "https://ror.org/020bcb226",
            "props": {
                "authoritative_id": "authid2",
                "name": "Oakton Community College",
            },
        },
    ]

    yield mock


@pytest.fixture()
def fake_manifest(app):
    python_path = Path(sys.executable)
    invenio_instance_path = python_path.parent.parent / "var" / "instance"
    manifest_path = invenio_instance_path / "static" / "dist"
    manifest_path.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        Path(__file__).parent / "manifest.json", manifest_path / "manifest.json"
    )



@pytest.fixture
def vocabularies_ui_resource_config(app):
    class Cfg(InvenioVocabulariesUIResourceConfig):
        api_service = "vocabularies"  # must be something included in oarepo, as oarepo is used in tests
        components = [VocabulariesFormConfigComponent]

    return Cfg()


@pytest.fixture
def vocabularies_ui_resource(app, vocabularies_ui_resource_config):
    return InvenioVocabulariesUIResource(vocabularies_ui_resource_config)
