# -*- coding: utf-8 -*-
import inspect
import requests
from typing import Dict, Optional, Union, Any
from mio.util.Logs import LogHandler


class ApiHelper(object):
    VERSION = '0.6'
    headers: Optional[Dict[str, str]] = None
    __server__: str

    def __get_logger__(self, name: str) -> LogHandler:
        name = '{}.{}'.format(self.__class__.__name__, name)
        return LogHandler(name)

    def __init__(self, server: str, headers: Optional[Dict[str, str]] = None, is_ds: bool = False):
        if is_ds:
            import requests_unixsocket
            requests_unixsocket.monkeypatch()
        self.__server__ = server
        self.headers = headers

    def get(self, url: str, output_json: bool = False) -> Optional[Union[str, Dict[str, Any]]]:
        logger = self.__get_logger__(inspect.stack()[0].function)
        try:
            url = f"{self.__server__}{url}"
            r = requests.get(url, headers=self.headers)
            if not output_json:
                return r.text
            return r.json()
        except Exception as e:
            logger.error(e)
            return None

    def post(
            self, url: str, args: Dict[str, Any], post_json: bool = False, output_json: bool = False
    ) -> Optional[Union[str, Dict[str, Any]]]:
        logger = self.__get_logger__(inspect.stack()[0].function)
        try:
            url = f"{self.__server__}{url}"
            if post_json:
                r = requests.post(url, json=args, verify=False, headers=self.headers)
            else:
                r = requests.post(url, data=args, verify=False, headers=self.headers)
            if not output_json:
                return r.text
            return r.json()
        except Exception as e:
            logger.error(e)
            return None
