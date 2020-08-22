from django.urls import include, path
from rest_framework import routers

import tests.testapp.views.authentication
import tests.testapp.views.authorization
import tests.testapp.views.pagination
import tests.testapp.views.status
import tests.testapp.views.views
from tests.testapp import views

router = routers.DefaultRouter()
router.register('views/key-values', views.views.KeyValueViewSet, basename='views-key-values')

urlpatterns = [
    path('', include(router.urls)),

    path('authentication/user-info', views.authentication.user_info, name='authentication-user-info'),

    path('authorization/login-required', views.authorization.login_required, name='authorization-login-required'),

    path('pagination/page-number', views.pagination.PageNumberPaginationView.as_view(), name='pagination-page-number'),
    path('pagination/limit-offset', views.pagination.LimitOffsetPaginationView.as_view(), name='pagination-limit-offset'),
    path('pagination/cursor', views.pagination.CursorPaginationView.as_view(), name='pagination-cursor'),

    path('status/<int:code>', views.status.status_code, name='status-code'),

    path('views/query-params', views.views.query_params, name='views-query-params'),
    path('views/headers', views.views.headers, name='views-headers'),
    path('views/data', views.views.data, name='views-data'),
]
