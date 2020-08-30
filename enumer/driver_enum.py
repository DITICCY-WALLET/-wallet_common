from enum import Enum, unique
from httplibs.coinrpc.ethrpc import EthereumRpc


@unique
class DriverEnum(Enum):
    EthereumRpc = EthereumRpc


