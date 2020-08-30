from code_status import *


class ResponseObject(object):

    def __new__(cls, code, msg=None, data=None):
        cls.code = code
        cls.msg = msg
        cls.data = data
        return {'code': code, 'msg': msg, 'data': data}

    @classmethod
    def raise_sign_exception(cls, msg=None, data=None):
        if msg is None:
            return sign_exception
        result = sign_exception.copy()
        if msg is not None:
            result['msg'] = msg
        if data is not None:
            result['data'] = data
        return result

    @classmethod
    def raise_404_error(cls, msg=None, data=None):
        if msg is None:
            return not_found_error
        result = not_found_error.copy()
        if msg is not None:
            result['msg'] = msg
        if data is not None:
            result['data'] = data
        return result

    @classmethod
    def raise_args_error(cls, msg=None, data=None):
        if msg is None:
            return args_error
        result = args_error.copy()
        if msg is not None:
            result['msg'] = msg
        if data is not None:
            result['data'] = data
        return result

    @classmethod
    def error(cls, code=None, msg=None, data=None):
        result = error_msg.copy()
        if code is not None:
            result['code'] = code
        if msg is not None:
            result['msg'] = msg
        if data is not None:
            result['data'] = data

        return result

    @classmethod
    def raise_exception(cls, msg=None, data=None):

        result = not_catch_error.copy()
        if msg is not None:
            result['msg'] = msg
        if data is not None:
            result['data'] = data

        return result

    @classmethod
    def success(cls, msg=None, data=None):
        result = success_msg.copy()
        if msg is not None:
            result['msg'] = msg
        if data is not None:
            result['data'] = data
        return result
