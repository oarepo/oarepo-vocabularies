import copy

from oarepo_model_builder.property_preprocessors import PropertyPreprocessor, process
from oarepo_model_builder.stack import ModelBuilderStack, ReplaceElement
from oarepo_model_builder.invenio.invenio_record_schema import InvenioRecordSchemaBuilder
from oarepo_model_builder.invenio.invenio_record import InvenioRecordBuilder


class VocabularyPreprocessor(PropertyPreprocessor):
    TYPE = 'vocabulary'

    @process(model_builder="*",
             path='**/properties/*',
             condition=lambda current, stack: True)
    def modify_oarepo_vocabulary(self, data, stack: ModelBuilderStack, **kwargs):
        if not isinstance(data, dict) or 'oarepo:vocabulary' not in data:
            return
        self._generate_vocabulary_model(data, stack)

    def _generate_vocabulary_model(self, data, stack):
        vocabulary_ext = data['oarepo:vocabulary']
        vocabulary_settings = self.builder.schema.settings.get('oarepo:vocabularies', {})
        type_ = vocabulary_ext.get('type')
        fields_ = vocabulary_ext.get('keys', ['id', 'title'])
        many = vocabulary_ext.get('many', False)
        if not type_:
            raise Exception('Please set type on oarepo:vocabulary element')
        field_path = '.'.join(x.key for x in stack.stack if x.schema_element_type == 'property')
        field_name = vocabulary_ext.get('name', field_path.split('.')[-1])
        field_name = field_name.replace('-', '_')
        # load type_ included model
        schema_name = vocabulary_ext.get('schema') or vocabulary_settings.get('schema', 'hvocabulary-basic')
        included_schema = self.builder.schema.included_schemas[schema_name](self.builder.schema)
        included_props = included_schema['model']['properties']
        # insert properties
        props = {}
        for fld in fields_:
            if fld in included_props:
                props[fld] = copy.deepcopy(included_props[fld])
        # HACK: adding props that would have otherwise be on invenio vocabulary schema
        self._force_generate_field(props, 'title', field='invenio_vocabularies.services.schema.i18n_strings')
        self._force_generate_field(props, 'description', field='invenio_vocabularies.services.schema.i18n_strings')
        self._force_generate_field(props, 'icon')
        data['properties'] = props
        data['type'] = 'object'
        vocabulary_record_class = vocabulary_ext.get('record-class')
        if not vocabulary_record_class:
            vocabulary_record_class = \
                vocabulary_settings.get('record-class') or 'oarepo_vocabularies_basic.records.api.OARepoVocabularyBasic'
        hierarchy_type = 'PIDHierarchyRelation' if not many else 'PIDHierarchyListRelation'
        data['invenio:relation'] = {
            'imports': [
                'oarepo_vocabularies.records.system_fields.pid_hierarchy_relation',
                '.'.join(vocabulary_record_class.split('.')[:-1])
            ],
            'name': field_name,
            'type': f'oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.{hierarchy_type}',
            'params': [
                f'"{field_path}"',
                'keys=[%s]' % (','.join(f'"{k}"' for k in fields_),),
                'pid_field=' + f'{vocabulary_record_class}.pid.with_type_ctx("hierarchy")',
                'cache_key="' + field_name + '-relation' + '"'
            ]
        }
        included_marshmallow = copy.deepcopy(included_schema['model'].get('oarepo:marshmallow'), {})
        # remove base classes as we do not want the schema to inherit from invenio vocabulary schema,
        # because it brings problems when array serialization of ancestors is loaded via load()->clean()
        # keep the VocabularyRelationSchema
        included_marshmallow['base-classes'] = ['oarepo_vocabularies.services.schema.VocabularyRelationSchema']
        marshmallow = data.setdefault(
            'oarepo:marshmallow',
            {
                **included_marshmallow,
                **data.get('oarepo:marshmallow', {})
            }
        )
        marshmallow.setdefault('generate', True)
        record_package, record = self.schema.settings.python.record_class.rsplit('.', 1)
        imported_classes = marshmallow.setdefault('imported-classes', {})
        imported_classes[record_package + '.' + record] = record
        imported_classes['oarepo_vocabularies.services.schema.VocabularyRelationField'] = \
            'VocabularyRelationField'
        schema_class_name = marshmallow.get('class')
        if not schema_class_name:
            for se in reversed(stack.stack):
                if se.schema_element_type == 'property':
                    schema_class_name = se.key.title()
                    break
            else:
                schema_class_name = self.stack.top.key.title()
        else:
            if '.' in schema_class_name:
                schema_package, schema_class_name = schema_class_name.rsplit('.', 1)
                imported_classes[schema_package + '.' + schema_class_name] = schema_class_name

        marshmallow.nested = 'VocabularyRelationField'
        marshmallow.field_args = f'related_field={record}.relations.{field_name}, many={many}'

    def _force_generate_field(self, props, field_name, field=None):
        om = props.get(field_name, {}).get('oarepo:marshmallow', None)
        if om:
            om['generate'] = True
            if field:
                field_end = field.split('.')[-1]
                om['field'] = field_end
                if '.' in field:
                    om.setdefault('imported-classes', {})[field] = field_end

    @process(model_builder=[InvenioRecordSchemaBuilder.TYPE, InvenioRecordBuilder.TYPE],
             path='**/properties/*',
             condition=lambda current, stack: stack.top.schema_element_type == 'property'
                                              and isinstance(stack.top.data, dict)
                                              and isinstance(stack.top.data.get('items'), dict)
                                              and stack.top.data['items'].get('oarepo:vocabulary'),
             priority=10)
    def modify_oarepo_vocabulary_array(self, data, stack: ModelBuilderStack, **kwargs):
        data = copy.deepcopy(data['items'])
        data.setdefault('oarepo:vocabulary')['many'] = True
        raise ReplaceElement(data={stack.top.key: data})
