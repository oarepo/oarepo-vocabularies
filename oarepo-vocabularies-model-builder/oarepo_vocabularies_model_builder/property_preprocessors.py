import copy

from oarepo_model_builder.property_preprocessors import PropertyPreprocessor, process
from oarepo_model_builder.stack import ModelBuilderStack


class VocabularyPreprocessor(PropertyPreprocessor):
    TYPE = 'vocabulary'

    @process(model_builder="*",
             path='**/properties/*',
             condition=lambda current, stack: True)
    def modify_oarepo_vocabulary(self, data, stack: ModelBuilderStack, **kwargs):
        if not isinstance(data, dict) or 'oarepo:vocabulary' not in data:
            return
        vocabulary_ext = data['oarepo:vocabulary']
        vocabulary_settings = self.builder.schema.settings.get('oarepo:vocabularies', {})

        type_ = vocabulary_ext.get('type')
        fields_ = vocabulary_ext.get('keys', ['id', 'title'])
        if not type_:
            raise Exception('Please set type on oarepo:vocabulary element')

        field_path = '.'.join(x.key for x in stack.stack if x.schema_element_type == 'property')
        field_name = vocabulary_ext.get('name', field_path.split('/')[-1])

        # load type_ included model
        schema_name = vocabulary_ext.get('schema') or vocabulary_settings.get('schema', 'hvocabulary-basic')
        included_schema = self.builder.schema.included_schemas[schema_name](self.builder.schema)

        included_props = included_schema['model']['properties']

        # insert properties
        props = {}
        for fld in fields_:
            if fld == 'id' and fld not in included_props:
                props[fld] = {
                    'type': 'keyword'
                }
            else:
                props[fld] = copy.deepcopy(included_props[fld])

        data['properties'] = props

        vocabulary_record_class = vocabulary_ext.get('record-class')
        if not vocabulary_record_class:
            vocabulary_record_class = \
                vocabulary_settings.get('record-class') or 'oarepo_vocabularies_basic.records.api.OARepoVocabularyBasic'

        data['invenio:relation'] = {
            'imports': [
                'oarepo_vocabularies.records.system_fields.pid_hierarchy_relation',
                '.'.join(vocabulary_record_class.split('.')[:-1])
            ],
            'name': field_name,
            'type': 'oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyRelation',
            'params': [
                f'"{field_path}"',
                'keys=[%s]' % (','.join(f'"{k}"' for k in fields_),),
                'pid_field=' + f'{vocabulary_record_class}.pid.with_type_ctx("hierarchy")',
                'cache_key="' + field_name + '-relation' + '"'
            ]
        }
        marshmallow = data.setdefault('oarepo:marshmallow', {})
        marshmallow.setdefault('generate', True)
