from rest_framework.test import APIClient


class DRFTestClient(APIClient):
    """DRF APIClient which supports passing a headers kwarg

    With the default APIClient, headers must be passed in WSGI environ form
    (i.e. HTTP_CONTENT_TYPE='application/json' for 'Content-Type: application/json')
    """

    def generic(self,
                method,
                path,
                data='',
                content_type='application/octet-stream',
                secure=False,
                headers=None,
                **extra):
        if headers:
            extra.update({
                f'HTTP_{name.upper().replace("-", "_")}': value
                for name, value in headers.items()
            })
        return super().generic(method, path, data, content_type, secure, **extra)


