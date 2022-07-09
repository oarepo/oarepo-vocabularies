from werkzeug.routing import BaseConverter


class PathOverrideConverter(BaseConverter):
    weight = 10000

    def __init__(self, map, *args, path=None, **kwargs):
        super().__init__(map, *args, **kwargs)
        self.path = path

    @property
    def regex(self):
        return self.path
