import json
from digit import digit
from enumer.coin_enum import TxStatusEnum


class BlockHeight(object):
    def __init__(self, current_height, best_height):
        self._current_height = current_height
        self._highest_height = best_height

    def __str__(self):
        return 'current: {}, highest: {}'.format(self._current_height, self._highest_height)

    @property
    def current_height(self):
        return self._current_height

    @current_height.setter
    def current_height(self, height):
        if not isinstance(height, int):
            raise TypeError('height must be int')
        self._current_height = height

    @property
    def highest_height(self):
        return self._highest_height

    @highest_height.setter
    def highest_height(self, height):
        if not isinstance(height, int):
            raise TypeError('height must be int')
        self._highest_height = height

    def get_hex_current_height(self):
        return digit.int_to_hex(self._current_height)

    def get_hex_highest_height(self):
        return digit.int_to_hex(self._highest_height)

    def to_dict(self) -> dict:
        return {
            "currentHeight": self._current_height,
            "highestHeight": self._highest_height,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class Tx(object):
    def __init__(self, block_height, block_hash, tx_hash, sender, receiver, value, gas, gas_price, nonce, data,
                 contract, status=TxStatusEnum.UNKNOWN.value):
        self.block_height = block_height
        self.block_hash = block_hash
        self.tx_hash = tx_hash
        self.sender = sender
        self.receiver = receiver
        self.value = value
        self.gas = gas
        self.gas_price = gas_price
        self.nonce = nonce
        self.data = data
        self.contract = contract
        self.status = status


class TxReceipt(object):
    def __init__(self, block_height, block_hash, tx_hash, sender, receiver, contract, status, gas_used):
        self.block_height = block_height
        self.block_hash = block_hash
        self.tx_hash = tx_hash
        self.sender = sender
        self.receiver = receiver
        self.contract = contract
        self.status = status
        self.gas_used = gas_used


class Block(object):
    def __init__(self, height, hash, timestamp, transactions):
        self.height = height
        self.hash = hash
        self.timestamp = timestamp
        self.transactions = transactions


if __name__ == '__main__':
    bh = BlockHeight(1, 5)
    print(bh.get_hex_current_height())
    print(bh.get_hex_highest_height())
    print(bh.current_height)
    print(bh.highest_height)
    bh.current_height = 2
    bh.highest_height = 10
    print(bh.current_height)
    print(bh.highest_height)
