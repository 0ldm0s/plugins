# PyMIO 插件

## 安装依赖

每个插件目录下均有一个`requirements.txt`文件，使用之前请确保已经安装了对应的依赖。绝大部分情况下是全平台通用的，但少部分插件因为有特殊的依赖，因此对某些特定的操作系统（例如wndows）可能会因为缺乏依赖而报错，这个时候请优先降级到3.7.x（一般建议是3.7.5）再进行尝试。

使用时，请统一放置在`plugins`目录下。

## 插件

### ApiHelper

这是一个用于快速编写访问远程api的插件（并非构建api的插件）。目前支持`get`和`post`两种方式，支持标准socket访问和unixsocket访问两种方式。

使用范例

```python
from flask import current_app

is_ds: bool = True
if current_app.config['ENV'] == 'production':
    server = "http+unix://%2Frun%2Febay-book-api%2Fpymio.sock"
else:
    is_ds = False
    server = "http://127.0.0.1:5050"

headers = {
    ....
}
args = {
    ....
}
api: ApiHelper = ApiHelper(server, headers=headers, is_ds=is_ds)
api_helper.post("/remote/api/path", args=args, post_json=True)
```

#### 函数方法

##### 初始化

| 名称    | 类型           | 备注                                              |
| ------- | -------------- | ------------------------------------------------- |
| server  | str            | 服务器地址，支持http/https和http+unix             |
| headers | Dict[str, str] | 访问时提交的header                                |
| is_ds   | bool           | 默认为False，当需要使用unixsocket时，需指定为True |

##### get方法

| 名称        | 类型 | 备注                            |
| ----------- | ---- | ------------------------------- |
| url         | str  | 远程api地址                     |
| output_json | bool | 是否输出为json对象，默认为False |

##### post方法

| 名称        | 类型           | 备注                                                         |
| ----------- | -------------- | ------------------------------------------------------------ |
| url         | str            | 远程api地址                                                  |
| args        | Dict[str, Any] | 要提交的数据，如果为json提交模式，则为raw数据，否则为post form |
| post_json   | bool           | 是否以json形式提交数据，默认为False                          |
| output_json | bool           | 是否输出为json对象，默认为False                              |

### QuickCache插件

具体请参阅[PyMio的文档](https://pymio-cookbook.readthedocs.io/zh_CN/latest/zh-cn/database.html#id15)，这里不再赘述。

### helium

`selenium`助手类，改编自同名的python包，使用方法基本一致。但是增加了一些新的特性。

#### renew_chromedriver函数

顾名思义，用于更新插件内chromedriver的版本，目前支持win32、linux64、mac64和mac64_m1这几种chromedriver。其中需要注意的是，linux下可能会缺乏对应chromium的版本，因此建议尽量使用google-chrome-stable。树莓派目前官方并未支持支持，因此只能使用系统自带的版本。

#### renew_msedgedriver函数

这是用于更新微软edge浏览器driver的函数，目前支持win64（暂时未检测windows的cpu类型），linux64和mac64（官方尚未支持m1），与线上稳定版保持一致。

#### get_rendered_source函数

这个函数用于获取渲染后的页面，这是针对某些前端框架特定的函数方法。

#### get_page_source函数

标准的获取源码的方式，只是直接映射出来，不需要先获取driver再读取。

#### get_page_text函数

这个函数用于输出纯文本内容（去掉所有的html标签）