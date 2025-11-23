# OARepo Vocabularies

Enhanced Invenio-Vocabularies extension providing hierarchical vocabulary support, custom fields integration, and advanced permission controls for vocabulary management in Invenio-based repositories.

## Features

- **Hierarchical Vocabularies**: Parent-child relationships with automatic level tracking, ancestor chains, and leaf detection
- **Custom Fields**: Extend vocabulary records with custom metadata fields using Invenio custom fields system
- **Advanced Permissions**: Fine-grained vocabulary-type-specific permission policies with dangerous operation detection
- **Multi-language Support**: ICU collation support for sorting and suggestions across multiple languages
- **UI Components**: Complete UI resource layer with search, detail, edit, and create views
- **API Extensions**: REST API endpoints for vocabulary types and hierarchy operations

## Installation

```bash
pip install oarepo-vocabularies
```

### Configuration

Add to `invenio.cfg`:

```python
from oarepo_vocabularies.services.config import VocabulariesConfig
from oarepo_vocabularies.resources.config import VocabulariesResourceConfig

VOCABULARIES_SERVICE_CONFIG = VocabulariesConfig
VOCABULARIES_RESOURCE_CONFIG = VocabulariesResourceConfig
```

## Core Components

### Vocabulary Record Model

The `Vocabulary` record class extends `invenio_vocabularies.records.api.Vocabulary`:

- **System Fields**:
  - `hierarchy`: `HierarchySystemField` - manages hierarchy metadata (level, titles, ancestors, leaf status)
  - `parent`: `ParentSystemField` - handles parent-child relationships
  - `custom_fields`: `DictField` - stores custom metadata
  - `relations`: `MultiRelationsField` - manages parent and custom field relations

- **Hierarchy Database Model** (`VocabularyHierarchy`):
  - `id`: UUID reference to vocabulary metadata
  - `parent_id`: UUID reference to parent hierarchy record
  - `pid`: String PID of the vocabulary term
  - `level`: Integer depth in hierarchy (1 for root)
  - `titles`: JSON array of title objects in hierarchy order
  - `ancestors`: JSON array of ancestor PIDs (parent to root)
  - `ancestors_or_self`: JSON array including self PID
  - `leaf`: Boolean indicating if term has children

### Hierarchy Operations

**Automatic Hierarchy Management**:

- On record creation: sets level, initializes ancestors, marks parent as non-leaf
- On parent change: updates entire descendant subtree, fixes previous parent leaf status
- On deletion: validates no children exist, updates parent leaf status

**Query Methods**:


```python
# Get direct children
VocabularyHierarchy.get_direct_subterms_ids(parent_id)

# Get all descendants (recursive)
VocabularyHierarchy.get_subterms_ids(parent_id)

# Access from record
record.hierarchy.query_subterms()        # direct children
record.hierarchy.query_descendants()     # all descendants
```

**Hierarchy Properties**:

```python
record.hierarchy.level              # depth in tree
record.hierarchy.leaf               # has no children
record.hierarchy.titles             # [self_title, parent_title, ...]
record.hierarchy.ancestors_ids      # ['parent', 'grandparent', ...]
record.hierarchy.parent_id          # direct parent PID
```

### Parent Management

**Setting Parent**:

```python
# On creation
data = {
    "id": "eng.US",
    "title": {"en": "English (US)"},
    "parent": {"id": "eng"},
    "type": "languages"
}
vocab = Vocabulary.create(data=data)

# On update
record.parent.set("new_parent_id")  # or None to remove
record.commit()
```

**Constraints**:

- Cannot delete record with children (raises `ValidationError`)
- Cannot create cycles (parent cannot be descendant)
- Parent change triggers full descendant tree update

### Custom Fields

**Configuration**:

```python
from invenio_records_resources.services.custom_fields import TextCF

VOCABULARIES_CF = [
    TextCF(name="blah"),
    # ... other custom fields
]
```

**Usage**:

```python
vocab_service.create(
    system_identity,
    {
        "id": "eng",
        "title": {"en": "English"},
        "type": "languages",
        "custom_fields": {"blah": "Hello"}
    }
)
```

### Services

**VocabulariesConfig** (`oarepo_vocabularies.services.config.VocabulariesConfig`):

- Extends `invenio_vocabularies.services.VocabulariesServiceConfig`
- Adds `KeepVocabularyIdComponent` - prevents ID changes on update
- Adds `ScanningOrderComponent` - manages vocabulary ordering
- Schema: `VocabularySchema` with hierarchy and custom_fields support
- Search: `VocabularySearchOptions` with hierarchy filters

**VocabularyTypeService** (`oarepo_vocabularies.services.service.VocabularyTypeService`):

- Lists available vocabulary types with metadata
- Aggregates term counts per vocabulary type
- Provides links to vocabulary listings

**Service Components**:

- `KeepVocabularyIdComponent`: Ensures vocabulary ID remains constant during updates
- `ScanningOrderComponent`: Handles vocabulary item ordering logic

### Search Options

**VocabularySearchOptions** parameters:

- `type`: vocabulary type filter
- `h-level`: filter by hierarchy level
- `h-parent`: filter by direct parent PID
- `h-ancestor`: filter by any ancestor PID
- `h-ancestor-or-self`: filter including self
- `tags`: filter by tags
- `updated_after`: filter by update timestamp
- `ids`: list of (type, id) tuples for specific records
- `source`: specify returned fields

**Sort Options**:

- `bestmatch`: relevance score (default for queries)
- `title`: alphabetical by title (language-aware)
- `newest`: most recently created first
- `oldest`: creation date ascending

**Query Parser**:

- Boosts matches in current language (10x for title, 5x for hierarchy titles)
- Default operator: AND

### Resources

**VocabulariesResourceConfig**:

- Extends `invenio_vocabularies.resources.config.VocabulariesResourceConfig`
- Adds hierarchy search parameters (`h-parent`, `h-ancestor`, `h-level`)
- Adds UI JSON serializer (`application/vnd.inveniordm.v1+json`)

**Vocabulary Type Resource**:

- Endpoint: `/api/vocabularies/`
- Lists available vocabulary types with counts
- Returns configured metadata (name, description, icons)

**API Links** (generated for each vocabulary):

- `self`: API detail endpoint
- `self_html`: UI detail page
- `vocabulary`: API list for vocabulary type
- `vocabulary_html`: UI search page
- `edit_html`: UI edit form
- `parent`: parent record (if exists)
- `parent_html`: parent UI page
- `children`: API list of direct children
- `children_html`: UI list of children
- `descendants`: API list of all descendants
- `descendants_html`: UI list of descendants

### Permissions

**Permission Generators**:

`IfVocabularyType(vocabulary_type, then_, else_)`:

- Conditional permission based on vocabulary type
- Example: Allow all users to manage "languages" but restrict "countries"

```python
can_create = [
    IfVocabularyType("languages", then_=[AnyUser()], else_=[])
]
```

`IfNonDangerousVocabularyOperation(then_, else_)`:

- Detects dangerous operations (ID change, parent change)
- Example: Allow custom field updates but restrict hierarchy changes

```python
can_update = [
    IfNonDangerousVocabularyOperation(then_=[AnyUser()], else_=[Admin()])
]
```

**Configuration**:

```python
from invenio_vocabularies.services.permissions import PermissionPolicy

# Set custom permission policy
VOCABULARIES_PERMISSIONS_POLICY = MyCustomPermissionPolicy

# Or use presets
OAREPO_PERMISSIONS_PRESETS = {
    "vocabularies": PermissionPolicy
}
```

**Dangerous Operations**:

- Changing vocabulary `id` field
- Changing hierarchy parent (adding/removing/changing)

### UI Views

**Blueprints**:

- `oarepo_vocabularies_ui`: main vocabulary UI (search, detail, edit, create)
- `oarepo_vocabulary_type_ui`: vocabulary type listing UI

**UI Components**:

- `VocabularyTypeAndProps`: provides vocabulary type metadata to templates
- `DepositVocabularyOptionsComponent`: vocabulary selector for deposits

**Templates**:

- Search results page with hierarchy breadcrumbs
- Detail page showing hierarchy position
- Edit form with parent selector
- Create form with vocabulary type selection

### CLI Commands

```bash
# Vocabulary management (extensible)
invenio oarepo vocabularies --help
```

### Configuration Options

```python
# Permission policy factory
VOCABULARIES_PERMISSIONS_POLICY = "path.to.PermissionPolicy"

# Vocabulary type metadata
INVENIO_VOCABULARY_TYPE_METADATA = {
    "languages": {
        "name": {"en": "Languages", "cs": "Jazyky"},
        "description": {"en": "Language vocabulary", "cs": "Slovník jazyků"},
        # ... additional metadata
    }
}

# Custom fields definition
VOCABULARIES_CF = [
    TextCF(name="custom_field_1"),
    # ...
]

# Sort/suggest custom fields
OAREPO_VOCABULARIES_SORT_CF = ["field1", "field2"]
OAREPO_VOCABULARIES_SUGGEST_CF = ["field1"]

# Cache settings for facets
VOCABULARIES_FACET_CACHE_SIZE = 2048
VOCABULARIES_FACET_CACHE_TTL = 60 * 60 * 24  # 24 hours

# Service/resource overrides
OAREPO_VOCABULARY_TYPE_SERVICE = VocabularyTypeService
OAREPO_VOCABULARY_TYPE_SERVICE_CONFIG = VocabularyTypeServiceConfig
OAREPO_VOCABULARY_TYPE_RESOURCE = VocabularyTypeResource
OAREPO_VOCABULARY_TYPE_RESOURCE_CONFIG = VocabularyTypeResourceConfig
```

## API Examples

### Create Hierarchical Vocabulary

```python
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service

# Create parent
parent = vocab_service.create(
    system_identity,
    {
        "id": "eng",
        "title": {"en": "English"},
        "type": "languages"
    }
)

# Create child
child = vocab_service.create(
    system_identity,
    {
        "id": "eng.US",
        "title": {"en": "English (US)"},
        "hierarchy": {"parent": "eng"},
        "type": "languages"
    }
)

# Access hierarchy data
print(child.data["hierarchy"])
# {
#     "level": 2,
#     "titles": [{"en": "English (US)"}, {"en": "English"}],
#     "ancestors": ["eng"],
#     "ancestors_or_self": ["eng.US", "eng"],
#     "leaf": True,
#     "parent": "eng"
# }
```

### Search with Hierarchy Filters

```python
# Get all children of a term
results = vocab_service.search(
    system_identity,
    {"h-parent": "eng"},
    type="languages"
)

# Get all descendants
results = vocab_service.search(
    system_identity,
    {"h-ancestor": "eng"},
    type="languages"
)

# Filter by level
results = vocab_service.search(
    system_identity,
    {"h-level": 2},
    type="languages"
)
```

### Update Parent Relationship

```python
# Change parent
vocab_service.update(
    system_identity,
    ("languages", "eng.US"),
    {
        "hierarchy": {"parent": "eng.UK"},
        "title": {"en": "English (US)"},
        "type": "languages"
    }
)

# Remove parent (make root)
vocab_service.update(
    system_identity,
    ("languages", "eng.US"),
    {
        "hierarchy": {"parent": None},
        "title": {"en": "English (US)"},
        "type": "languages"
    }
)
```

### Using Record API

```python
from oarepo_vocabularies.records.api import Vocabulary

# Get record
record = Vocabulary.pid.with_type_ctx("languages").resolve("eng.US")

# Access hierarchy
print(record.hierarchy.level)           # 2
print(record.hierarchy.parent_id)       # "eng"
print(record.hierarchy.leaf)            # True
print(record.hierarchy.ancestors_ids)   # ["eng"]

# Query children
children = record.hierarchy.query_subterms()

# Update parent programmatically
record.parent.set("new_parent_id")
record.commit()
```

## Testing

```bash
# Run all tests
./run.sh test

# Run specific test
pytest tests/test_hierarchy.py -v

# Run with coverage
pytest --cov=oarepo_vocabularies tests/
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev,tests]"

# Format code
black oarepo_vocabularies tests
isort oarepo_vocabularies tests
autoflake --in-place --remove-all-unused-imports -r oarepo_vocabularies

# Type checking
mypy oarepo_vocabularies
```

## Entry Points

The package registers several Invenio entry points:

```python
[project.entry-points."invenio_base.apps"]
oarepo_vocabularies = "oarepo_vocabularies.ext:OARepoVocabularies"
oarepo_vocabularies_ui = "oarepo_vocabularies.ui.ext:InvenioVocabulariesAppExtension"

[project.entry-points."invenio_base.api_apps"]
oarepo_vocabularies = "oarepo_vocabularies.ext:OARepoVocabularies"
oarepo_vocabularies_ui = "oarepo_vocabularies.ui.ext:InvenioVocabulariesAppExtension"

[project.entry-points."invenio_jsonschemas.schemas"]
oarepo_vocabularies = "oarepo_vocabularies.records.jsonschemas"

[project.entry-points."invenio_base.blueprints"]
oarepo_ui = "oarepo_vocabularies.views.app:create_app_blueprint"
oarepo_vocabularies_ui = "oarepo_vocabularies.ui.views:create_blueprint"
oarepo_vocabulary_type_ui = "oarepo_vocabularies.ui.views:create_vocabulary_type_blueprint"

[project.entry-points."invenio_base.api_blueprints"]
oarepo_vocabulary_type_api = "oarepo_vocabularies.views.api:create_api_blueprint"

[project.entry-points."invenio_assets.webpack"]
oarepo_vocabularies_ui_theme = "oarepo_vocabularies.ui.theme.webpack:theme"

[project.entry-points."invenio_i18n.translations"]
oarepo_vocabularies_ui = "oarepo_vocabularies"
```

## License

Copyright (c) 2025 CESNET z.s.p.o.

OARepo Vocabularies is free software; you can redistribute it and/or modify it under the terms of the MIT License. See [LICENSE](LICENSE) file for more details.

## Links

- Documentation: <https://narodni-repozitar.github.io/developer-docs/docs/technology/invenio/nrp-toolchain/plugins/vocabularies>
- Repository: <https://github.com/oarepo/oarepo-vocabularies>
- PyPI: <https://pypi.org/project/oarepo-vocabularies/>
- Issues: <https://github.com/oarepo/oarepo-vocabularies/issues>
- OARepo Project: <https://github.com/oarepo>

## Acknowledgments

This project builds upon [Invenio Framework](https://inveniosoftware.org/) and is developed as part of the OARepo ecosystem.
