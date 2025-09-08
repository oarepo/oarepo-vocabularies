#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
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
