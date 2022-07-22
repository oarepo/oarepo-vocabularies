from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import TransformerError
from invenio_vocabularies.datastreams.transformers import BaseTransformer


class HierarchyTransformer(BaseTransformer):
    def __init__(self):
        super().__init__()
        self.stack = []

    def apply(self, stream_entry: StreamEntry, *args, **kwargs):
        if not stream_entry.entry:
            return stream_entry

        level = stream_entry.entry.pop('level', None)
        if not level:
            return stream_entry
        level = int(level)
        while level < len(self.stack) + 1:
            self.stack.pop()

        if level != len(self.stack) + 1:
            raise TransformerError(f"Bad level for entry {stream_entry.entry}")

        self.stack.append(stream_entry.entry['id'])
        stream_entry.entry['id'] = '/'.join(self.stack)
        return stream_entry
