import json

import click
import numpy as np
import pandas as pd
from flask_principal import Identity, UserNeed
from invenio_access.permissions import any_user, system_process
from invenio_app.factory import create_api, create_app
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_vocabularies.records.models import VocabularyType
from pandas._libs.parsers import _NA_VALUES

from hierarchical_vocabularies.services.service import (
    HVocabulariesService,
    HVocabulariesServiceConfig,
)

from .utils import (
    RecordRefactorMethods,
    RecordsStack,
    VocabularyRecord,
    clean_df,
    find_empty_line_index,
)

api = create_api()
service = HVocabulariesService(config=HVocabulariesServiceConfig)


def identity():
    """Simple identity to interact with the service."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(any_user)
    i.provides.add(system_process)
    return i


# Remove values from default pandas NA_VALUES as they represent country codes
disable_na_values = [b"NA"]
my_default_na_values = [
    item.decode("UTF-8") for item in _NA_VALUES if item not in disable_na_values
]


@click.group()
def hvocabularies():
    """Hierarchical vocabularies command."""


@hvocabularies.command()
@click.argument("filepath", type=click.Path(exists=True))
def import_v(filepath):
    """Import vocabulary from XLS"""
    click.echo("Loading file:")
    click.echo(click.format_filename(filepath))
    df = pd.read_excel(filepath)

    print("\n")

    # Find 2 consecutive empty rows
    split_index = find_empty_line_index(df=df)
    print("split_index", split_index)
    # Refactor and clean the df
    vocabulary_meta, vocabulary_data = clean_df(df=df, split_index=split_index)

    print(vocabulary_meta.head())
    print("\n")
    # print(vocabulary_data.to_json(orient='records', indent=1, force_ascii=False))
    print("\n")
    # print(vocabulary_data.to_json(indent=2, orient='records'))

    aaa = vocabulary_data.to_dict(orient="records")

    print(vocabulary_meta.to_dict())

    all_nodes: list[TreeNode] = [
        TreeNode(name=record["slug"], **record) for record in aaa
    ]

    tree_root = TreeRoot()
    for i, new_node in enumerate(all_nodes):

        if i == 0:
            # First iteration (set Root)
            new_node.parent_oid = tree_root.oid  # Set Node ID to TreeRoot class
            new_node.parent_index = tree_root.index
            tree_root.add_child(new_node)
            tree_root.add_node(new_node)
        else:
            # Get last Node from upper/parent levels list
            parent_node: TreeNode = tree_root.levels[new_node.level - 1][-1]
            new_node.parent_oid = parent_node.oid  # Set parent ID
            new_node.parent_index = parent_node.index  # Set parent Index
            parent_node.add_child(new_node)
            tree_root.add_node(new_node)

    tree_root.print_tree_references(show_id="index")
    x = tree_root.build_tree()
    # tree_root.print_tree_shape()


@hvocabularies.command()
@click.argument("filepath", type=click.Path(exists=True))
def import_v2(filepath):
    """Import vocabulary from XLS"""
    click.echo(f"Loading file: {click.format_filename(filepath)}")

    # Dataframe: ignore cells with "NA" as NaN (Nambia country code)
    df = pd.read_excel(filepath, keep_default_na=False, na_values=my_default_na_values)

    # Find 2 consecutive empty rows
    split_index = find_empty_line_index(df=df)

    # Refactor and clean the df
    vocabulary_meta, vocabulary_data = clean_df(df=df, split_index=split_index)

    # print(vocabulary_data[["tags_0", "tags_1"]])
    # print(vocabulary_data.dtypes)

    vocabulary_meta_dict = vocabulary_meta.to_dict(orient="index")[0]
    vocabulary_items = vocabulary_data.to_dict(orient="records")

    vocabulary_code = vocabulary_meta_dict["code"]
    vocabulary_refactor_func = RecordRefactorMethods().refactor_method(vocabulary_code)

    vocabulary_records: list[VocabularyRecord] = []

    for item in vocabulary_items:
        record = VocabularyRecord(**item)
        record.refactor(vocabulary_refactor_func, vocabulary_meta_dict)
        # print(record.refactored_data)
        vocabulary_records.append(record)

        # print(json.dumps(record.refactored_data, indent=2, ensure_ascii=False))
        # print(record.refactored_data)

    with api.app_context():

        # Create type
        vocabulary_id = vocabulary_meta_dict.get("code", None)
        pid_type = vocabulary_meta_dict.get("pid_type", vocabulary_id[:6])

        existing_type = VocabularyType.query.filter_by(id=vocabulary_id).first()

        if not existing_type:
            service.create_type(
                identity=identity(), id=vocabulary_id, pid_type=pid_type
            )

        # Build stack and save
        stack = RecordsStack()

        for i, record in enumerate(vocabulary_records):

            print(record.refactored_data)

            try:

                try:
                    _prev_record = stack.last_in_stack()
                except IndexError:
                    # Empty stack
                    stack.add(record)
                    record.add_id(stack.stack_url())
                    service.create(identity=identity(), data=record.refactored_data)
                else:

                    # One more bigger level
                    if record.level - 1 == _prev_record.level:
                        stack.add(record)
                        record.add_id(stack.stack_url())
                        service.create(identity=identity(), data=record.refactored_data)
                        print(stack.stack_url())

                    # Equal to previous level
                    if record.level == _prev_record.level:
                        stack.replace_last(record)
                        record.add_id(stack.stack_url())
                        service.create(identity=identity(), data=record.refactored_data)
                        print(stack.stack_url())

                    # One more lower then previous level
                    if record.level + 1 == _prev_record.level:
                        stack.crop_to_level(level=record.level)
                        stack.add(record)
                        record.add_id(stack.stack_url())
                        service.create(identity=identity(), data=record.refactored_data)
                        print(stack.stack_url())

            except PIDAlreadyExists:
                print("Record already exists")
