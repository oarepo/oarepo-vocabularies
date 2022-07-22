import typing
import marshmallow as ma
import marshmallow.fields as ma_fields
from invenio_pidstore.errors import PIDDoesNotExistError
from marshmallow.exceptions import FieldInstanceResolutionError, ValidationError
from marshmallow.utils import resolve_field_instance


class VocabularyRelationSchema(ma.Schema):
    version = ma_fields.Str(attribute='@v', load_only=False, dump_only=False)
    id_ = ma_fields.Str(attribute='id')


class VocabularyRelationField(ma_fields.Field):
    def __init__(self, cls_or_instance: typing.Union[ma.Schema, type], *, related_field=None, many=False,
                 **kwargs):
        super().__init__(**kwargs)
        if not related_field:
            raise AttributeError('Related field is required')
        self.many = many
        self.related_field = related_field

        try:
            self.inner = resolve_field_instance(ma_fields.Nested(cls_or_instance))
        except FieldInstanceResolutionError as error:
            raise ValueError(
                "The vocabulary relation elements must be a subclass or instance of "
                "marshmallow.base.FieldABC."
            ) from error

    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Union[str, None],
            data: typing.Union[typing.Mapping[str, typing.Any], None],
            **kwargs,
    ):
        def _coerce(x):
            if isinstance(x, str):
                return {'id': x}
            if isinstance(x, dict) and 'id' in x:
                return x
            raise ValidationError('Value must be a list of ids or dictionaries containing ids')

        if value is None:
            return [] if self.many else None
        if self.many and not isinstance(value, (list, tuple)):
            raise ValidationError('For lists of related vocabulary item, the value must be a list/tuple')
        if isinstance(value, str):
            value = [value]
        elif isinstance(value, dict):
            value = [value]
        if isinstance(value, (tuple, list)):
            value = [_coerce(x) for x in value]
        else:
            raise ValidationError('Value must be a list of ids or dictionaries containing ids')

        # remove ancestors from the list
        ancestors = set()
        for d in value:
            id_ = d['id']
            last = ''
            for a in id_.split('/')[:-1]:
                a = last + a
                last = a + '/'
                ancestors.add(a)
        value = [x for x in value if x['id'] not in ancestors]

        if not self.many and len(value) > 1:
            raise ValidationError(f'Only one non-ancestor value required for '
                                  f'simple vocabulary terms, got {[x["id"] for x in value]}')

        # normalize the value
        value = [{'id': x['id']} for x in value]

        # check if data exist in vocabulary
        if not self.context.get('skip_vocabulary_check'):
            self._check_vocabulary(value)
        value.sort(key=lambda x: (-len(x['id'].split('/')), x['id']))
        return value if self.many else value[0]

    def _check_vocabulary(self, value):
        for val in value:
            try:
                resolved = self.related_field.pid_field.resolve(val['id'])
            except PIDDoesNotExistError:
                resolved = None

            if not resolved:
                raise ValidationError(f'Vocabulary item in vocabulary {self.related_field.pid_field._type_id} '
                                      f'with id {val["id"]} was not found')
