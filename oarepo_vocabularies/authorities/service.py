import abc


class AuthorityService(abc.ABC):
    @abc.abstractmethod
    def search(self, *, query=None, page=1, size=10, **kwargs):
        """
        Search the external authority service by the given text query and return
        page & size with the data. The returned structure must be the same as Invenio
        vocabulary listing, that is:
        ```
        {
            'hits': {
                'total': <number of results>,
                'hits': [
                    {'id': 1, title: {'en': ...}, ...},
                    {'id': 1, title: {'en': ...}, ...},
                ]
            },
            'links': {
                'self': ...,
                'next': ...
            }
        }
        ```
        """

    @abc.abstractmethod
    def get(self, item_id, *, uow, value, **kwargs):
        """
        Gets vocabulary item by id. Returns the item as JSON or KeyError if the item could not be found.
        @param item_id  value['id']
        @param uow      actual unit of work (if you need to create something inside the db, do it inside this uow)
        @param value    the value passed from the client
        """
