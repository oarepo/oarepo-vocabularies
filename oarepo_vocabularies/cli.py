import csv
import io
import shutil
import typing
import zipfile
from pathlib import Path

import click
import requests
import tqdm
import yaml
from invenio_vocabularies.contrib.affiliations.models import AffiliationsMetadata
from oarepo_runtime.cli import oarepo
from oarepo_runtime.cli.fixtures import load


@oarepo.group(name="vocabularies", help="Vocabularies tools.")
def vocabularies():
    # just a runtime group
    pass


@vocabularies.command(name="import-ror")
@click.argument("uri", default="https://doi.org/10.5281/zenodo.6347574")
@click.pass_context
def import_ror(ctx: click.Context, uri: str):
    """Import ROR vocabulary from Zenodo.

    Args:
        uri (str): URI to the ROR vocabulary in Zenodo. Default is
            https://doi.org/10.5281/zenodo.6347574.
    """

    # download ZIP with ROR dump from Zenodo
    tmp_ror_file = Path("/tmp/ror.zip")
    if tmp_ror_file.exists():
        click.secho(f"Removing {tmp_ror_file}", fg="yellow")
        tmp_ror_file.unlink()
    download_ror(uri, tmp_ror_file)

    # get affiliations from database that are not added by this downloader
    records_not_added_by_ror = get_records_not_added_by_ror()

    # convert ROR dump to YAML, and filter out records that are not added by ROR
    tmp_ror_converted_dir = Path("/tmp/ror-converted")
    if tmp_ror_converted_dir.exists():
        click.secho(f"Removing {tmp_ror_converted_dir}", fg="yellow")
        shutil.rmtree(tmp_ror_converted_dir)

    tmp_ror_converted_dir.mkdir(parents=True)
    convert_ror(
        tmp_ror_file, tmp_ror_converted_dir / "ror.yaml", records_not_added_by_ror
    )

    # create a catalogue.yaml file to load the converted ROR dump
    (tmp_ror_converted_dir / "catalogue.yaml").write_text(
        """
affiliations:
- writer: affiliations
  update: true
- source: ./ror.yaml
"""
    )

    # and load it
    ctx.invoke(load, fixture_dir_or_catalogue=str(tmp_ror_converted_dir), verbose=True)


def convert_ror(
    tmp_ror_file: Path, output: Path, records_not_added_by_ror: dict[str, str]
):

    with open(output, "w", encoding="utf-8") as out_f:
        yaml.safe_dump_all(
            get_affiliation_records(tmp_ror_file, records_not_added_by_ror),
            out_f,
            default_flow_style=False,
            allow_unicode=True,
        )


def get_affiliation_records(
    tmp_ror_file: Path, records_not_added_by_ror: dict[str, str]
) -> typing.Generator[dict[str, typing.Any], None, None]:
    # unzip the file to get the csv file and open it
    with zipfile.ZipFile(tmp_ror_file, "r") as zip_ref:
        zf = [x for x in zip_ref.namelist() if x.endswith("schema_v2.csv")]
        if not zf:
            raise click.ClickException(
                f"Failed to find schema_v2.csv in {tmp_ror_file}"
            )
        click.secho(f"Processing {zf[0]}", fg="yellow")
        with zip_ref.open(zf[0], "r") as f:
            reader = csv.DictReader(
                io.TextIOWrapper(f, encoding="utf-8"),
                delimiter=",",
                quotechar='"',
            )

            for row in tqdm.tqdm(reader, leave=False):
                names = ror_to_multidict(row["names.types.label"])
                aliases = ror_to_multidict(row["names.types.alias"])
                term_id = "ror:" + row["id"].rsplit("/", 1)[-1]
                if row["id"] in records_not_added_by_ror:
                    # if there is a database record with ROR and at the same time
                    # it was not created from ROR, we need to skip it and not update
                    # the name
                    continue

                if aliases:
                    names = aliases

                if not names:
                    continue

                if "no_lang_code" in names:
                    n = names.pop("no_lang_code")
                    if "en" not in names:
                        names["en"] = n

                name = names.get("cs", names.get("en")) or next(iter(names.values()))
                yield {
                    "id": term_id,
                    "name": name,
                    "title": names,
                    "identifiers": [
                        {
                            "scheme": "ror",
                            "identifier": row["id"],
                        }
                    ],
                }


def ror_to_multidict(name: str) -> dict[str, str]:
    """Convert a ROR name to a multidict.

    Args:
        name (str): Name to convert, looks like en: aaaa; cs: bbbb

    Returns:
        dict: Multidict with the name and its type.
    """
    with_lang = [x.strip() for x in name.split(";")]
    return {
        x.split(":")[0].strip(): x.split(":")[1].strip()
        for x in with_lang
        if len(x.split(":")) == 2
    }


def download_ror(uri: str, tmp_ror_file: Path):
    resp = requests.get(uri)
    if resp.status_code != 200:
        raise click.ClickException(f"Failed to download {uri}: {resp.status_code}")
    # get link header with content type application/json
    zip_url = resp.links["item"]["url"]
    # download the zip file and store it as /tmp/ror.zip
    zip_resp = requests.get(zip_url, stream=True)
    if zip_resp.status_code != 200:
        raise click.ClickException(
            f"Failed to download {zip_url}: {zip_resp.status_code}"
        )
    click.secho(f"Downloading {zip_url} to {tmp_ror_file}", fg="yellow")
    with open(tmp_ror_file, "wb") as f:
        for chunk in tqdm.tqdm(
            zip_resp.iter_content(chunk_size=8192),
            total=int(zip_resp.headers.get("Content-Length", 0)) // 8192,
            unit="chunk",
            leave=False,
        ):
            f.write(chunk)
    click.secho(f"Downloaded {zip_url} to {tmp_ror_file}", fg="green")


@typing.no_type_check
def get_records_not_added_by_ror() -> dict[str, str]:
    not_from_ror_records: dict[str, str] = {}
    click.secho("Filtering records not added by ROR downloader", fg="yellow")

    for affiliation in tqdm.tqdm(
        AffiliationsMetadata.query.yield_per(1000), leave=False
    ):
        identifiers = affiliation.json.get("identifiers", [])
        ror_identifier = next((x for x in identifiers if x["scheme"] == "ror"), None)
        if not ror_identifier:
            continue
        ror_identifier = ror_identifier["identifier"]
        if not ror_identifier.startswith("https://ror.org/"):
            ror_identifier = "https://ror.org/" + ror_identifier.split("/")[-1]

        # if the identifier is from ROR, skip it
        if affiliation.pid.startswith("ror:"):
            continue

        not_from_ror_records[ror_identifier] = affiliation.pid
    click.secho(
        f"Got {len(not_from_ror_records)} records not added by ROR downloader",
        fg="green",
    )
    return not_from_ror_records
