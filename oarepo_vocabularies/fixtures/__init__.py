#
# Data iterators
#
class DataIterator:
    """Data iterator base class."""

    def __init__(self, data_file):
        """Initialize iterator."""
        self._data_file = data_file
