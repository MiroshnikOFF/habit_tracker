from rest_framework.pagination import PageNumberPagination


class PlacePaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 30


class ActionPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 30


class HabitPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 30
