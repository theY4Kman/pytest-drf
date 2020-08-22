from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


@api_view()
def status_code(request: Request, code: int) -> Response:
    return Response(status=code)
