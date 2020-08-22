from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import (
    CursorPagination,
    LimitOffsetPagination,
    PageNumberPagination,
)


class PageNumberPaginationView(GenericAPIView, mixins.ListModelMixin):
    queryset = ()
    pagination_class = PageNumberPagination


class LimitOffsetPaginationView(GenericAPIView, mixins.ListModelMixin):
    queryset = ()
    pagination_class = LimitOffsetPagination


class CursorPaginationView(GenericAPIView, mixins.ListModelMixin):
    queryset = ()
    pagination_class = CursorPagination
