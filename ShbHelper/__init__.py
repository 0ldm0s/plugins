# -*- coding: UTF-8 -*-
import inspect
import orjson as json
from typing import Optional, Dict, Any, Tuple
from mio.util.Logs import LogHandler
from mio.util.Helper import get_now_microtime, md5, get_local_now, str2int
from plugins.ApiHelper import ApiHelper
from plugins.QuickCache import QuickCache


class ShbHelper:
    VERSION = '0.2'
    app_key: str
    secret: str
    api: ApiHelper
    cache: QuickCache
    __access_token: Optional[str] = None
    API_GET_ACCESS_TOKEN = "/service/auth/get_access_token"
    API_GET_TASK_DETAIL = "/service/task/get_task_taskNo"
    API_TOKEN_KEY = "shb:token"

    def __get_logger__(self, name: str) -> LogHandler:
        name = f"{self.__class__.__name__}.{name}"
        return LogHandler(name)

    def __init__(self, app_key: str, secret: str, access_token: Optional[str] = None):
        self.api: ApiHelper = ApiHelper(
            server="https://oapi.shb.ltd", headers={"Content-type": "application/json"})
        self.app_key = app_key
        self.secret = secret
        self.cache = QuickCache()
        if access_token is None:
            _, access_token = self.cache.cache(self.API_TOKEN_KEY)
        self.access_token = access_token

    @property
    def access_token(self) -> str:
        return self.__access_token

    @access_token.setter
    def access_token(self, access_token: str):
        self.__access_token = access_token

    def __sign__(self, ts: int):
        secret: str = f"{self.secret}_{ts}"
        return md5(secret)

    def get_token(self) -> Optional[Dict[str, Any]]:
        console_log: LogHandler = self.__get_logger__(inspect.stack()[0].function)
        if self.access_token is not None:
            console_log.info("读取缓存数据")
            return self.access_token
        timestamp = get_now_microtime(max_ms_lan=3, hours=8)
        args: Dict[str, Any] = {
            "appKey": self.app_key,
            "timestamp": timestamp,
            "verifyCode": self.__sign__(timestamp)
        }
        result = self.api.post(self.API_GET_ACCESS_TOKEN, args=args, post_json=True, output_json=True)
        try:
            data: Dict[str, Any] = json.loads(str(result))
            if data["errorCode"] != "0" or "data" not in data:
                console_log.error(data["message"])
                return None
        except Exception as e:
            console_log.error(e)
            return None
        token_data: Dict[str, Any] = data["data"]
        self.access_token = token_data["access_token"]
        # 计算时长
        expire_time: int = int(str2int(token_data["expire_time"]) / 1000)
        dt: int = get_local_now(hours=8)
        expire_time = expire_time - dt - 60  # 多冗余1分钟，避免翻车
        self.cache.cache(self.API_TOKEN_KEY, self.access_token, expiry=expire_time)
        console_log.debug("成功获取token")
        return self.access_token

    def get_task_detail(self, task_no: str) -> Tuple[Optional[Dict[str, Any]], str]:
        console_log: LogHandler = self.__get_logger__(inspect.stack()[0].function)
        error_msg: str
        access_token: Optional[str] = self.access_token
        if access_token is None:
            access_token = self.get_token()
        if access_token is None:
            error_msg = "获取token失败，请检查配置是否有误"
            console_log.error(error_msg)
            return None, error_msg
        console_log.info(f"正在请求[{task_no}]的数据")
        params = {
            "accessToken": access_token,
            "taskNo": task_no
        }
        result = self.api.get(self.API_GET_TASK_DETAIL, params, output_json=True)
        try:
            data: Dict[str, Any] = json.loads(str(result))
            if data["errorCode"] != "0" or "data" not in data:
                error_msg = data["message"]
                console_log.error(error_msg)
                return None, error_msg
            task_detail: Dict[str, Any] = data["data"]
            console_log.debug(task_detail)
            return task_detail, "ok"
        except Exception as e:
            error_msg = str(e)
            console_log.error(error_msg)
            return None, error_msg
