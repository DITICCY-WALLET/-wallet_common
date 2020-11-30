from enum import Enum, unique


@unique
class DBStatusEnum(Enum):
    NO = 0
    YES = 1
    REMOVED = 2
    DELETED = 3


if __name__ == '__main__':
    print(DBStatusEnum.NO.value)
