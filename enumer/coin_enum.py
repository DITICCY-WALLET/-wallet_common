from enum import Enum, unique


@unique
class TxStatus(Enum):
    INVALID = 0
    VALID = 1
    UNKNOWN = 2


@unique
class TxTypeEum(Enum):
    # 充值
    DEPOSIT = 0
    # 提现
    WITHDRAW = 1
    # 归集
    COLLECTION = 2
    # 补充手续费
    EXTRA = 3
    # 用户地址向非归集地址归集
    ERROR = 9


@unique
class SendEnum(Enum):
    NOT_PUSH = 0
    PUSHED = 1
    NEEDLESS = 2
