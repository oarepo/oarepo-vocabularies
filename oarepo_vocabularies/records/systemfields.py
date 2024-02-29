from oarepo_runtime.records.systemfields import PathSelector


class HierarchyPartSelector(PathSelector):
    level = 0

    def __init__(self, *paths, level=None, **kwargs):
        super().__init__(*paths)
        if level is not None:
            self.level = level
        if not self.paths:
            raise ValueError("At least one path must be set")

    def select(self, data):
        parts = super().select(data)

        elements = []
        for dg in parts:
            ids = dg["hierarchy"]["ancestors_or_self"]
            titles = dg["hierarchy"]["title"]
            if len(ids) > self.level:
                elements.append(
                    {"id": ids[-1 - self.level], "title": titles[-1 - self.level]}
                )
        return elements
