from flask_resources import ResourceConfig

class VocabularyTypeResourceConfig(ResourceConfig):
    blueprint_name = 'vocabulary_types'
    url_prefix = '/vocabularies'
    
    routes = {
        "list": "/",
    }
    