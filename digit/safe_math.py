from decimal import Decimal


def add(x, y) -> Decimal:
    x, y = Decimal(str(x)), Decimal(str(y))
    return x + y


def minus(x, y) -> Decimal:
    x, y = Decimal(str(x)), Decimal(str(y))
    return x - y


def multi(x, y) -> Decimal:
    x, y = Decimal(str(x)), Decimal(str(y))
    return x * y


def divided(x, y) -> Decimal:
    x, y = Decimal(str(x)), Decimal(str(y))
    return x / y


def e_calc(wei):
    return '1e{}'.format(wei)


if __name__ == '__main__':
    a = [1, '1', 1.1, 3, '5.6', 0.1]
    b = [0.1, '3', 1.3, 9, '5.6', 0.0000000000000000001]

    for x in a:
        for y in b:
            print("{} + {} = {}".format(x, y, add(x, y)))
            print("{} - {} = {}".format(x, y, minus(x, y)))
            print("{} * {} = {}".format(x, y, multi(x, y)))
            print("{} / {} = {}".format(x, y, divided(x, y)))
