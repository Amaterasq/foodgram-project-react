from rest_framework.pagination import PageNumberPagination


class LimitResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'limit'
