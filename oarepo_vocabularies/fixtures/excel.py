from . import DataIterator
import openpyxl
from invenio_vocabularies.datastreams.errors import ReaderError
import re


class ExcelIterator(DataIterator):
    def __iter__(self):
        try:
            wb_obj = openpyxl.load_workbook(self._data_file)
            sheet_obj = wb_obj.active
        except Exception as err:
            raise ReaderError(
                f"Cannot decode excel file {self._data_file.name}: {str(err)}"
            )

        header, data = self.get_excel_data(sheet_obj)
        for row in data:
            print(">>>>>>>>>>>>", self._data_file, row)
            yield row

    def get_excel_data(self, sheet_obj):
        """
        returns an iterator (header, data)
        """
        header = []
        data = []
        it = sheet_obj.iter_rows()

        try:
            row = next_row(it)
            while empty(row):
                row = next_row(it)
            while not empty(row):
                header.append(row)
                row = next_row(it)
            while empty(row):
                row = next_row(it)
            while True:
                if not empty(row):
                    data.append(row)
                row = next_row(it)
        except StopIteration:
            pass
        if not data:
            return [], self.to_dict(header)
        else:
            return self.to_dict(header), self.to_dict(data)

    def to_dict(self, dta):
        def is_array(val):
            try:
                int(val)
                return True
            except:
                return False

        def set_single(container, key, val):
            try:
                key = int(key)
                while key >= len(container):
                    container.append(None)
                container[key] = val
            except (TypeError, ValueError):
                container[key] = val

        def iterset(k, v, container):
            while True:
                current_key = k[0]
                next_key = k[1] if len(k) > 1 else None
                if not next_key:
                    set_single(container, current_key, v)
                    return
                if isinstance(container, list):
                    container.append({} if not is_array(next_key) else [])
                    container = container[-1]
                else:
                    container = container.setdefault(
                        current_key, {} if not is_array(next_key) else []
                    )
                k = k[1:]

        def to_dict_item(header, item):
            ret = RowDict()
            for k, v in zip(header, item):
                if not k:
                    continue
                v = v if v is not None else ""
                v = str(v).strip()
                if v:
                    iterset(k, v, ret)
            return ret

        keys = [re.split("[_.]", x) if x else None for x in dta[0]]
        return [to_dict_item(keys, d) for d in dta[1:]]


def next_row(it):
    return [x.value for x in next(it)]


def empty(r):
    for val in r:
        if val:
            return False
    return True


class RowDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._header = {}
