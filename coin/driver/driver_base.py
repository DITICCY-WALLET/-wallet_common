from enumer.driver_enum import DriverEnum
from httplibs.coinrpc.ethrpc import EthereumRpc


class DriverBase(object):
    def __init__(self, rpc):
        self.rpc = rpc


class DriverFactory(object):
    drivers = {
        "ETHEREUM": EthereumRpc
    }

    def __new__(cls, coin: str, *args, **kwargs):
        driver = cls.drivers.get(coin.upper())
        if driver is not None:
            return driver(*args, **kwargs)
        raise ValueError('没有该RPC引擎')

