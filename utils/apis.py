# -*- coding: utf-8 -*-

"""
JSON API definition.
"""


class Page(object):
    """
    Page object for display pages.

    Attributes:
        item_count (int): The item count
        page_index (int): The current page index
        page_size (int): The number of items to show each page
        page_count (int): Total pages count
        offset (int): one of the parameters in SQL statement
        limit (int): another the parameter in SQL statement
        has_next (bool): Whether has next page
        has_previous (bool): Whether has previous page
    """

    def __init__(self, item_count, page_index=1, page_size=30):
        """
        Init Pagination by item_count, page_index and page_size.

        Args:
            item_count (int): The item count
            page_index (int): The current page index
            page_size (int): The number of items to show each page

        Examples:
            >>> p1 = Page(100, 1)
            >>> p1.page_count
            4
            >>> p1.offset
            0
            >>> p1.limit
            30
            >>> p2 = Page(90, 9, 10)
            >>> p2.page_count
            9
            >>> p2.offset
            80
            >>> p2.limit
            10
            >>> p3 = Page(91, 10, 10)
            >>> p3.page_count
            10
            >>> p3.offset
            90
            >>> p3.limit
            10
        """
        self.item_count = item_count
        self.page_size = page_size
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0)
        if (item_count == 0) or (page_index > self.page_count):
            self.offset = 0
            self.limit = 0
            self.page_index = 1
        else:
            self.page_index = page_index
            self.offset = self.page_size * (page_index - 1)
            self.limit = self.page_size
        self.has_next = self.page_index < self.page_count
        self.has_previous = self.page_index > 1

    def __str__(self):
        return 'item_count: {}, page_count: {}, page_index: {}, page_size: {}, offset: {}, limit: {}'.format(
            self.item_count, self.page_count, self.page_index, self.page_size, self.offset, self.limit)

    __repr__ = __str__


class StandardError(Exception):
    """
    the StandardError which contains error
    """
    def __init__(self, error: str):
        super(StandardError, self).__init__(error)
        self.error = error


class APIError(Exception):
    """
    the base APIError which contains error(required), data(optional) and msg(optional).
    """
    def __init__(self, error: str, msg=''):
        super(APIError, self).__init__(msg)
        self.error = error
        self.msg = msg


class APIValueError(APIError):
    """
    Indicate the input value has error or invalid. The data specifies the error field of input form.
    """
    def __init__(self, field: str):
        super(APIValueError, self).__init__('value:invalid', field)


class APIResourceNotFoundError(APIError):
    """
    Indicate the resource was not found. The data specifies the resource name.
    """
    def __init__(self, field: str):
        super(APIResourceNotFoundError, self).__init__('value:not_found', field)


class APIPermissionError(APIError):
    """
    Indicate the api has no permission.
    """
    def __init__(self, msg=''):
        super(APIPermissionError, self).__init__('permission:forbidden', msg)


class APINeedLogin(APIError):
    """
    Indicate the page needs login
    """
    def __init__(self, msg=''):
        super(APINeedLogin, self).__init__('permission:need_login', msg)


class APIMissingParams(APIError):
    """
    Indicate the request miss some params
    """
    def __init__(self, param=''):
        super(APIMissingParams, self).__init__('request:missing_params', param)


class APIBadRequest(APIError):
    """
    Indicate an invalid request
    """
    def __init__(self, msg=''):
        super(APIBadRequest, self).__init__('request:bad_request', msg)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
