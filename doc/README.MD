# wallet common 使用文档

wallet common 是集成给上层调用使用的一个 common 工具包.

## http

## jsonrpc
jsonrpc 包含版本
* jsonrpc version1
* jsonrpc version1

### jsonrpc v1
功能支持：
* 单条请求

### jsonrpc v2
* 单条请求: single_post
* 多条请求:
    * 相同命令多条请求：many_post
    * 不同命令多条请求：diff_post

#### 单条请求
_single_post(method, params=None, ignore_err=True)
method: str rpc 方法
params: [dict or str or list or ...]
ignore_err: bool

#### 多条请求
多条请求分为：
* 相同命令多条请求：many_post
* 不同命令多条请求：diff_post

请求条数以 params 的数量为参照, 若没有 params, 但有 method 时, 不发送请求.
所以, 请自备 None 来替换空参数

##### many_post
_many_post(method, params, ignore_err=True):
method: str rpc 方法
params: [[dict or str or list or ...], [dict or str or list or ...], ...]
ignore_err: bool

##### diff_post
method: [str rpc 方法, str rpc 方法, ...]
params: [[dict or str or list or ...], [dict or str or list or ...], ...]
ignore_err: bool
`注意`: method 数量要与 params 数据一致