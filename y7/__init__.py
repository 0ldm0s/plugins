# -*- coding: UTF-8 -*-
import orjson
import inspect
import requests
from flask import Flask
from typing import Dict, Optional, Union, List, Tuple
from mio.util.Helper import get_local_now, str2int
from mio.util.Logs import LogHandler
from config import Redis_VideoAccessToken_Key, Redis_Video_Address_Key, VideoAppKey, \
    VideoSecret
from plugins.QuickCache import QuickCache


class y7(object):
    VERSION: str = "0.3"
    _current_app: Flask
    _qc: QuickCache

    def __get_logger__(self, name: str) -> LogHandler:
        name = "{}.{}".format(self.__class__.__name__, name)
        return LogHandler(name)

    def __init__(self, current_app: Flask):
        self._current_app = current_app
        self._qc = QuickCache(current_app=current_app)

    def __do_post__(
            self, url: str, args: Dict, headers: Optional[Dict] = None, post_json: bool = False,
            output_json: bool = False
    ) -> Optional[Union[str, Dict]]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        headers = {} if headers is None else headers
        try:
            if post_json:
                r = requests.post(url, json=args, verify=False, headers=headers, timeout=3)
            else:
                r = requests.post(url, data=args, verify=False, headers=headers, timeout=3)
            if not output_json:
                return r.text
            return r.json()
        except Exception as e:
            console_log.error(e)
            return None

    def __do_get__(
            self, url: str, args: Optional[Dict] = None, headers: Optional[Dict] = None,
            output_json: bool = False
    ) -> Optional[Union[str, Dict]]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        headers = {} if headers is None else headers
        args = {} if args is None else args
        try:
            r = requests.get(url, params=args, headers=headers, timeout=3)
            if not output_json:
                return r.text
            return r.json()
        except Exception as e:
            console_log.error(e)
            return None

    def __do_put__(
            self, url: str, args: Optional[Dict] = None, headers: Optional[Dict] = None,
            output_json: bool = False
    ) -> Optional[Union[str, Dict]]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        headers = {} if headers is None else headers
        args = {} if args is None else args
        try:
            r = requests.put(url, params=args, headers=headers, timeout=3)
            if not output_json:
                return r.text
            return r.json()
        except Exception as e:
            console_log.error(e)
            return None

    def __do_delete__(
            self, url: str, args: Optional[Dict] = None, headers: Optional[Dict] = None,
            output_json: bool = False
    ) -> Optional[Union[str, Dict]]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        headers = {} if headers is None else headers
        args = {} if args is None else args
        try:
            r = requests.delete(url, params=args, headers=headers, timeout=3)
            if not output_json:
                return r.text
            return r.json()
        except Exception as e:
            console_log.error(e)
            return None

    def do_get_token(self) -> Optional[str]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        access_token: Optional[str]
        _, access_token = self._qc.cache(Redis_VideoAccessToken_Key, is_pickle=False)
        if access_token is None:
            get_token: Optional[str] = self.__do_post__(
                "https://open.ys7.com/api/lapp/token/get",
                args={
                    "appKey": VideoAppKey,
                    "appSecret": VideoSecret
                }
            )
            if get_token is None:
                console_log.error("无法获取到远端的数据")
                return None
            remote_data: Dict = orjson.loads(get_token)
            if remote_data["code"] != "200":
                msg = "远端返回错误信息[{}]:{}".format(
                    remote_data["code"], remote_data["msg"])
                console_log.error(msg)
                return None
            access_token = remote_data["data"]["accessToken"]
            expire_time: int = str2int(remote_data["data"]["expireTime"])
            expire_time = int(expire_time / 1000)  # 转成秒
            dt: int = get_local_now(hours=8)
            expire_time = expire_time - dt
            if expire_time <= 0:
                expire_time = int(6 * 24 * 3600)
            self._qc.cache(
                Redis_VideoAccessToken_Key, value=access_token, expiry=expire_time,
                is_pickle=False)
        return access_token

    def do_get_url(
            self, device_serial: str, protocol: int = 2
    ) -> Optional[str]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        if len(device_serial) == 0:
            console_log.error("传了个空的device_serial?")
            return None
        video_url: Optional[str]
        rvak: str = Redis_Video_Address_Key.format(device_serial, protocol)
        _, video_url = self._qc.cache(rvak, is_pickle=False)
        if video_url is None:
            access_token: Optional[str] = self.do_get_token()
            if access_token is None:
                console_log.error("获取token失败！")
                return None
            get_url: Optional[str] = self.__do_post__(
                "https://open.ys7.com/api/lapp/v2/live/address/get",
                args={
                    "accessToken": access_token,
                    "deviceSerial": device_serial,
                    "protocol": protocol
                }
            )
            if get_url is None:
                console_log.error(f"[{device_serial}]无法获取到远端的数据")
                return None
            remote_data: Dict = orjson.loads(get_url)
            if remote_data["code"] != "200":
                msg = "[{}]远端返回错误信息[{}]:{}".format(
                    device_serial, remote_data["code"], remote_data["msg"])
                console_log.error(msg)
                return None
            video_url = remote_data["data"]["url"]
            expire_time: int = str2int(remote_data["data"]["expireTime"])
            expire_time = int(expire_time / 1000)  # 转成秒
            dt: int = get_local_now(hours=8)
            expire_time = expire_time - dt
            if expire_time <= 0:
                expire_time = int(6 * 24 * 3600)
            self._qc.cache(
                rvak, value=video_url, expiry=expire_time, is_pickle=False)
        return video_url

    def do_get_projects_list(self, page: int = 0, per_page: int = 10) -> Optional[List[Dict]]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        access_token: Optional[str] = self.do_get_token()
        if access_token is None:
            console_log.error("未能获取token")
            return None
        get_projects_list: Optional[str] = self.__do_get__(
            "https://open.ys7.com/api/open/cloud/v1/projects",
            args={
                "accessToken": access_token,
                "pageNumber": page,
                "pageSize": per_page,
            }
        )
        if get_projects_list is None:
            console_log.error(f"无法获取项目列表")
            return None
        remote_data: Dict = orjson.loads(get_projects_list)
        meta = remote_data["meta"]
        if meta["code"] != 200:
            msg = "远端返回错误信息[{}]:{}".format(meta["code"], meta["message"])
            console_log.error(msg)
            return None
        if "data" not in remote_data:
            console_log.error(f"返回非正常数据：{get_projects_list}")
            return None
        return remote_data["data"]

    def do_update_project(
            self, project_id: str, project_name: str, expire_days: int, storage_type: int
    ) -> Tuple[bool, str]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        access_token: Optional[str] = self.do_get_token()
        if access_token is None:
            console_log.error("未能获取token")
            return None
        update_project: Optional[str] = self.__do_put__(
            f"https://open.ys7.com/api/open/cloud/v1/project/{project_id}",
            args={
                "accessToken": access_token,
                "projectName": project_name,
                "expireDays": expire_days,
                "storageType": storage_type,
            }
        )
        if update_project is None:
            msg = f"无法获取项目[{project_id}]的详情"
            console_log.error(msg)
            return False, msg
        remote_data: Dict = orjson.loads(update_project)
        meta = remote_data["meta"]
        if meta["code"] != 200:
            msg = "远端返回错误信息[{}]:{}".format(meta["code"], meta["message"])
            console_log.error(msg)
            return False, msg
        return True, "Ok"

    def do_create_project(
            self, project_id: str, project_name: str, expire_days: int, storage_type: int
    ) -> Tuple[bool, str]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        access_token: Optional[str] = self.do_get_token()
        if access_token is None:
            console_log.error("未能获取token")
            return None
        create_project: Optional[str] = self.__do_post__(
            f"https://open.ys7.com/api/open/cloud/v1/project/{project_id}",
            args={
                "accessToken": access_token,
                "projectName": project_name,
                "expireDays": expire_days,
                "storageType": storage_type,
            }
        )
        if create_project is None:
            msg = f"无法创建项目[{project_id}]"
            console_log.error(msg)
            return False, msg
        remote_data: Dict = orjson.loads(create_project)
        meta = remote_data["meta"]
        if meta["code"] != 200:
            msg = "远端返回错误信息[{}]:{}".format(meta["code"], meta["message"])
            console_log.error(msg)
            return False, msg
        return True, "Ok"

    def do_del_project(self, project_id: str) -> Tuple[bool, str]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        access_token: Optional[str] = self.do_get_token()
        if access_token is None:
            console_log.error("未能获取token")
            return None
        create_project: Optional[str] = self.__do_delete__(
            f"https://open.ys7.com/api/open/cloud/v1/project/{project_id}",
            args={
                "accessToken": access_token,
            }
        )
        if create_project is None:
            msg = f"无法删除项目[{project_id}]"
            console_log.error(msg)
            return False, msg
        remote_data: Dict = orjson.loads(create_project)
        meta = remote_data["meta"]
        if meta["code"] != 200:
            msg = "远端返回错误信息[{}]:{}".format(meta["code"], meta["message"])
            console_log.error(msg)
            return False, msg
        return True, "Ok"

    def do_video_save(
            self, project_id: str, device_serial: str, start_time: str, end_time: str, file_id: str,
            channel_no: int = 1
    ) -> Optional[Dict]:
        # 文档地址：[https://open.ys7.com/help/357]
        # ! 注意：这个接口只是保存视频切片在云端，并不执行下载操作
        console_log = self.__get_logger__(inspect.stack()[0].function)
        if len(device_serial) == 0:
            console_log.error("传了个空的device_serial?")
            return None
        access_token: Optional[str] = self.do_get_token()
        if access_token is None:
            console_log.error(f"[{device_serial}]获取token失败！")
            return None
        video_save: Optional[str] = self.__do_post__(
            "https://open.ys7.com/api/open/cloud/v1/video/save",
            args={
                "accessToken": access_token,
                "channelNo": channel_no,
                "projectId": project_id,
                "deviceSerial": device_serial,
                "startTime": start_time,
                "endTime": end_time,
                "fileId": file_id,
                "recType": "cloud",
            }
        )
        if video_save is None:
            console_log.error(f"[{device_serial}]无法获取到远端的数据")
            return None
        remote_data: Dict = orjson.loads(video_save)
        meta = remote_data["meta"]
        if meta["code"] != 200:
            msg = "远端返回错误信息[{}]:{}".format(meta["code"], meta["message"])
            console_log.error(msg)
            return None
        if "data" not in remote_data:
            console_log.error(f"返回非正常数据：{video_save}")
            return None
        return remote_data["data"]

    def do_rec_video_save(
            self, project_id: str, device_serial: str, start_time: str, end_time: str,
    ) -> Optional[Dict]:
        # 文档地址：[https://open.ys7.com/help/1381]
        # ! 注意：这个接口只是保存视频切片在云端，并不执行下载操作
        console_log = self.__get_logger__(inspect.stack()[0].function)
        if len(device_serial) == 0:
            console_log.error("传了个空的device_serial?")
            return None
        access_token: Optional[str] = self.do_get_token()
        if access_token is None:
            console_log.error(f"[{device_serial}]获取token失败！")
            return None
        rec_video_save: Optional[str] = self.__do_post__(
            "https://open.ys7.com/api/open/cloud/v1/rec/video/save",
            headers={
                # "Content-Type": "application/x-www-form-urlencoded",
                "accessToken": access_token,
                "deviceSerial": device_serial,
            },
            args={
                "projectId": project_id,
                "startTime": start_time,
                "endTime": end_time,
                "recType": "cloud",
                "streamType": 1,
            }
        )
        if rec_video_save is None:
            console_log.error(f"[{device_serial}]无法获取到远端的数据")
            return None
        remote_data: Dict = orjson.loads(rec_video_save)
        meta = remote_data["meta"]
        if meta["code"] != 200:
            msg = "远端返回错误信息[{}]:{}".format(meta["code"], meta["message"])
            console_log.error(msg)
            return None
        if "data" not in remote_data:
            console_log.error(f"返回非正常数据：{rec_video_save}")
            return None
        return remote_data["data"]

    def do_instant_video_save(
            self, project_id: str, device_serial: str, record_seconds: int = 1800
    ) -> Optional[Dict]:
        # 文档地址：[https://open.ys7.com/help/1381]
        # ! 注意：这个接口只是保存视频切片在云端，并不执行下载操作
        console_log = self.__get_logger__(inspect.stack()[0].function)
        if len(device_serial) == 0:
            console_log.error("传了个空的device_serial?")
            return None
        access_token: Optional[str] = self.do_get_token()
        if access_token is None:
            console_log.error(f"[{device_serial}]获取token失败！")
            return None
        instant_video_save: Optional[str] = self.__do_post__(
            "https://open.ys7.com/api/open/cloud/v1/instant/record/save",
            headers={
                # "Content-Type": "application/x-www-form-urlencoded",
                "accessToken": access_token,
                "deviceSerial": device_serial,
            },
            args={
                "projectId": project_id,
                "recordSeconds": record_seconds,
            }
        )
        if instant_video_save is None:
            console_log.error(f"[{device_serial}]无法获取到远端的数据")
            return None
        remote_data: Dict = orjson.loads(instant_video_save)
        meta = remote_data["meta"]
        if meta["code"] != 200:
            msg = "远端返回错误信息[{}]:{}".format(meta["code"], meta["message"])
            console_log.error(msg)
            return None
        if "data" not in remote_data:
            console_log.error(f"返回非正常数据：{instant_video_save}")
            return None
        return remote_data["data"]

    def do_get_task_info(self, task_id: str) -> Optional[Dict]:
        # 文档地址：[https://open.ys7.com/help/1370]
        console_log = self.__get_logger__(inspect.stack()[0].function)
        if len(task_id) == 0:
            console_log.error("传了个空的task_id?")
            return None
        access_token: Optional[str] = self.do_get_token()
        if access_token is None:
            console_log.error(f"[{task_id}]获取token失败！")
            return None
        get_task_info: Optional[str] = self.__do_get__(
            f"https://open.ys7.com/api/v3/open/cloud/task/{task_id}",
            args={
                "accessToken": access_token,
            }
        )
        if get_task_info is None:
            console_log.error(f"[{task_id}]无法获取到远端的数据")
            return None
        remote_data: Dict = orjson.loads(get_task_info)
        meta = remote_data["meta"]
        if meta["code"] != 200:
            msg = "远端返回错误信息[{}]:{}".format(meta["code"], meta["message"])
            console_log.error(msg)
            return None
        if "data" not in remote_data:
            console_log.error(f"返回非正常数据：{get_task_info}")
            return None
        return remote_data["data"]

    def do_get_task_files_list(
            self, task_id: str, page: int = 0, per_page: int = 50
    ) -> Optional[Dict]:
        # 文档地址：[https://open.ys7.com/help/1373]
        console_log = self.__get_logger__(inspect.stack()[0].function)
        if len(task_id) == 0:
            console_log.error("传了个空的task_id?")
            return None
        access_token: Optional[str] = self.do_get_token()
        if access_token is None:
            console_log.error(f"[{task_id}]获取token失败！")
            return None
        get_task_files_list: Optional[str] = self.__do_get__(
            "https://open.ys7.com/api/v3/open/cloud/task/files",
            args={
                "accessToken": access_token,
                "taskId": task_id,
                "pageNumber": page,
                "pageSize": per_page,
                "hasUrl": True,
            }
        )
        if get_task_files_list is None:
            console_log.error(f"[{task_id}]无法获取到远端的数据")
            return None
        remote_data: Dict = orjson.loads(get_task_files_list)
        meta = remote_data["meta"]
        if meta["code"] != 200:
            msg = "远端返回错误信息[{}]:{}".format(meta["code"], meta["message"])
            console_log.error(msg)
            return None
        if "data" not in remote_data:
            console_log.error(f"返回非正常数据：{get_task_files_list}")
            return None
        return remote_data["data"]
