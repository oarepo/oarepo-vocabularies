#! /bin/bash

cd $(dirname "$0")

export version=$(cat oarepo_vocabularies/__init__.py | grep '__version__' | sed "s/^.*= *//" | tr -d "'")

export suffix="-basic"
export description="Basic schema for vocabularies."
IFS= read -r -d '' install_requires << EOM
    oarepo_vocabularies>=${version}
EOM

IFS= read -r -d '' package_exclude << EOM
    oarepo_vocabularies.models*
    oarepo_vocabularies.records*
    oarepo_vocabularies.resources*
    oarepo_vocabularies.services*
    tests
    tests.*
EOM

IFS= read -r -d '' entry_points << EOM
;flask.commands =
;    vocabularies = invenio_vocabularies.cli:vocabularies
invenio_base.apps =
    oarepo_vocabularies_basic =oarepo_vocabularies.basic.ext:OARepoVocabulariesBasicExt
invenio_base.api_apps =
    oarepo_vocabularies_basic =oarepo_vocabularies.basic.ext:OARepoVocabulariesBasicExt
invenio_base.api_blueprints =
    oarepo_vocabularies_basic = oarepo_vocabularies.basic.views:create_basic_blueprint_from_app
invenio_db.alembic =
    oarepo_vocabularies_basic =oarepo_vocabularies.basic:alembic
invenio_db.models =
     oarepo_vocabulary_model = oarepo_vocabularies.basic.records.models
invenio_jsonschemas.schemas =
    oarepo_vocabularies.basic = oarepo_vocabularies.basic.records.jsonschemas
invenio_search.mappings =
    oarepo_vocabularies.basic = oarepo_vocabularies.basic.records.mappings
EOM

export install_requires
export entry_points
export package_exclude

envsubst < setup-proto.cfg >setup-basic.cfg

IFS= read -r -d '' entry_points << EOM
;flask.commands =
;    vocabularies = invenio_vocabularies.cli:vocabularies
invenio_base.apps =
    oarepo_vocabularies_basic =oarepo_vocabularies.basic.ext:OARepoVocabulariesBasicExt
    oarepo_vocabularies = oarepo_vocabularies.ext:OARepoVocabulariesExt
invenio_base.api_apps =
    oarepo_vocabularies_basic =oarepo_vocabularies.basic.ext:OARepoVocabulariesBasicExt
    oarepo_vocabularies = oarepo_vocabularies.ext:OARepoVocabulariesExt
invenio_base.api_blueprints =
    oarepo_vocabularies_basic = oarepo_vocabularies.basic.views:create_basic_blueprint_from_app
invenio_db.alembic =
    oarepo_vocabularies_basic =oarepo_vocabularies.basic:alembic
invenio_db.models =
     oarepo_vocabulary_model = oarepo_vocabularies.basic.records.models
invenio_jsonschemas.schemas =
    oarepo_vocabularies.basic = oarepo_vocabularies.basic.records.jsonschemas
invenio_search.mappings =
    oarepo_vocabularies.basic = oarepo_vocabularies.basic.records.mappings
EOM


export install_requires=""
envsubst < setup-proto.cfg >setup-basic-local.cfg


export suffix=""
export description=""
export install_requires=""
IFS= read -r -d '' package_exclude << EOM
    oarepo_vocabularies.basic*
    tests
    tests.*
EOM

IFS= read -r -d '' entry_points << EOM
invenio_base.apps =
    oarepo_vocabularies = oarepo_vocabularies.ext:OARepoVocabulariesExt
invenio_base.api_apps =
    oarepo_vocabularies = oarepo_vocabularies.ext:OARepoVocabulariesExt
EOM

export install_requires
export entry_points
export package_exclude

envsubst < setup-proto.cfg >setup-library.cfg
