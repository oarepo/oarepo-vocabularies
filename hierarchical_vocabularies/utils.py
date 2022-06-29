import copy
import json
import typing as t

import numpy as np
import pandas as pd


def find_empty_line_index(df: pd.DataFrame) -> int:
    """
    Find two consecutive empty lines and return the index of the first one

    :param df: Pandas dataframe
    :return: Index of the first of two consecutive empty lines
    :raise IndexError
    """

    # Empty row indexes
    empty_rows_indexes = df.index[df.isna().all(axis=1)]

    # diff: Compare two consecutive indexes: (n+1) - n
    # Return array value as True, if the result is 1. False if not.
    # nonzero: get rid of False values -> tuple of arrays
    # transpose: By default, transpose 2D array to matrix
    two_empty_lines_1th_index = np.transpose(
        np.nonzero((np.diff(empty_rows_indexes) == 1))
    )

    try:
        # It's not an index of rows but index of "2-empty-lines" indexes array (empty_rows_indexes)
        index_of_index = two_empty_lines_1th_index.flatten()[0]
    except IndexError:
        raise IndexError("No two consecutive empty lines found")
    else:
        # This is the index of actual row of the file
        first_2_empty_lines_index = empty_rows_indexes[index_of_index]
        return first_2_empty_lines_index


def clean_df(df: pd.DataFrame, split_index: int) -> tuple[pd.DataFrame, pd.DataFrame]:

    # Split df on a row after which 2 consecutive empty rows follow
    vocabulary_meta, vocabulary_data = np.split(df, [split_index], axis=0)

    # Drop empty columns from meta_info
    vocabulary_meta.dropna(axis=1, how="all", inplace=True)

    # Data
    vocabulary_data.dropna(inplace=True, how="all", axis=0)  # Remove empty rows
    vocabulary_data.reset_index(drop=True, inplace=True)  # Reset row index
    vocabulary_data.columns = vocabulary_data.iloc[0].values  # Set first row as header
    vocabulary_data.drop(labels=0, axis=0, inplace=True)  # Drop first row
    vocabulary_data.reset_index(drop=True, inplace=True)  # Reset row index again
    # Convert column "vocabulary_data" to int64
    vocabulary_data = vocabulary_data.astype({"level": int})

    vocabulary_data = vocabulary_data.where(vocabulary_data.notnull(), None)
    # vocabulary_data = vocabulary_data.replace({np.nan: None}).replace({pd.isnull: None})

    return vocabulary_meta, vocabulary_data


class RecordRefactorMethods:

    vocabulary_meta: dict = None

    def refactor_method(self, name: str) -> callable:
        """Returning refactor method for a specific vocabulary"""
        return self.__getattribute__(name)

    @staticmethod
    def _generic_refactor(
        record: dict, delete_keys: list, vocabulary_meta: dict
    ) -> dict:
        new_record = copy.deepcopy(record)
        delete_keys = ["title", "level", "slug"] + delete_keys

        new_record["title"] = RecordRefactorMethods._title(record)
        new_record["type"] = vocabulary_meta.get("code")

        # Delete keys
        for k, v in record.items():
            for item in delete_keys:
                if item in k:
                    del new_record[k]

        return new_record

    @staticmethod
    def _delete_keys(record: dict, keys: list) -> dict:
        """Delete keys from the dict"""

        new_record = copy.copy(record)

        for k, v in record.items():
            for item in keys:
                if item in k:
                    del new_record[k]

        return new_record

    @staticmethod
    def _title(record: dict) -> dict:
        """Generic parsing method to parse title_<lang>"""
        titles: dict = {
            k.rsplit("_")[1]: v
            for k, v in record.items()
            if k.startswith("title") and v is not None
        }

        return titles

    # @staticmethod
    # def _type(vocabulary_meta: dict):
    #     """Returns pid_type or first 6 chars from 'code' field as fallback"""
    #     vocabulary_type = vocabulary_meta.get("code", None)
    #     return {"id": vocabulary_type, "pid_type": vocabulary_type[:6]}

    @staticmethod
    def _related_uri(record: dict) -> dict:
        return {
            k.split("_")[1]: v
            for k, v in record.items()
            if "relatedURI" in k and v is not None
        }

    @staticmethod
    def _alpha3(record: dict) -> dict:
        return {
            k.split("_")[1]: v
            for k, v in record.items()
            if "alpha3" in k and v is not None
        }

    @staticmethod
    def _non_preferred_labels(record: dict) -> list[dict]:

        non_preferred_labels = {
            k: v for k, v in record.items() if "nonpreferredLabels" in k
        }

        return [
            {k.split("_")[1]: v}
            for k, v in non_preferred_labels.items()
            if v is not None
        ]

    @staticmethod
    def _remove_if_none(record: dict) -> dict:
        return {k: v for k, v in record.items() if v}

    @staticmethod
    def countries(record: dict, vocabulary_meta) -> dict:
        delete_keys = ["alpha3"]
        new_record = RecordRefactorMethods._generic_refactor(
            record, delete_keys, vocabulary_meta
        )

        new_record["alpha3Code"] = RecordRefactorMethods._alpha3(record)

        return RecordRefactorMethods._remove_if_none(new_record)

    @staticmethod
    def licenses(record: dict, vocabulary_meta: dict) -> dict:
        delete_keys = ["relatedURI"]

        new_record = RecordRefactorMethods._generic_refactor(
            record, delete_keys, vocabulary_meta
        )

        new_record["relatedURI"] = RecordRefactorMethods._related_uri(record)

        return RecordRefactorMethods._remove_if_none(new_record)

    @staticmethod
    def languages(record: dict, vocabulary_meta) -> dict:
        delete_keys = ["alpha3"]
        new_record = RecordRefactorMethods._generic_refactor(
            record, delete_keys, vocabulary_meta
        )

        new_record["alpha3Code"] = RecordRefactorMethods._alpha3(record)

        return RecordRefactorMethods._remove_if_none(new_record)

    @staticmethod
    def institutions(record: dict, vocabulary_meta) -> dict:
        delete_keys = [
            "tag",
            "nonpreferredLabels",
            "relatedURI",
            "contexts",
        ]

        new_record = RecordRefactorMethods._generic_refactor(
            record, delete_keys, vocabulary_meta
        )

        new_record["tags"] = [
            v for k, v in record.items() if "tag" in k and v is not None
        ]

        new_record["nonpreferredLabels"] = RecordRefactorMethods._non_preferred_labels(
            record
        )

        new_record["relatedURI"]: dict = RecordRefactorMethods._related_uri(record)

        new_record["contexts"] = [
            v for k, v in record.items() if "contexts" in k and v is not None
        ]

        # RID field to str
        new_record["RID"] = str(record["RID"]) if record["RID"] else None

        return RecordRefactorMethods._remove_if_none(new_record)

    @staticmethod
    def funders(record: dict, vocabulary_meta) -> dict:
        delete_keys = [
            "relatedURI",
            "aliases",
            "nonpreferredLabels",
        ]

        new_record = RecordRefactorMethods._generic_refactor(
            record, delete_keys, vocabulary_meta
        )

        new_record["relatedURI"]: dict = RecordRefactorMethods._related_uri(record)

        # Aliases
        new_record["aliases"] = [
            v for k, v in record.items() if "aliases" in k and v is not None
        ]

        # Non-Preferred labels
        new_record["nonpreferredLabels"] = RecordRefactorMethods._non_preferred_labels(
            record
        )

        return RecordRefactorMethods._remove_if_none(new_record)

    @staticmethod
    def access_rights(record: dict, vocabulary_meta) -> dict:
        delete_keys = ["relatedURI"]
        new_record = RecordRefactorMethods._generic_refactor(
            record, delete_keys, vocabulary_meta
        )

        new_record["relatedURI"]: dict = RecordRefactorMethods._related_uri(record)

        return RecordRefactorMethods._remove_if_none(new_record)

    @staticmethod
    def contributor_type(record: dict, vocabulary_meta) -> dict:
        delete_keys = ["relatedURI"]
        new_record = RecordRefactorMethods._generic_refactor(
            record, delete_keys, vocabulary_meta
        )

        new_record["relatedURI"]: dict = RecordRefactorMethods._related_uri(record)

        return RecordRefactorMethods._remove_if_none(new_record)

    @staticmethod
    def item_relation_type(record: dict, vocabulary_meta) -> dict:
        delete_keys = ["hint"]
        new_record = RecordRefactorMethods._generic_refactor(
            record, delete_keys, vocabulary_meta
        )

        new_record["hint"] = {
            k.split("_")[1]: v
            for k, v in record.items()
            if "hint" in k and v is not None
        }

        return RecordRefactorMethods._remove_if_none(new_record)

    @staticmethod
    def resource_type_related_item(record: dict, vocabulary_meta) -> dict:
        delete_keys = ["nonpreferredLables", "relatedURI"]
        new_record = RecordRefactorMethods._generic_refactor(
            record, delete_keys, vocabulary_meta
        )

        new_record["nonpreferredLabels"] = RecordRefactorMethods._non_preferred_labels(
            record
        )

        new_record["relatedURI"]: dict = RecordRefactorMethods._related_uri(record)

        return RecordRefactorMethods._remove_if_none(new_record)

    @staticmethod
    def resource_type(record: dict, vocabulary_meta) -> dict:
        delete_keys = ["relatedURI", "nonpreferredLabels"]
        new_record = RecordRefactorMethods._generic_refactor(
            record, delete_keys, vocabulary_meta
        )

        new_record["nonpreferredLabels"] = RecordRefactorMethods._non_preferred_labels(
            record
        )

        new_record["relatedURI"]: dict = RecordRefactorMethods._related_uri(record)

        return RecordRefactorMethods._remove_if_none(new_record)

    @staticmethod
    def subject_categories(record: dict, vocabulary_meta) -> dict:
        delete_keys = []
        new_record = RecordRefactorMethods._generic_refactor(
            record, delete_keys, vocabulary_meta
        )

        return new_record


class VocabularyRecord:
    def __init__(self, **kwargs) -> t.NoReturn:
        self.slug = str(kwargs.get("slug"))
        self.level = int(kwargs.get("level"))

        self.original_data: dict = kwargs
        self.refactored_data: dict = {}

    def __str__(self) -> str:
        return self.slug

    def __repr__(self) -> str:
        return json.dumps(self.__dict__, indent=2, ensure_ascii=False, default=str)

    def print_record(self) -> t.NoReturn:
        print(self.__repr__())

    def refactor(self, refactor_func: callable, vocabulary_meta: dict) -> t.NoReturn:
        self.refactored_data = refactor_func(self.original_data, vocabulary_meta)

    def add_id(self, value):
        self.refactored_data["id"] = value


class RecordsStack:
    def __init__(self):
        self.stack: list[VocabularyRecord] = []

    def add(self, record: VocabularyRecord) -> t.NoReturn:
        self.stack.append(record)

    def remove(self, item: VocabularyRecord) -> t.NoReturn:
        self.stack.remove(item)

    def last_in_stack(self) -> VocabularyRecord:
        return self.stack[-1]

    def replace_last(self, item: VocabularyRecord) -> t.NoReturn:
        self.stack[-1] = item

    def stack_url(self) -> str:
        """Build url path from items in stack"""
        return "/".join([record.slug for record in self.stack])

    def crop_to_level(self, level: int) -> t.NoReturn:
        """Make stack 'flatten' by filtering out equal or higher levels"""
        self.stack = [record for record in self.stack if record.level < level]
