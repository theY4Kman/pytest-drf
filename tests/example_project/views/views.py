from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from tests.example_project.models import KeyValue


@api_view()
def query_params(request: Request) -> Response:
    return Response(request.query_params)


@api_view()
def headers(request: Request) -> Response:
    return Response(request.headers)


@api_view(['POST'])
def data(request: Request) -> Response:
    return Response(request.data)


class KeyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyValue
        fields = (
            'id',
            'key',
            'value',
        )


class KeyValueViewSet(viewsets.ModelViewSet):
    queryset = KeyValue.objects.order_by('id')
    serializer_class = KeyValueSerializer
    pagination_class = PageNumberPagination
