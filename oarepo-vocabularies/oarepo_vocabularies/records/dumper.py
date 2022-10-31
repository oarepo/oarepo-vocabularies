from invenio_records.dumpers import SearchDumper, SearchDumperExt


class HierarchyPathExt(SearchDumperExt):
    HIERARCHY_ATTR = 'hierarchy'
    HIERARCHY_PATH_ATTR = 'path'
    HIERARCHY_LEVEL_ATTR = 'level'
    HIERARCHY_REVERSE_PATH_ATTR = 'reverse_path'

    def dump(self, record, data):
        """Dump index data."""
        data[self.HIERARCHY_ATTR] = {
            self.HIERARCHY_PATH_ATTR: record.hierarchy_path,
            self.HIERARCHY_REVERSE_PATH_ATTR: record.hierarchy_path,
            self.HIERARCHY_LEVEL_ATTR: record.level
        }

    def load(self, data, record_cls):
        """Load (remove) indexed data."""
        data.pop(self.HIERARCHY_ATTR, None)


class OARepoVocabularyDumperBase(SearchDumper):
    pass
