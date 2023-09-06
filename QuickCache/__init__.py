# -*- coding: utf-8 -*-
import os
import pickle
from flask import Flask
from typing import Optional, Any, Tuple, List
from mio.sys import redis_db
from mio.util.Logs import LogHandler
from mio.util.Helper import get_root_path, read_txt_file


class QuickCache(object):
    VERSION = "0.13"
    redis_key: str

    def __init__(self, current_app: Optional[Flask] = None):
        # 如果在cli下使用，则需要显式的传入app
        if current_app is None:
            from flask import current_app
        self.redis_key = current_app.config["REDIS_KEY_PREFIX"]

    def get_keys(self, key: str, is_full_key: bool = False) -> List[str]:
        console_log = LogHandler("QuickCache.get_keys")
        try:
            redis_key: str = f"{self.redis_key}:Cache:{key}" if not is_full_key else key
            keys: Optional[List[bytes]] = redis_db.keys(redis_key)
            return [str(key, encoding="utf-8") for key in keys]
        except Exception as e:
            console_log.error(e)
            return []

    def lpush(self, key: str, value: Optional[Any] = None, expiry: int = 0, is_full_key: bool = False) -> bool:
        console_log = LogHandler("QuickCache.lpush")
        if key is None or len(key) <= 0:
            return False
        redis_key: str = f"{self.redis_key}:Cache:{key}" if not is_full_key else key
        try:
            redis_db.lpush(redis_key, pickle.dumps(value))
            if expiry > 0:
                redis_db.expire(name=redis_key, time=expiry)
        except Exception as e:
            console_log.error(e)
            return False

    def llen(self, key: str, is_full_key: bool = False) -> int:
        console_log = LogHandler("QuickCache.llen")
        if key is None or len(key) <= 0:
            return 0
        redis_key: str = f"{self.redis_key}:Cache:{key}" if not is_full_key else key
        try:
            return redis_db.llen(redis_key)
        except Exception as e:
            console_log.error(e)
            return 0

    def inc_num(self, key: str, num: int = 1, is_full_key: bool = False) -> Optional[int]:
        console_log = LogHandler("QuickCache.inc_num")
        if key is None or len(key) <= 0:
            return None
        redis_key: str = f"{self.redis_key}:Cache:{key}" if not is_full_key else key
        try:
            item = redis_db.incr(redis_key, num)
            return item
        except Exception as e:
            console_log.error(e)
            return None

    def dec_num(self, key: str, num: int = 1, is_full_key: bool = False) -> Optional[int]:
        console_log = LogHandler("QuickCache.dec_num")
        if key is None or len(key) <= 0:
            return None
        redis_key: str = f"{self.redis_key}:Cache:{key}" if not is_full_key else key
        try:
            item = redis_db.decr(redis_key, num)
            return item
        except Exception as e:
            console_log.error(e)
            return None

    def rpop(self, key: str, is_full_key: bool = False) -> Optional[Any]:
        console_log = LogHandler("QuickCache.llen")
        if key is None or len(key) <= 0:
            return None
        redis_key: str = f"{self.redis_key}:Cache:{key}" if not is_full_key else key
        try:
            return pickle.loads(redis_db.rpop(redis_key))
        except Exception as e:
            console_log.error(e)
            return None

    def cache(
            self, key: str, value: Optional[Any] = None, expiry: int = 0, is_full_key: bool = False,
            is_pickle: bool = True
    ) -> Tuple[bool, Optional[Any]]:
        console_log = LogHandler("QuickCache.cache")
        if key is None or len(key) <= 0:
            return False, None
        redis_key: str = f"{self.redis_key}:Cache:{key}" if not is_full_key else key
        try:
            if value is None:
                # 读取
                val: Optional[bytes] = redis_db.get(redis_key)
                if val:
                    data: Any
                    if is_pickle:
                        data = pickle.loads(val)
                    else:
                        data = val.decode("utf-8")
                    return True, data
                return True, None
            else:
                # 写入
                val = value if not is_pickle else pickle.dumps(value)
                if expiry > 0:
                    redis_db.setex(redis_key, expiry, val)
                else:
                    redis_db.set(redis_key, val)
                return True, value
        except Exception as e:
            console_log.error(e)
            return False, None

    def remove_cache(self, key: str, is_full_key: bool = False):
        console_log = LogHandler("QuickCache.remove_cache")
        if key is None or len(key) <= 0:
            return
        redis_key: str = f"{self.redis_key}:Cache:{key}" if not is_full_key else key
        try:
            redis_db.delete(redis_key)
        except Exception as e:
            console_log.debug(e)

    def cache_page(
            self, key: str, template_filename: str, expiry: int = 3600, is_full_key: bool = False, **kwargs
    ) -> Optional[str]:
        from flask import render_template_string
        redis_key: str = f"{self.redis_key}:Page:Cache:{key}" if not is_full_key else key
        root_path: str = os.path.join(get_root_path(), "web", "template")
        template_filename = root_path + os.path.sep + template_filename
        if not os.path.isfile(template_filename):
            return None
        # 开始渲染
        text: str = read_txt_file(template_filename)
        text = render_template_string(text, **kwargs)
        self.cache(redis_key, text, expiry)
        return text

    def read_page(self, key: str, expiry: int = 3600, is_full_key: bool = False) -> Optional[str]:
        redis_key: str = f"{self.redis_key}:Page:Cache:{key}" if not is_full_key else key
        is_ok, text = self.cache(redis_key)
        if not is_ok or text is None:
            return None
        # 刷新缓存
        self.cache(redis_key, text, expiry)
        return text
