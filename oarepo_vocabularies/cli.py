import click
from oarepo_runtime.cli import oarepo


@oarepo.group(name="vocabularies", help="Vocabularies tools.")
def vocabularies():
    # just a runtime group
    pass


@vocabularies.command(name="import-ror")
@click.argument("uri", default="https://doi.org/10.5281/zenodo.6347574")
def import_ror(uri: str):
    from oarepo_vocabularies.tasks import import_ror_from_zenodo

    import_ror_from_zenodo(uri=uri)
