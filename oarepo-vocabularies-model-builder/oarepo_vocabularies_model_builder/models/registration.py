import importlib.resources as pkg_resources

from .. import models
from yaml import full_load

hvocabulary = full_load(pkg_resources.open_text(models, 'hvocabulary.yaml'))
hvocabulary_basic_model = full_load(pkg_resources.open_text(models, 'hvocabulary-basic-model.yaml'))
