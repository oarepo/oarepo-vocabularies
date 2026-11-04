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

## Import ORCID data

This chapter is written for the repository administrator. It describes how to load the ORCID
registry into the `names` vocabulary using the **Import Annual ORCID Public Data File** job.

> In the administration interface the job is named **Import Annual ORCID Public Data File**; its
task identifier is `import_orcid_dump`.

### What is imported

The job streams ORCID's annual *Public Data File* from Figshare (public, CC0, **no credentials
needed**) and creates one `names` record per ORCID iD that has a public family name. The file is a
snapshot of the whole registry (~20M iDs) taken once a year.

Only the summaries archive is used (`*_summaries.tar.gz`); the `activities_*` archives of the same
release are not needed. Typical sizes: 2025 = 46.3 GB, 2026 = 57.3 GB compressed (streamed, never
written to disk).

### Prerequisites

- `oarepo-vocabularies` installed
- RabbitMQ and at least one Celery worker running: the archive is read by a single task, while the
  writes are handed over to the workers in batches.
- PostgreSQL and OpenSearch running, database migrations applied.
- Outbound HTTPS access to `api.figshare.com` and `ndownloader.figshare.com`, and to `api.ror.org`
  for affiliations missing from the vocabulary.
- **A ROR API client id** (free, register at <https://ror.readme.io/docs/client-id>), set as
  `OAREPO_VOCABULARIES_ORCID_ROR_CLIENT_ID`. Without it ROR applies a much lower rate limit and the
  import keeps waiting for it while fetching missing affiliations.
- No extra disk space; roughly one batch of records in memory (~5 MB at `batch_size=5000`).
- Celery and RabbitMQ allowing long-running tasks, see
  [Long-running tasks](#long-running-tasks-celery-and-rabbitmq).

### Configuration

In `invenio.cfg`:

> [!IMPORTANT]
> Do not forget `OAREPO_VOCABULARIES_ORCID_ROR_CLIENT_ID`. It is not required, but ROR allows
> 2,000 requests per 5 minutes only to identified clients; requests without a client id are limited
> to 50 per 5 minutes, which makes a full import much slower (it waits for the rate limit).

```python
# Year of the data file to import. Pin it: a load is then reproducible (same archive, same md5)
# and a new release cannot silently change what is being imported. Set to None to always take
# the newest file available.
OAREPO_VOCABULARIES_ORCID_DUMP_YEAR = 2026

# Where to look for the file. The collection lags behind the actual release, so the ORCID group
# is searched as well; both can normally be left at their defaults.
OAREPO_VOCABULARIES_ORCID_DUMP_COLLECTION_ID = 7931102
OAREPO_VOCABULARIES_ORCID_DUMP_GROUP_ID = 8907
OAREPO_VOCABULARIES_ORCID_DUMP_API_URL = "https://api.figshare.com/v2"

# Affiliations (ROR ids) referenced by ORCID records but missing from the affiliations vocabulary
# are imported from the ROR API. SET THIS: a client id raises ROR's rate limit considerably
# (register at https://ror.readme.io/docs/client-id). Sent as the `Client-Id` header.
OAREPO_VOCABULARIES_ORCID_ROR_CLIENT_ID = "<your-ror-client-id>"
OAREPO_VOCABULARIES_ORCID_ROR_API_URL = "https://api.ror.org/v2"
```

To see which file a given configuration resolves to, without importing anything:

```bash
invenio shell
>>> from oarepo_vocabularies.orcid.figshare import resolve_dump
>>> dump = resolve_dump()
>>> dump.year, dump.name, round(dump.size / 1e9, 1), dump.md5
(2026, 'ORCID_2026_10_summaries.tar.gz', 57.3, 'a55a16fe0b292bda03cc6016546c8984')
```

If a newer release exists than the pinned year, the job logs a warning and keeps the pinned one.

### Long-running tasks (Celery and RabbitMQ)

The task reading the archive runs for hours, and a batch write may wait for the ROR rate limit.
Two settings can interrupt that:

- **Celery time limits.** If `CELERY_TASK_TIME_LIMIT` / `CELERY_TASK_SOFT_TIME_LIMIT` are set on
  the instance, relax them for the import tasks only:

  ```python
  CELERY_TASK_ANNOTATIONS = {
      "oarepo_vocabularies.orcid.tasks.import_orcid_dump": {"time_limit": None, "soft_time_limit": None},
      "invenio_vocabularies.datastreams.tasks.write_many_entry": {"time_limit": 4 * 3600},
  }
  ```

- **RabbitMQ `consumer_timeout`** (default 30 minutes). A running task is not affected (its message
  is acknowledged when it starts), but messages the busy worker has already prefetched stay
  unacknowledged. When they wait longer than the timeout, RabbitMQ closes the channel
  (`PRECONDITION_FAILED - delivery acknowledgement on channel 1 timed out`) and the worker silently
  stops consuming until it is restarted. Raise the timeout for the queues the worker consumes,
  e.g. with a policy (RabbitMQ 3.12+, no restart needed):

  ```bash
  rabbitmqctl set_policy celery-long-tasks '^(celery|low)$' \
    '{"consumer-timeout": 14400000}' --apply-to queues    # 4 hours
  ```

  Only one policy applies to a queue (the one with the highest priority): if the queues already
  have a policy, add the `consumer-timeout` key to it instead. Alternatively set
  `consumer_timeout = 14400000` in `rabbitmq.conf` (global, needs a restart), or route the import
  to a dedicated queue and worker with `CELERY_TASK_ROUTES`. `CELERY_WORKER_PREFETCH_MULTIPLIER = 1`
  reduces the number of waiting messages but does not remove the risk.

### Create the job (once)

Either in the administration interface (**Administration → Jobs → Create**, task
`import_orcid_dump`), or from the command line:

```bash
# check the task name
invenio jobs types

# create the job
invenio jobs create --title "Import Annual ORCID Public Data File" --task import_orcid_dump

# note the job id
invenio jobs list
```

### Run the import

The run takes four optional arguments:

| Argument | Default | Meaning |
| --- | --- | --- |
| `year` | configured year | Release year to import. Empty = use `OAREPO_VOCABULARIES_ORCID_DUMP_YEAR`. |
| `url` | empty | Import an archive from an explicit url, skipping the Figshare discovery. **https only.** |
| `limit` | empty | Stop after N records — use this for the smoke test. |
| `batch_size` | 5000 | Records per message handed to the workers. |
| `update_existing` | `false` | Update records that already exist instead of skipping them. |

**1. Smoke test first** (a few minutes, exercises download, transformation, dispatch and writes):

```bash
curl -X POST https://<your-site>/api/jobs/<job_id>/runs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "title": "ORCID smoke test",
    "args": {
      "job_arg_schema": "ImportORCIDDumpArgsSchema",
      "year": 2026,
      "limit": 10000
    }
  }'
```

**2. Full import** — same call without `limit`:

```bash
curl -X POST https://<your-site>/api/jobs/<job_id>/runs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"title": "ORCID 2026", "args": {"job_arg_schema": "ImportORCIDDumpArgsSchema", "year": 2026}}'
```

`job_arg_schema` must always be sent — it tells the framework which argument schema to validate
against. The administration form fills it in automatically.

### Monitor the run

```bash
invenio jobs runs <job_id>          # list the runs of the job, with their ids and status
invenio jobs log <run_id> --follow  # tail the log until the run finishes
```

The administration interface shows the same information, including one subtask per batch.
The parent run accumulates `total_entries`; inserted/updated/errored counters live on the subtasks.

A full import is mostly limited by reading and parsing the archive, which happens in a single task:
expect **roughly 1,000 records per second** (about 6 hours per 20M records, measured on a
development machine). Adding workers only shortens the write tail. The first batches are slower
while missing affiliations are fetched from ROR.

### Verify the result

```bash
# number of imported name records
psql -c "select count(*) from name_metadata"

# number of indexed documents (alias '<SEARCH_INDEX_PREFIX>names-name-v2.0.0')
curl -s 'localhost:9200/<prefix>names-name-v2.0.0/_count?filter_path=count'

# a known record, both by id and through the resolve endpoint
curl -s https://<your-site>/api/names/0000-0002-1825-0097
```

After the load, merging index segments keeps search fast:

```bash
curl -X POST 'localhost:9200/<prefix>names-name-v2.0.0/_forcemerge?max_num_segments=1'
```

### Notes and expected behaviour

- **`WARNING Missing name or family name for ORCiD ID: …` is normal.** Records whose name is not
  public (or that were never claimed) cannot become name records and are skipped, not imported.
  For the same reason the final count is lower than the number of ORCID iDs in the file.
- **Re-running is safe.** Record ids are derived from the ORCID iD and inserted with
  `ON CONFLICT (pid) DO NOTHING`, so an interrupted or repeated run does not create duplicates;
  existing records are neither changed nor re-indexed. Use `update_existing=true` to rewrite and
  re-index rows that already exist (their version is incremented).
- **There is no resume checkpoint.** If the download is interrupted, start a new run; it re-reads
  the archive from the beginning (a few tens of minutes before it catches up).
- **Nothing is written to disk.** The archive is streamed over HTTPS and unpacked on the fly.
- **The load bypasses the vocabulary service** for speed: it writes the database rows and index
  documents directly, one `INSERT` and one `_bulk` request per batch. It reproduces what the
  service would store (`name` = "family, given", affiliations with an id stored as `{"id": ...}`)
  and what Invenio's indexer would write (the record's search dump, the prefixed index alias, the
  same external versioning), so the records can be read, searched, re-indexed and later edited
  through Invenio as usual. Permission checks are not applied.
- **Affiliations must exist in the affiliations vocabulary.** Invenio fails to read a name record
  that references an unknown affiliation id. The ids of a batch are therefore looked up with one
  query; missing ROR ids are fetched from the ROR API and created in the affiliations vocabulary.
  When ROR rate-limits the requests, the import waits and retries. An affiliation that still can
  not be resolved (unknown to ROR, or rate limited 10 times in a row) is stored with its name
  only; a later run with `update_existing=true` links it once the affiliation exists.
- **A different year does not delete old records.** Re-importing a newer snapshot adds and updates,
  it does not remove iDs that disappeared from the registry.

### Keeping the data current

The public data file is released **once a year**, so the vocabulary drifts. For incremental updates
use the stock Invenio job `import_orcid_names` (`ImportORCIDJob`), which reads ORCID's incremental
S3 feed (`v3.0-summaries` + `orcid-lambda-file`) and needs ORCID-issued AWS credentials:

```python
VOCABULARIES_ORCID_ACCESS_KEY = "..."
VOCABULARIES_ORCID_SECRET_KEY = "..."
VOCABULARIES_ORCID_SUMMARIES_BUCKET = "v3.0-summaries"
VOCABULARIES_ORCID_SYNC_SINCE = {"days": 1}
```

Roughly 136k records change per day (≈2M per month). Two caveats of that job as shipped: pass
`since` as a **naive** `"YYYY-MM-DD HH:MM:SS.ffffff"` value through `custom_args` (a timezone-aware
value makes the reader fail to parse it), and expect the whole `last_modified.csv.tar`
(~820 MB) to be read into memory per run.

### Troubleshooting

| Symptom | Cause / remedy |
| --- | --- |
| The job is not listed | Package not reinstalled after upgrade, or the web app/workers not restarted. Check `invenio jobs types`. |
| `Unknown field.` next to an argument | The run was submitted without `job_arg_schema` (or with the wrong one). Send `"job_arg_schema": "ImportORCIDDumpArgsSchema"`. |
| `no <year> public data file available` | That year does not exist; the error lists the years that do. Clear `year` to use the newest. |
| `HTTP Error 403: Forbidden` from `ndownloader.figshare.com` | The request was blocked by Figshare's edge, not rejected by this code: the API works while the downloader answers `403` (bare `awselb` page). Typical causes are a VPN/datacenter exit IP or a filtering proxy. Retry from an unfiltered network. |
| `url must use the https scheme` / `url must not contain credentials` | The archive url (job argument or `OAREPO_VOCABULARIES_ORCID_DUMP_API_URL`) is not an absolute https url. Only https urls are accepted, for every outbound request. |
| Run ends as *partially succeeded* | Some entries failed transformation; the log names the ORCID iDs. Usually invalid or private names. |
| `ROR API rate limit hit, retrying …` in the worker log | ROR throttled the affiliation lookups; the batch waits (`Retry-After`, or a minute) and retries, which slows the import down. Set `OAREPO_VOCABULARIES_ORCID_ROR_CLIENT_ID` to get a higher limit. |
| Worker log shows `delivery acknowledgement on channel 1 timed out`, then nothing is processed | RabbitMQ `consumer_timeout` expired for prefetched messages; restart the worker and raise the timeout, see [Long-running tasks](#long-running-tasks-celery-and-rabbitmq). |
| Nothing is written, run is fast | Check the worker log: the batches are processed by Celery, so a worker consuming a different queue will not process them. |

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
record.hierarchy.query_subterms()  # direct children
record.hierarchy.query_descendants()  # all descendants
```

**Hierarchy Properties**:

```python
record.hierarchy.level  # depth in tree
record.hierarchy.leaf  # has no children
record.hierarchy.titles  # [self_title, parent_title, ...]
record.hierarchy.ancestors_ids  # ['parent', 'grandparent', ...]
record.hierarchy.parent_id  # direct parent PID
```

### Parent Management

**Setting Parent**:

```python
# On creation
data = {"id": "eng.US", "title": {"en": "English (US)"}, "parent": {"id": "eng"}, "type": "languages"}
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
    system_identity, {"id": "eng", "title": {"en": "English"}, "type": "languages", "custom_fields": {"blah": "Hello"}}
)
```

### SKOS Mappings

Vocabulary items can declare SKOS mapping relations to concepts in other vocabularies/schemes (e.g. a local
"languages" term mapped to an external authority like LOC or ISO 639). Mappings are stored on the `mappings`
field as a list of objects validated by `MappingSchema`:

- `identifier` (string, required): the identifier of the matched concept in the target scheme (e.g. a URI or code)
- `scheme` (string, required): the name/identifier of the target scheme the mapping points to
- `relation` (string, required): the SKOS relation type between this vocabulary item and the target concept.
  Must be one of:
  - `exactMatch`: this item matches the target exactly. Usable for both import and export.
  - `broadMatch`: the target identifier is broader than this item. Usable for export only (not import).
  - `narrowMatch`: the target identifier is narrower than this item. Usable for import only (not export).
  - `closeMatch`: the target identifier is close to this item. Not usable for import or export.
  - `relatedMatch`: the target identifier is related to this item. Not usable for import or export.

**Setting mappings**:

```python
vocab_service.create(
    system_identity,
    {
        "id": "eng",
        "title": {"en": "English"},
        "type": "languages",
        "mappings": [
            {"identifier": "http://id.loc.gov/vocabulary/iso639-2/eng", "scheme": "loc", "relation": "exactMatch"},
            {"identifier": "eng-related-id", "scheme": "otherscheme", "relation": "relatedMatch"},
        ],
    },
)
```

**Searching by mapping** - use the `skos` search parameter with `relation:identifier` or
`relation:identifier@scheme` values (multiple values are OR-ed together):

```python
# Match items with an exact-match mapping to a given identifier in a given scheme
vocab_service.search(
    system_identity,
    {"skos": ["exactMatch:http://id.loc.gov/vocabulary/iso639-2/eng@loc"]},
    type="languages",
)

# scheme is optional - match on relation + identifier only
vocab_service.search(system_identity, {"skos": ["exactMatch:http://id.loc.gov/vocabulary/iso639-2/eng"]})
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
- `skos`: filter by SKOS mapping, values of form `relation:identifier` or `relation:identifier@scheme` (see [SKOS Mappings](#skos-mappings))

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
can_create = [IfVocabularyType("languages", then_=[AnyUser()], else_=[])]
```

`IfNonDangerousVocabularyOperation(then_, else_)`:

- Detects dangerous operations (ID change, parent change)
- Example: Allow custom field updates but restrict hierarchy changes

```python
can_update = [IfNonDangerousVocabularyOperation(then_=[AnyUser()], else_=[Admin()])]
```

**Configuration**:

```python
from invenio_vocabularies.services.permissions import PermissionPolicy

# Set custom permission policy
VOCABULARIES_PERMISSIONS_POLICY = MyCustomPermissionPolicy

# Or use presets
OAREPO_PERMISSIONS_PRESETS = {"vocabularies": PermissionPolicy}
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
parent = vocab_service.create(system_identity, {"id": "eng", "title": {"en": "English"}, "type": "languages"})

# Create child
child = vocab_service.create(
    system_identity,
    {"id": "eng.US", "title": {"en": "English (US)"}, "hierarchy": {"parent": "eng"}, "type": "languages"},
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
results = vocab_service.search(system_identity, {"h-parent": "eng"}, type="languages")

# Get all descendants
results = vocab_service.search(system_identity, {"h-ancestor": "eng"}, type="languages")

# Filter by level
results = vocab_service.search(system_identity, {"h-level": 2}, type="languages")
```

### Create Vocabulary with SKOS Mappings

```python
vocab_service.create(
    system_identity,
    {
        "id": "eng",
        "title": {"en": "English"},
        "type": "languages",
        "mappings": [
            {"identifier": "http://id.loc.gov/vocabulary/iso639-2/eng", "scheme": "loc", "relation": "exactMatch"},
        ],
    },
)

# Search for items mapped to a given identifier
results = vocab_service.search(
    system_identity,
    {"skos": ["exactMatch:http://id.loc.gov/vocabulary/iso639-2/eng@loc"]},
    type="languages",
)
```

### Update Parent Relationship

```python
# Change parent
vocab_service.update(
    system_identity,
    ("languages", "eng.US"),
    {"hierarchy": {"parent": "eng.UK"}, "title": {"en": "English (US)"}, "type": "languages"},
)

# Remove parent (make root)
vocab_service.update(
    system_identity,
    ("languages", "eng.US"),
    {"hierarchy": {"parent": None}, "title": {"en": "English (US)"}, "type": "languages"},
)
```

### Using Record API

```python
from oarepo_vocabularies.records.api import Vocabulary

# Get record
record = Vocabulary.pid.with_type_ctx("languages").resolve("eng.US")

# Access hierarchy
print(record.hierarchy.level)  # 2
print(record.hierarchy.parent_id)  # "eng"
print(record.hierarchy.leaf)  # True
print(record.hierarchy.ancestors_ids)  # ["eng"]

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

[project.entry-points."invenio_jobs.jobs"]
import_orcid_dump = "oarepo_vocabularies.orcid.jobs:ImportORCIDDumpJob"
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
