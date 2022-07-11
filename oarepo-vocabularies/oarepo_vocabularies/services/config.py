from copy import deepcopy

from invenio_records_resources.services import Link, pagination_links
from invenio_records_resources.services.base.links import preprocess_vars
from invenio_vocabularies.services import VocabulariesServiceConfig
from uritemplate import URITemplate


class PathLink(Link):
    # can not use normal invenio Link as it escapes '/' in id
    def __init__(self, uritemplate, query=None, querytemplate=None, when=None, vars=None):
        super().__init__(uritemplate, when=when, vars=vars)
        self.query = query
        self._querytemplate = URITemplate(querytemplate) if querytemplate else None

    def path_vars(self, obj, context):
        # extracted vars handling from Link.expand
        vars = {}
        vars.update(deepcopy(context))
        self.vars(obj, vars)
        if self._vars_func:
            self._vars_func(obj, vars)
        return preprocess_vars(vars)

    def expand(self, obj, context):
        vars = self.path_vars(obj, context)

        ret = self._uritemplate.expand(**vars)

        if not ret.endswith('/'):
            ret += '/'
        ret += vars['id']

        if self.query:
            ret += '?' + self.query
        if self._querytemplate:
            ret += self._querytemplate.expand(**vars)
        return ret


def hierarchy_links(tpl, query):
    """Create pagination links for hierarchy requests (prev/self/next) from the same template."""
    return {
        "prev": PathLink(
            tpl, querytemplate=query,
            when=lambda pagination, ctx: pagination.has_prev,
            vars=lambda pagination, vars: vars["args"].update(
                {"page": pagination.prev_page.page}
            ),
        ),
        "self": PathLink(tpl, querytemplate=query),
        "next": PathLink(
            tpl, querytemplate=query,
            when=lambda pagination, ctx: pagination.has_next,
            vars=lambda pagination, vars: vars["args"].update(
                {"page": pagination.next_page.page}
            ),
        ),
    }


class OARepoVocabulariesServiceConfigBase(VocabulariesServiceConfig):
    links_item = {
        "self": PathLink(
            "{+api}/v/{type}",
            vars=lambda record, vars: vars.update(
                {
                    "id": record.pid.pid_value,
                    "type": record.type.id,
                }
            ),
        ),
        "parent": PathLink(
            "{+api}/v/{type}",
            vars=lambda record, vars: vars.update(
                {
                    "id": '/'.join(record.pid.pid_value.split('/')[:-1]),
                    "type": record.type.id,
                }
            ),
            when=lambda record, vars: '/' in record.pid.pid_value
        ),
        "children": PathLink(
            "{+api}/v/{type}", query="hierarchy=children",
            vars=lambda record, vars: vars.update(
                {
                    "id": record.pid.pid_value,
                    "type": record.type.id,
                }
            )
        ),
        "self+children": PathLink(
            "{+api}/v/{type}", query="hierarchy=self+children",
            vars=lambda record, vars: vars.update(
                {
                    "id": record.pid.pid_value,
                    "type": record.type.id,
                }
            )
        ),
        "descendants": PathLink(
            "{+api}/v/{type}", query="hierarchy=descendants",
            vars=lambda record, vars: vars.update(
                {
                    "id": record.pid.pid_value,
                    "type": record.type.id,
                }
            )
        ),
        "self+descendants": PathLink(
            "{+api}/v/{type}", query="hierarchy=self+descendants",
            vars=lambda record, vars: vars.update(
                {
                    "id": record.pid.pid_value,
                    "type": record.type.id,
                }
            )
        ),
        "ancestors": PathLink(
            "{+api}/v/{type}/", query="hierarchy=ancestors",
            vars=lambda record, vars: vars.update(
                {
                    "id": record.pid.pid_value,
                    "type": record.type.id,
                }
            ),
            when=lambda record, vars: '/' in record.pid.pid_value
        ),
        "self+ancestors": PathLink(
            "{+api}/v/{type}/", query="hierarchy=self+ancestors",
            vars=lambda record, vars: vars.update(
                {
                    "id": record.pid.pid_value,
                    "type": record.type.id,
                }
            ),
            when=lambda record, vars: '/' in record.pid.pid_value
        )
    }

    links_search = pagination_links("{+api}/v/{type}{?args*}")
    links_hierarchy = hierarchy_links("{+api}/v/{type}/", "{?args*}")
    components = [
        *VocabulariesServiceConfig.components
    ]
