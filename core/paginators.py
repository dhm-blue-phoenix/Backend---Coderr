from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    A standard pagination class that uses page numbers.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
