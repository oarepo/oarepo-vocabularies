#! /bin/bash

cd $(dirname "$0")

export version=$(cat oarepo_vocabularies/__init__.py | grep '__version__' | sed "s/^.*= *//" | tr -d "'")

export module_name="oarepo_vocabularies"
export extra_options=""
export suffix="-basic"
export description="Basic schema for vocabularies."
IFS= read -r -d '' install_requires <<EOM
    oarepo_vocabularies>=${version}
EOM

IFS= read -r -d '' packages <<EOM
    oarepo_vocabularies_basic
EOM

IFS= read -r -d '' entry_points <<EOM
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
oarepo.models =
    hvocabulary-basic = oarepo_vocabularies.models.registration:hvocabulary_basic_model
EOM

export install_requires
export entry_points
export packages

envsubst <setup-proto.cfg >setup-basic.cfg

IFS= read -r -d '' entry_points <<EOM
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
oarepo.models =
    hvocabulary-basic = oarepo_vocabularies.models.registration:hvocabulary_basic_model
    hvocabulary = oarepo_vocabularies.models.registration:hvocabulary
EOM

IFS= read -r -d '' packages <<EOM
    oarepo_vocabularies
    oarepo_vocabularies.basic
    oarepo_vocabularies.basic.records
    oarepo_vocabularies.basic.resources
    oarepo_vocabularies.basic.services
    oarepo_vocabularies.datastreams
    oarepo_vocabularies.models
    oarepo_vocabularies.records
    oarepo_vocabularies.resources
    oarepo_vocabularies.services
EOM

IFS= read -r -d '' extra_options <<EOM
[options.package_data]
oarepo_vocabularies.models =
    *.yaml
EOM

IFS= read -r -d '' install_requires <<EOM
    invenio-vocabularies>=0.11.6
    openpyxl>=3.0.0<4.0.0
EOM


export install_requires
export packages
export extra_options
envsubst <setup-proto.cfg >setup-basic-local.cfg

export suffix=""
export description=""
export extra_options=""

IFS= read -r -d '' install_requires <<EOM
    invenio-vocabularies>=0.11.6
    openpyxl>=3.0.0<4.0.0
EOM

IFS= read -r -d '' package_exclude <<EOM
    tests
    tests.*
EOM

IFS= read -r -d '' entry_points <<EOM
invenio_base.apps =
    oarepo_vocabularies = oarepo_vocabularies.ext:OARepoVocabulariesExt
invenio_base.api_apps =
    oarepo_vocabularies = oarepo_vocabularies.ext:OARepoVocabulariesExt
oarepo.models =
    hvocabulary = oarepo_vocabularies.models.registration:hvocabulary
EOM

export install_requires
export entry_points
export package_exclude

envsubst <setup-proto.cfg >setup-library.cfg

export suffix="-model-builder"
export description="Model builder extension."
IFS= read -r -d '' install_requires <<EOM
EOM


IFS= read -r -d '' packages <<EOM
    oarepo_vocabularies_model_builder
    oarepo_vocabularies_model_builder.models
EOM

IFS= read -r -d '' extra_options <<EOM

[options.package_data]
oarepo_vocabularies_model_builder.models =
    *.yaml
EOM


IFS= read -r -d '' entry_points <<EOM
oarepo.models =
    hvocabulary = oarepo_vocabularies_model_builder.models.registration:hvocabulary
    hvocabulary-basic = oarepo_vocabularies_model_builder.models.registration:hvocabulary_basic_model
EOM

export install_requires
export entry_points
export package_exclude
export extra_options
export module_name="oarepo_vocabularies_model_builder"

envsubst <setup-proto.cfg >setup-model-builder.cfg
