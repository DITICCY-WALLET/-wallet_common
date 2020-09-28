
class RequestError(Exception):
    pass


class JsonRpcError(Exception):
    def __init__(self, code=-32603, message="Internal Error"):
        self.code = code
        self.message = message

    def __repr__(self):
        return 'code: {} message: {}'.format(self.code, self.message)

    def __str__(self):
        return self.__repr__()


class RsaCryptoError(Exception):
    pass


class SyncError(Exception):
    pass


class PasswordError(Exception):
    pass
