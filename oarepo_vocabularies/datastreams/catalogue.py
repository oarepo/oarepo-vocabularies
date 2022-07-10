import os

import yaml
from flask import current_app
from invenio_vocabularies.datastreams import DataStreamFactory
from invenio_vocabularies.records.models import VocabularyType


class YAMLCatalogueReader:
    """
    TODO: when invenio supports factories in cli, consider moving to factories & invenio catalogue

    YAML format for oarepo vocabularies so that we can load multiple vocabularies at the same time.
    File format: array of the following:

    - code: <code>
      pid: <pid_type>           # optional, if not set, equal to code
      service: <service-name>   # service to use, defaults to config.OAREPO_DEFAULT_VOCABULARY_SERVICE if not set
      title:
        cs: <title in czech>
        en: <title in english>...
      file:            # reference to the file
    """

    def iter(self, fp_or_fname):
        if isinstance(fp_or_fname, str):
            fp = open(fp_or_fname, 'rb')
        else:
            fp = fp_or_fname
        try:
            yaml_path = fp.name
            yaml_dir_path = os.path.dirname(yaml_path)
            data = yaml.safe_load(fp) or []
            for entry in data:
                vt = VocabularyType.query.filter_by(id=entry['code']).one_or_none()
                if not vt:
                    VocabularyType.create(id=entry['code'], pid_type=data.get('pid', entry['code']))
                vocabulary_file = open(os.path.join(yaml_dir_path, entry['file']))
                service_name = entry.get('service') or current_app.config['OAREPO_DEFAULT_VOCABULARY_SERVICE']
                yield entry['code'], service_name, vocabulary_file
        finally:
            if isinstance(fp_or_fname, str):
                fp.close()

    def create_or_update_vocabularies(self, fp_or_fname, identity, update=False):
        for vocabulary_type, service, vocabulary_file in self.iter(fp_or_fname):
            ds = DataStreamFactory.create(
                readers_config=[{
                    'type': 'excel',
                    'args': {
                        'vocabulary_type': vocabulary_type,
                        'origin': vocabulary_file,
                    }
                }],
                transformers_config=[{
                    'type': 'hierarchy',
                    'args': {}
                }],
                writers_config=[{
                    'type': 'service',
                    'args': {
                        'service_or_name': service,
                        'update': update,
                        'identity': identity
                    }
                }],
            )

            success, errored, filtered = 0, [], 0
            for result in ds.process():
                if result.filtered:
                    filtered += 1
                if result.errors:
                    errored.append(result.errors)
                else:
                    success += 1
            return success, errored, filtered
