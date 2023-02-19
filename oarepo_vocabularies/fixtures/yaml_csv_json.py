from . import DataIterator
import csv
import json
import yaml


class YamlIterator(DataIterator):
    """YAML data iterator that loads records from YAML files."""

    def __iter__(self):
        """Iterate over records."""
        with open(self._data_file) as fp:
            # Allow empty files
            data = yaml.safe_load(fp) or []
            for entry in data:
                yield entry


class CSVIterator(DataIterator):
    """CSV data iterator that loads records from CSV files."""

    def map_row(self, header, row):
        """Map a CSV row into a record."""
        entry = {}
        for attr, value in zip(header, row):
            if attr == "tags":
                value = [x.strip() for x in value.split(",")]
            keys = attr.split("__")
            if len(keys) == 1:
                entry[keys[0]] = value
            elif len(keys) == 2:
                if keys[0] not in entry:
                    entry[keys[0]] = {}
                entry[keys[0]][keys[1]] = value
        return entry

    def __iter__(self):
        """Iterate over records."""
        with open(self._data_file) as fp:
            reader = csv.reader(fp, delimiter=";", quotechar='"')
            header = next(reader)
            for row in reader:
                yield self.map_row(header, row)


class JSONLinesIterator(DataIterator):
    """JSON Lines data iterator that loads records from JSON Lines files."""

    def __iter__(self):
        """Iterate over records."""
        with open(self._data_file) as fp:
            for line in fp:
                yield json.loads(line)
