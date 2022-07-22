from invenio_vocabularies.records.systemfields import VocabularyPIDFieldContext


class VocabularyHierarchyPIDFieldContext(VocabularyPIDFieldContext):
    def resolve(self, pid_value):
        """Resolve identifier.

        :params pid_value: Either a tuple ``(type_id, pid_value)`` or just a
            ``pid_value`` if the type context has been initialized using
            ``with_type_ctx()``.
        """
        pid_type = self.pid_type
        if pid_type is None:
            type_id, pid_value = pid_value
            pid_type = self.get_pid_type(type_id)

        # Create resolver
        resolver = self.field._resolver_cls(
            pid_type=pid_type,
            object_type=self.field._object_type,
            getter=self.record_cls.get_record,
        )

        # Resolve: TODO: speed this up by making several requests at once?
        resolved_pid = None
        records = []
        last_pid = ''
        for current_id in pid_value.split('/'):
            current_id = last_pid + current_id
            last_pid = current_id + '/'
            pid, record = resolver.resolve(current_id)
            resolved_pid = pid
            records.append(record)

        # order from this to ancestors
        records = list(reversed(records))

        records[0].ancestors = records
        self.field._set_cache(records[0], resolved_pid)

        return records[0]
