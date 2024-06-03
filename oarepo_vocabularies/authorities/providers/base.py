import abc


class AuthorityProvider(abc.ABC):
    @abc.abstractmethod
    def search(self, identity, params, **kwargs):
        """
        Search the external authority service by the given text query.

        @param identity: current user identity
        @param params:   query parameters dict in form of {"q": string, "page": number, ...}
        @return:         a tuple of: (items, total?, page_size?)
        """

    @abc.abstractmethod
    def get(self, identity, item_id, *, uow, value, **kwargs):
        """
        Gets vocabulary item by id. Returns the item as JSON or KeyError if the item could not be found.

        @param item_id:  value['id']
        @param uow:      actual unit of work (if you need to create something inside the db, do it inside this uow)
        @param value:    the value passed from the client
        """
