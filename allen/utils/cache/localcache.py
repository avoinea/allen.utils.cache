""" Client cache
"""
import logging
from datetime import datetime
from base64 import encodestring
logger = logging.getLogger('allen.utils.cache.localcache')

def etag(etag_string):
    """ Make etag
    """
    text = encodestring(etag_string)
    text = text.split('\n')
    return text[0]

def cache(method):
    def wrapper(self, *args, **kwargs):
        context = self.context
        request = self.request

        etag_string = getattr(self, 'etag', '')
        if not etag_string:
            request.response.setStatus(200)
            return method(self, *args, **kwargs)

        if isinstance(etag_string, datetime):
            etag_string = etag_string.isoformat().split('.')[0]

        if not isinstance(etag_string, (unicode, str)):
            request.response.setStatus(200)
            return method(self, *args, **kwargs)

        context_etag = etag(etag_string)
        request_etag = request.getHeader('If-None-Match', '')
        request_etag = request_etag.replace('-gzip', '', 1)

        logger.info('%s - %s', context_etag, request_etag)
        if request_etag == context_etag:
            request.response.setStatus(304)
            return ''

        request.response.setHeader('etag', context_etag)
        request.response.setStatus(200)
        return method(self, *args, **kwargs)
    return wrapper
