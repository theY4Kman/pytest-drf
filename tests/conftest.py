from pytest_djangoapp import configure_djangoapp_plugin

pytest_plugins = configure_djangoapp_plugin(
    app_name='tests',
    migrate=False,
    settings=dict(
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'rest_framework',
            'tests.testapp',
        ],
        ROOT_URLCONF='tests.testapp.urls',
        REST_FRAMEWORK={
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.AllowAny',
            ],
            'PAGE_SIZE': 100,
        },
    ),
)
