from flask import current_app, g, render_template
from flask_babelex import lazy_gettext as _

from invenio_i18n.ext import current_i18n
from flask_resources import from_conf, request_parser, resource_requestctx, route
from invenio_records_resources.resources.records.resource import (
    request_read_args,
    request_view_args,
)
from oarepo_ui.resources.resource import RecordsUIResource
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_vocabularies.ui.utils import load_custom_fields
from oarepo_vocabularies.ui.utils import dump_empty

request_vocabulary_args = request_parser(
    from_conf("request_vocabulary_type_args"), location="view_args"
)


class InvenioVocabulariesUIResource(RecordsUIResource):
    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        parent_routes = super().create_url_rules()
        return [
            route("GET", routes["create"], self.create),
            route("GET", routes["edit"], self.edit),
        ] + parent_routes

    def new_record(self):
        """Create an empty record with default values."""
        record = dump_empty(self._api_service.config.schema)
        record["files"] = {"enabled": False}
        record["pids"] = {}
        return record

    def get_vocabulary_props_config(self, vocabulary_type):
        #  TODO: Remove mocked defaults after https://github.com/oarepo/oarepo-vocabularies/pull/44
        #        gets resolved.
        return current_app.config.get(
            "INVENIO_VOCABULARY_TYPE_METADATA",
            {
                "languages": {
                    "alpha3CodeENG": {
                        "description": _("ISO 639-2 standard 3-letter language code"),
                        "icon": None,
                        "label": _("Alpha3 code (English)"),
                        "multiple": False,
                        "options": [
                            # {
                            #     "id": "concept",
                            #     "title": "Concept"
                            # },
                            # ...
                        ],
                        "placeholder": "eng, cze...",
                        "search": False,
                    },
                    "alpha3CodeNative": {
                        "description": _("ISO 639-2 standard 3-letter language code"),
                        "icon": None,
                        "label": _("Alpha3 code (native)"),
                        "multiple": False,
                        "options": [],
                        "placeholder": "eng, ces...",
                        "search": False,
                    },
                },
                "licenses": {},
                "contributor-types": {
                    "marcCode": {
                        "label": _("MARC code"),
                    },
                    "dataCiteCode": {"label": _("DataCite code")},
                },
                "countries": {
                    "alpha3Code": {
                        "label": _("Alpha3 code (English)"),
                        "placeholder": "USA, CZE...",
                    }
                },
                "funders": {"acronym": {"label": _("Acronym")}},
                "institutions": {
                    "acronym": {"label": _("Acronym")},
                    "contexts": {"label": _("Contexts")},
                    "RID": {
                        "label": _("RID"),
                        "description": _(
                            "A Registered Application Provider Identifier"
                        ),
                    },
                    "ICO": {"label": _("ICO")},
                    "nameType": {"label": _("Name type"), "default": "organizational"},
                },
                "item-relation-types": {"pair": {"label": _("Relation")}},
                "resource-types": {
                    "coarType": {"label": _("COAR type")},
                    "dataCiteCode": {"label": _("DataCite code")},
                },
                "subject-categories": {},
            },
        ).get(vocabulary_type, {})

    def get_form_config(self, vocabulary_type, **kwargs):
        """Get the react form configuration."""
        conf = current_app.config
        custom_fields = load_custom_fields()

        return dict(
            current_locale=str(current_i18n.locale),
            default_locale=conf.get("BABEL_DEFAULT_LOCALE", "en"),
            links=dict(),
            custom_fields=custom_fields,
            vocabulary_props=self.get_vocabulary_props_config(vocabulary_type),
            **kwargs,
        )

    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def detail(self):
        return super().detail()

    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def export(self):
        return super().export()

    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def search(self):
        return super().search()

    # TODO: !IMPORTANT!: needs to be enabled before production deployment
    # @login_required
    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def create(self):
        vocabulary_type = resource_requestctx.view_args["vocabulary_type"]
        empty_record = self.new_record()
        layout = current_oarepo_ui.get_layout(self.get_layout_name())
        self.run_components(
            "before_vocabulary_create",
            layout=layout,
            resource=self,
            record=empty_record,
            identity=g.identity,
        )
        template_def = self.get_template_def("edit")
        template = current_oarepo_ui.get_template(template_def["layout"], {})

        return render_template(
            template,
            record=empty_record,
            data=empty_record,
            ui=empty_record.get("ui", empty_record),
            ui_config=self.config,
            ui_resource=self,
            forms_config=self.get_form_config(
                vocabulary_type,
                # TODO: define create link in vocabulary service config links
                createUrl=f"/api{self._api_service.config.url_prefix}{vocabulary_type}"
            ),
            layout=layout,
            component_key="edit",
        )

    # TODO: !IMPORTANT!: needs to be enabled before production deployment
    # @login_required
    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def edit(self):
        record = self._get_record(resource_requestctx)
        serialized_record = self.config.ui_serializer.dump_obj(record.to_dict())
        layout = current_oarepo_ui.get_layout(self.get_layout_name())
        self.run_components(
            "before_vocabulary_edit",
            layout=layout,
            resource=self,
            record=serialized_record,
            identity=g.identity,
        )
        template_def = self.get_template_def("edit")
        template = current_oarepo_ui.get_template(template_def["layout"], {})

        return render_template(
            template,
            record=serialized_record,
            data=serialized_record,
            ui=serialized_record.get("ui", serialized_record),
            ui_config=self.config,
            ui_resource=self,
            forms_config=self.get_form_config(
                resource_requestctx.view_args["vocabulary_type"],
                updateUrl=record.links.get("self", None),
            ),
            layout=layout,
            component_key="edit",
        )

    def _get_record(self, resource_requestctx):
        return self._api_service.read(
            g.identity,
            (
                resource_requestctx.view_args["vocabulary_type"],
                resource_requestctx.view_args["pid_value"],
            ),
        )
