from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Пагинатор с возможностью ограничения размера страницы."""
    page_size_query_param = 'limit'
