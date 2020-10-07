from coin.coin_tools import Tx, TxReceipt, Block
from digit import digit
from enumer.coin_enum import TxStatusEnum


class EthereumResolver(object):
    TRANSFER_ABI = '0xa9059cbb'
    GET_BALANCE_ABI = '0x70a08231'
    ADDRESS_LENGTH = 40
    ADDRESS_FILL_LENGTH = 24
    ADDRESS_FULL_LENGTH = ADDRESS_LENGTH + ADDRESS_FILL_LENGTH
    TRANSFER_VALUE_LENGTH = 64
    DEFAULT_GAS = 100000
    # 15G
    DEFAULT_GAS_PRICE = 15 * 1000 * 1000 * 1000
    # ZERO ADDRESS
    ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

    @classmethod
    def get_transfer_body(cls, sender=None, receiver=None, gas: int = None, gas_price: int = None, value: int = 0,
                          contract=None) -> dict:
        if gas is None:
            gas = cls.DEFAULT_GAS
        if gas_price is None:
            gas_price = cls.DEFAULT_GAS_PRICE
        body = {
            "from": cls.get_address(sender),
            "to": cls.get_address(receiver),
            "value": cls.get_value(value) if contract is None else '0x0',
            "gas": digit.int_to_hex(gas),
            # K M G  -> 10G
            "gasPrice": digit.int_to_hex(gas_price),
        }
        if contract is not None:
            body['to'] = digit.add_0x(contract)
            body['data'] = cls.TRANSFER_ABI + cls.get_address(receiver, contract) + cls.get_value(value, contract)
        return body

    @classmethod
    def get_balance_body(cls, address, contract):
        return {
            "from": cls.get_address(cls.ZERO_ADDRESS),
            "to": cls.get_address(contract),
            "value": digit.int_to_hex(0),
            "gas": digit.int_to_hex(cls.DEFAULT_GAS),
            # K M G  -> 10G
            "gasPrice": digit.int_to_hex(cls.DEFAULT_GAS_PRICE),
            "data": cls.GET_BALANCE_ABI + cls.get_address(address, contract)
        }

    @classmethod
    def get_estimate_gas_body(cls, contract=None):
        return cls.get_transfer_body(None, None, 0, 0, 0, contract)

    @classmethod
    def get_address(cls, address=None, contract=None) -> str:
        """
        获取合适的地址, 若是合约类型, 则补全至合适的位数, 并且没有0x开头
        :param address: 地址
        :param contract: 合约地址
        :return: hex or hex not have ox
        """
        if address is not None:
            if contract is None:
                return digit.add_0x(address)
            return digit.del_0x(address).zfill(cls.ADDRESS_FULL_LENGTH)
        if contract is None:
            return digit.add_0x('0' * cls.ADDRESS_LENGTH)
        return '0' * cls.ADDRESS_FULL_LENGTH

    @classmethod
    def get_value(cls, value, contract=None) -> str:
        """
        获取合适的金额, 若是合约类型, 则补全至合适的位数, 并且没有0x开头
        :param value: 金额
        :param contract:
        :return: hex or hex not have ox
        """
        if contract is None:
            return digit.int_to_hex(value)
        real_value = digit.int_to_hex(value, has_0x=False)
        return real_value.zfill(cls.TRANSFER_VALUE_LENGTH)

    @classmethod
    def resolver_transaction(cls, tx):
        """
        只支持标准 erc20 与 eth交易, 其他交易暂时不支持
        :param tx:
        :return:
        """
        block_height = digit.hex_to_int(tx['blockNumber'])
        block_hash = tx['blockHash']
        tx_hash = tx['hash']
        sender = cls.get_address(tx['from'])
        receiver = cls.get_address(tx['to'])
        value = digit.hex_to_int(tx['value'])
        gas = digit.hex_to_int(tx['gas'])
        gas_price = digit.hex_to_int(tx['gasPrice'])
        nonce = digit.hex_to_int(tx['nonce'])
        status = TxStatusEnum.UNKNOWN.value
        data = None
        contract = None
        # 去掉开头 0x
        if tx['input'].startswith(cls.TRANSFER_ABI):
            _input = tx['input']
            data = _input
            contract = tx['to']
            abi_length = len(cls.TRANSFER_ABI)
            abi, address, amount = (_input[0:abi_length], _input[abi_length:abi_length + cls.ADDRESS_FULL_LENGTH],
                                    _input[abi_length + cls.ADDRESS_FULL_LENGTH:])
            receiver = cls.get_address(address[cls.ADDRESS_FILL_LENGTH:])
            value = digit.hex_to_int(amount)
        return Tx(block_height, block_hash, tx_hash, sender, receiver, value, gas, gas_price, nonce, data, contract,
                  status)

    @classmethod
    def resolver_receipt(cls, receipt):
        block_height = digit.hex_to_int(receipt['blockNumber'])
        block_hash = receipt['blockHash']
        tx_hash = receipt['transactionHash']
        sender = receipt['from']
        receiver = receipt['to']
        contract = receipt['contractAddress']
        status = digit.hex_to_int(receipt['status'])
        gas_used = digit.hex_to_int(receipt['gasUsed'])
        return TxReceipt(block_height, block_hash, tx_hash, sender, receiver, contract, status, gas_used)

    @classmethod
    def resolver_block(cls, block, detail=True):
        """不包含交易"""
        block_height = digit.hex_to_int(block['number'])
        block_hash = block['hash']
        block_time = digit.hex_to_int(block['timestamp'])
        if detail:
            transactions = [cls.resolver_transaction(tx) for tx in block['transactions']]
        else:
            transactions = []

        return Block(height=block_height, hash=block_hash, timestamp=block_time, transactions=transactions)


if __name__ == '__main__':
    tx_body = {
        "blockHash": "0x853f6eccdb5914876d951a371e37e1280d44456f51d63bf51b72d70669ff9cbf",
        "blockNumber": "0x5ed32e",
        "chainId": None,
        "condition": None,
        "creates": None,
        "from": "0x81b7e08f65bdf5648606c89998a9cc8164397647",
        "gas": "0x5208",
        "gasPrice": "0x3f62ae8d",
        "hash": "0xe78e0124cd0d744895ec95c2f9940325345a25a746de93190c90d9bfa6722560",
        "input": "0x",
        "nonce": "0x191caa0",
        "publicKey": "0xe5af5959ae17550b2fe7bac2cde9dbae548c25033bdf71da03edb5cadda34baad4d60d47f8051f2f056c3156f68f9972c77a43e93434e8281f35290f417c6df4",
        "r": "0x184a47065f14cfe075895a50af230a17feceb8b946f8be07a9110099a64b4453",
        "raw": "0xf86f840191caa0843f62ae8d82520894afabf50ca77558e7a83e9722726aa780d31b0c72880de0b6b3a7640000801ba0184a47065f14cfe075895a50af230a17feceb8b946f8be07a9110099a64b4453a018c1403562c30c2453d421c71f068de4ce1854e74dca26f5f5b90fb13e30c03c",
        "s": "0x18c1403562c30c2453d421c71f068de4ce1854e74dca26f5f5b90fb13e30c03c",
        "standardV": "0x0",
        "to": "0xafabf50ca77558e7a83e9722726aa780d31b0c72",
        "transactionIndex": "0x5",
        "v": "0x1b",
        "value": "0xde0b6b3a7640000"
    }
    tx_obj = EthereumResolver.resolver_transaction(tx_body)
    print(tx_obj)

    tx_receipt = {
            "blockHash": "0x853f6eccdb5914876d951a371e37e1280d44456f51d63bf51b72d70669ff9cbf",
            "blockNumber": "0x5ed32e",
            "contractAddress": None,
            "cumulativeGasUsed": "0x20f50c",
            "from": "0x81b7e08f65bdf5648606c89998a9cc8164397647",
            "gasUsed": "0x5208",
            "logs": [],
            "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "status": "0x1",
            "to": "0xafabf50ca77558e7a83e9722726aa780d31b0c72",
            "transactionHash": "0xe78e0124cd0d744895ec95c2f9940325345a25a746de93190c90d9bfa6722560",
            "transactionIndex": "0x5"
        }

    x = {
        "jsonrpc": "2.0",
        "result": {
            "blockHash": "0x6dfb37e78721f706d1759084dc174ee7da02be601fd110510361213b23bd0860",
            "blockNumber": "0x5f0d25",
            "contractAddress": None,
            "cumulativeGasUsed": "0xff36",
            "from": "0x0ab1884cd5369d012aba18c1d063d245379f2c36",
            "gasUsed": "0x971c",
            "logs": [
                {
                    "address": "0x09413b841d9e6db12081c33693f67addc5475fe7",
                    "blockHash": "0x6dfb37e78721f706d1759084dc174ee7da02be601fd110510361213b23bd0860",
                    "blockNumber": "0x5f0d25",
                    "data": "0x0000000000000000000000000000000000000000000000000000013049a4e000",
                    "logIndex": "0x0",
                    "removed": False,
                    "topics": [
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                        "0x0000000000000000000000000ab1884cd5369d012aba18c1d063d245379f2c36",
                        "0x000000000000000000000000d353721b4fa78a90b6c919bf63a113045bec8d90"
                    ],
                    "transactionHash": "0xcf13c31e274f7494d90ca996b26a64ce9e41b06c6a4cad6e37e2ddf04b81e47f",
                    "transactionIndex": "0x1",
                    "transactionLogIndex": "0x0",
                    "type": "mined"
                },
                {
                    "address": "0xd353721b4fa78a90b6c919bf63a113045bec8d90",
                    "blockHash": "0x6dfb37e78721f706d1759084dc174ee7da02be601fd110510361213b23bd0860",
                    "blockNumber": "0x5f0d25",
                    "data": "0x00000000000000000000000000000000000000000000000000000000007a6e41",
                    "logIndex": "0x1",
                    "removed": False,
                    "topics": [
                        "0xa11cc37ec8f8db79aef59d01f3d42e13c496890e54aec05fea0f354d0b7fd390"
                    ],
                    "transactionHash": "0xcf13c31e274f7494d90ca996b26a64ce9e41b06c6a4cad6e37e2ddf04b81e47f",
                    "transactionIndex": "0x1",
                    "transactionLogIndex": "0x1",
                    "type": "mined"
                },
                {
                    "address": "0xd353721b4fa78a90b6c919bf63a113045bec8d90",
                    "blockHash": "0x6dfb37e78721f706d1759084dc174ee7da02be601fd110510361213b23bd0860",
                    "blockNumber": "0x5f0d25",
                    "data": "0x00000000000000000000000000000000000000000000000000000000007a6e410000000000000000000000000000000000000000000000000000000000000008",
                    "logIndex": "0x2",
                    "removed": False,
                    "topics": [
                        "0xfcd24348f8b1763ef3460819c910d715cb77c0cbff8bb4ae45a392fc893f885c"
                    ],
                    "transactionHash": "0xcf13c31e274f7494d90ca996b26a64ce9e41b06c6a4cad6e37e2ddf04b81e47f",
                    "transactionIndex": "0x1",
                    "transactionLogIndex": "0x2",
                    "type": "mined"
                }
            ],
            "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000080000000000000800000000000000000000000000000000000000000000000800000008000000000000000040008000040000000000000000000000000000800000000000000000000000000000000000000000000000000000000000010000000000010000000000000000080000000000000000000000000000000000000004000000000000000030000000000000000000000000000000000000000000000040000000006000000000000000000000000800000000000000008000000000000000000008000000000000000000000000000000000000000000000000000000100",
            "status": "0x1",
            "to": "0xd353721b4fa78a90b6c919bf63a113045bec8d90",
            "transactionHash": "0xcf13c31e274f7494d90ca996b26a64ce9e41b06c6a4cad6e37e2ddf04b81e47f",
            "transactionIndex": "0x1"
        },
        "id": 3
    }

    print(EthereumResolver.get_transfer_body(sender='0x5c8d1a6e68dfd5a1b51c59c5de6749b939627404',
                                             receiver='0x5c8d1a6e68dfd5a1b51c59c5de6749b939627404',
                                             value=1000, contract='0xbed2d19d9551f6666c31ce2a72eb4533262d5dab'))
