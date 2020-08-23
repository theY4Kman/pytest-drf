from django.urls import reverse

__all__ = ['url_for']


def url_for(viewname, *args, _urlconf=None, _current_app=None, **kwargs):
    """Build URI for a view, given args and kwargs

    This wrapper of Django's reverse allows view args and kwargs to be passed
    as positional and keyword args, instead of: `reverse(args=(), kwargs={})`

    >>> reverse('myview-detail', args=(1337,))
    '/myview/1337'
    >>> reverse('myview-detail', kwargs={'security_event_id' : 1337})
    '/myview/1337'

    >>> url_for('myview-detail', 1337)
    '/myview/1337'
    >>> url_for('myview-detail', security_event_id=1337)
    '/myview/1337'
    """
    return reverse(viewname,
                   urlconf=_urlconf,
                   current_app=_current_app,
                   args=args,
                   kwargs=kwargs)
