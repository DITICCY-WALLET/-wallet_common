from json import JSONDecodeError
import traceback

from exceptions import JsonRpcError
from httplibs.httplib import Http


class JsonRpcBatchMixin(object):
    def _many_post(self, method: str, params, ignore_err=True):

        def processor(data):
            """JSONRPC协议中, result与error互斥, 两者不可能同时拥有值."""
            results = [d.get('result') for d in data]
            if ignore_err:
                return results
            if not all(results):
                self.logger.debug('many post中返回数据错误: {}'.format(data))
                raise JsonRpcError(-1, "many post中返回数据中错误.")

        payload = [{'jsonrpc': "2.0", "id": next(self.get_id()),
                    'method': method, "params": self.right_params(p)} for p in params]
        return self._send_data(payload, processor)

    def _diff_post(self, methods: list, params: list, ignore_err=True):
        def processor(data):
            """JSONRPC协议中, result与error互斥, 两者不可能同时拥有值."""
            results = [d.get('result') for d in data]
            if ignore_err:
                return results
            if not all(results):
                self.logger.debug('many post中返回数据错误: {}'.format(data))
                raise JsonRpcError(-1, "many post中返回数据中错误.")

        payload = [{'jsonrpc': "2.0", "id": next(self.get_id()),
                    'method': methods[k], "params": self.right_params(p)} for k, p in enumerate(params)]
        return self._send_data(payload, processor)


class JsonRpcSingleMixin(object):
    def _single_post(self, method: str, params=None, ignore_err=True):
        """强制使用jsonrpc 2.0版本"""

        def processor(data):
            err = data.get('error')
            if not err:
                return data['result']
            if ignore_err:
                return data.get('result')
            raise JsonRpcError(code=err.get('code', -32603), message=err.get('message', ''))

        payload = {"jsonrpc": "2.0", "id": next(self.get_id()), "method": method,
                   "params": self.right_params(params)}
        return self._send_data(payload, processor)


class JsonRpcV1(Http, JsonRpcSingleMixin):
    __version = '1.0'
    _default_is_json = True

    def __init__(self, host, **kwargs):
        self._id = 0
        super().__init__(host, **kwargs)

    def get_id(self):
        _id = self._id
        self._id += 1
        yield _id

    def reset_id(self):
        self._id = 0

    def build_payload(self, method, params, id=None):
        _id = id or self._id
        return {"id": _id, 'method': method, 'params': params, 'jsonrpc': self.__version}

    def choice_post_func(self, params, diff=False):
        """
        选择一个合适的 post 方法, 主要用于 many_post 与 single_post 之间自动选择.
        :param params: 参数, 根据参数选择是 single 还是 many. 如果是 list||tuple 或
            list||tuple<list> 则为 many, 如果是 普通类型 则是single
        :param diff: 是否选择 diff 方法
        :return: single_post  v1 版本只有 single, 没有选择
        """
        return self._single_post

    @classmethod
    def get_params(cls, params, *args):
        """
        获取合适的参数, 不需要自己额外匹配是 single 请求或是 many 请求.
        :param params: 主要参数
        :param args: 额外参数
        :return: payload  v1 版本只能返回自己, 无法做多参数请求, 仅v2可以
        """
        return [params, *args]

    @classmethod
    def right_params(cls, p):
        if isinstance(p, (tuple, list)):
            return p
        if isinstance(p, (set,)):
            return list(p)
        if isinstance(p, (int, float, str, dict)):
            return [p]
        if p is None:
            return []
        return [p]

    def _send_data(self, params, processor):
        try:
            rsp = super().post(self.host, params=params)
            if self._is_json:
                try:
                    rsp_result = rsp.json()
                except JSONDecodeError as e:
                    self.logger.warning("rsp json decode error: {}".format(e))
                    rsp_result = rsp.text
            else:
                rsp_result = rsp.text
        except Exception as e:
            rsp_result = {'error': {"code": 0, "message": "不可预知的错误: {}".format(e)}}
            self.logger.warning(traceback.format_exc())
        result = processor(rsp_result)
        self.reset_id()
        return result


class JsonRpcV2(JsonRpcV1, JsonRpcBatchMixin):
    __version = '2.0'

    def choice_post_func(self, params, diff=False):
        """
        选择一个合适的 post 方法, 主要用于 many_post 与 single_post 之间自动选择.
        部分情况下该方法可能不适用, 要根据情况自己判断, 请注意.
        :param params: 参数, 根据参数选择是 single 还是 many. 如果是 list||tuple 或
            list||tuple<list> 则为 many, 如果是 普通类型 则是single
        :param diff: 是否选择 diff 方法
        :return: single_post || many_post || diff_post
        """
        if isinstance(params, (list, tuple)):
            func = self._many_post
        elif isinstance(params, int) and params > 1:
            func = self._many_post
        else:
            func = self._single_post
        if diff:
            func = self._diff_post

        return func

    @classmethod
    def get_params(cls, params, *args):
        if isinstance(params, (list, tuple, set, range)):
            payload = [[p, *args] for p in params]
        else:
            payload = [params, *args]
        return payload


if __name__ == '__main__':
    rpc = JsonRpcV2('http://192.168.10.201:37001')
    # rpc = JsonRpcV2('http://192.168.10.201:33601')
    print(rpc._many_post('1', '2'))
    print(rpc._single_post('1', '2'))
    print(rpc._diff_post('1', '2'))

