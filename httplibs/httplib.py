import json
import logging
import re

import requests


class Http(object):
    _default_headers = dict()
    _default_basic_auth = None
    _default_is_pre_request = False
    _default_timeout = (60, 60)
    _default_is_json = False

    _CHECK_HOST = re.compile(
        r'httplibs[s]://.*?[/]|(?<![.\d])(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?![.\d])')

    def __init__(self, host, **kwargs):
        self._host = host
        self._headers = self._default_headers
        self._headers.update(kwargs.get('headers', {}))
        self._basic_auth = kwargs.get('auth', self._default_basic_auth)
        self._basic_auth_str = self._default_basic_auth and ''.join(self._basic_auth)
        self._is_pre_request = kwargs.get('is_pre_request', self._default_is_pre_request)
        self._timeout = kwargs.get('timeout', self._default_timeout)
        self._is_json = kwargs.get('is_json',  self._default_is_json)

        if self._is_json:
            self.set_header('content-type', 'application/json')

        self.logger = kwargs.get('logger', logging)

        self.logger.debug('host: {} header: {} auth:{} timeout: {}'.format(
            self._host, self._headers, self._basic_auth_str, self._timeout))

        self.session = requests.session

    def format_params(self, params):
        _data, _json = None, None
        if self._is_json:
            if not isinstance(params, (dict, list)):
                try:
                    _json = json.loads(params)
                except Exception:
                    _data = params
            else:
                _json = params
        else:
            if isinstance(params, (dict, list)):
                try:
                    _data = json.dumps(params)
                except Exception as e:
                    raise ValueError("参数无法转换为data请求数据, 请确认数据: {}".format(params))
            else:
                _data = params
        return _data, _json

    def _request(self, method, url, **kwargs):

        headers = kwargs.get('headers') or self.get_headers()
        auth = kwargs.get('auth') or self._basic_auth
        timeout = kwargs.get('auth') or self._timeout
        self.logger.debug('url: {} header: {} auth:{} timeout: {}'.format(
            url, self._headers, self._basic_auth_str, self._timeout))
        with self.session().request(method, url, headers=headers, auth=auth, timeout=timeout, **kwargs) as rsp:
            return rsp

    def get(self, url, params, **kwargs):
        method = 'GET'
        return self._request(method, url, params=params **kwargs)

    def post(self, url, params, **kwargs):
        method = 'POST'
        _data, _json = self.format_params(params)
        return self._request(method, url, data=_data, json=_json, **kwargs)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        _check_value = self._CHECK_HOST.match(value)
        if _check_value is not None:
            self._host = _check_value.string

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value: (tuple, int)):
        if isinstance(value, (tuple, int)):
            self._timeout = value

    def get_headers(self, key: str = None) -> (dict, str):
        if key is None:
            return self._headers
        return self._headers.get(key)

    def set_header(self, key: str, value: str):
        self._headers.update({key: value})

    def rm_header(self, key: str) -> str:
        return self._headers.pop(key)
