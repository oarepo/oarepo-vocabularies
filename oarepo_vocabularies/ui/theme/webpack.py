from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "oarepo_vocabularies_search": "./js/oarepo_vocabularies_ui/search/app.js",
                "oarepo_vocabularies_ui_components": "./js/oarepo_vocabularies_ui/custom-components.js",
                "oarepo_vocabularies_detail": "./js/oarepo_vocabularies_ui/detail/app.js",
                "oarepo_vocabularies_form": "./js/oarepo_vocabularies_ui/form/app.js",
            },
            dependencies={
                "@tanstack/react-query": "^4",
            },
            devDependencies={},
            aliases={
                "@translations/oarepo_vocabularies_ui": "./translations/oarepo_vocabularies_ui",
                "@js/oarepo_vocabularies": "js/oarepo_vocabularies_ui",
            },
        )
    },
)
