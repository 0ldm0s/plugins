# -*- coding: UTF-8 -*-
from typing import List
from mio.sys import redis_db


class FlaskCachingHelper(object):
    key_prefix: str
    flask_cache_prefix: str

    def __init__(self, key_prefix: str = "", flask_cache_prefix: str = "flask_cache_"):
        self.key_prefix = key_prefix
        self.flask_cache_prefix = flask_cache_prefix

    def redis_cached_delete(self, function_name: str, need_url_for: bool = True):
        search_key: str = f"{self.flask_cache_prefix}{self.key_prefix}*"
        if need_url_for:
            from flask import url_for
            function_name = url_for(function_name)
        keys: List[bytes] = redis_db.keys(search_key)
        for _key_ in keys:
            url_key: str = _key_.decode("UTF-8")
            if function_name in url_key:
                redis_db.delete(url_key)
