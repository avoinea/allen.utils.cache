import logging
from zope.component import ComponentLookupError
from zope.component import getUtility
from lovely.memcached.interfaces import IMemcachedClient

logger = logging.getLogger('allen.utils.cache.ramcache')

def cache(method):
    """ Cache """
    def wrapper(self, *args, **kwargs):
        """ Original method """
        try:
            util = getUtility(IMemcachedClient)
        except ComponentLookupError, err:
            logger.exception(err)
            return method(self, *args, **kwargs)

        cache_key = getattr(self, 'etag', None)
        if not cache_key:
            return method(self, *args, **kwargs)

        content = util.query(cache_key)
        if content:
            logger.debug('From cache')
            return content

        logger.debug('From ZODB')
        content = method(self, *args, **kwargs)
        util.set(content, cache_key)
        return content
    return wrapper
