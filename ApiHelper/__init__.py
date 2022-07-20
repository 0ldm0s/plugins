# -*- coding: utf-8 -*-
import inspect
import requests
from typing import Dict, Optional, Union, Any
from mio.util.Logs import LogHandler


class ApiHelper(object):
    VERSION = '0.8'
    headers: Dict[str, str] = {
        "User-Agent": "curl/7.79.1"
    }
    __server__: str
    verify_cert: bool

    def __get_logger__(self, name: str) -> LogHandler:
        name = f"{self.__class__.__name__}.{name}"
        return LogHandler(name)

    def __init__(
            self, server: str, headers: Optional[Dict[str, str]] = None, is_ds: bool = False, verify_cert: bool = True
    ):
        if is_ds:
            import requests_unixsocket
            requests_unixsocket.monkeypatch()
        self.__server__ = server
        if headers is not None and isinstance(headers, dict):
            self.headers.update(headers)
        self.verify_cert = verify_cert

    def get(
            self, url: str, params: Optional[Dict[str, Any]] = None, output_json: bool = False
    ) -> Optional[Union[str, Dict[str, Any]]]:
        logger = self.__get_logger__(inspect.stack()[0].function)
        try:
            url = f"{self.__server__}{url}"
            r = requests.get(url, params=params, headers=self.headers, verify=self.verify_cert)
            if not output_json:
                return r.text
            return r.json()
        except Exception as e:
            logger.error(e)
            return None

    def post(
            self, url: str, args: Dict[str, Any], params: Optional[Dict[str, Any]] = None, post_json: bool = False,
            output_json: bool = False
    ) -> Optional[Union[str, Dict[str, Any]]]:
        logger = self.__get_logger__(inspect.stack()[0].function)
        try:
            url = f"{self.__server__}{url}"
            if post_json:
                r = requests.post(url, params=params, json=args, verify=self.verify_cert, headers=self.headers)
            else:
                r = requests.post(url, params=params, data=args, verify=self.verify_cert, headers=self.headers)
            if not output_json:
                return r.text
            return r.json()
        except Exception as e:
            logger.error(e)
            return None
