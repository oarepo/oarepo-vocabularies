from oarepo_runtime.cli import oarepo
from flask.cli import with_appcontext
from oarepo_vocabularies.fixtures.fixtures import PrioritizedVocabulariesFixtures
import click
from invenio_access.permissions import system_identity
from invenio_vocabularies.records.api import Vocabulary


@oarepo.group(name="vocabularies", help="Vocabularies tools.")
def vocabularies():
    # just a runtime group
    pass


@vocabularies.command("fixtures")
@click.argument("app_dir", required=False)
@with_appcontext
def create_fixtures(app_dir=None):
    """Create the vocabulary fixtures."""
    click.secho("Creating required fixtures...", fg="green")

    fixture = PrioritizedVocabulariesFixtures(
        system_identity, app_data_folder=app_dir, delay=False
    )
    fixture.load()
    Vocabulary.index.refresh()
