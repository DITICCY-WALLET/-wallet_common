from abc import ABCMeta, abstractmethod

from coin.coin_tools import BlockHeight
from coin.resolver.eth_resolver import EthereumResolver
from digit import digit
from exceptions import JsonRpcError
from httplibs.jsonrpc import JsonRpcV2


class RpcBase(metaclass=ABCMeta):
    @abstractmethod
    def get_block_height(self):
        pass

    @abstractmethod
    def get_block_by_number(self, block_height, details=True):
        pass

    @abstractmethod
    def get_block_by_hash(self, block_hash, details=True):
        pass

    @abstractmethod
    def get_transaction_by_hash(self, tx_hash, details=True):
        pass

    @abstractmethod
    def get_transactions(self, count, offset):
        pass

    @abstractmethod
    def unlock_wallet(self) -> bool:
        pass

    @abstractmethod
    def open_wallet(self, passphrase, timeout=60, address=None) -> bool:
        pass

    @abstractmethod
    def send_transaction(self, sender, receiver, value, passphrase, gas=None, gas_price=None, fee=None, contract=None, comment=None, **kwargs):
        pass

    @abstractmethod
    def send_raw_transaction(self, raw):
        pass

    @abstractmethod
    def new_address(self, passphrase, count=1) -> str or list:
        pass

    @abstractmethod
    def get_balance(self, address, contract=None, block_height="latest"):
        pass

    @abstractmethod
    def get_wallet_balance(self, contract=None, block_height='latest', *, exclude=None):
        pass

    @abstractmethod
    def get_smart_fee(self, confirm_height=6, contract=None):
        pass

    @abstractmethod
    def gas_price(self):
        """仅 ETH 类实现该方法"""
        pass


class EthereumRpcBase(RpcBase, JsonRpcV2):
    def get_block_height(self):
        sync_method = 'eth_syncing'
        number_method = 'eth_blockNumber'
        sync, number = self._diff_post([sync_method, number_method], [None, None])
        if sync:
            block_height = BlockHeight(digit.hex_to_int(sync['currentBlock']), digit.hex_to_int(sync['highestBlock']))
        elif number:
            block_height = BlockHeight(digit.hex_to_int(number), digit.hex_to_int(number))
        else:
            self.logger.error('get_block_height 请求, 两个方式均未获取到正常拿. sync: {} number: {}'.format(sync, number))
            raise JsonRpcError(code=1,
                               message='get_block_height 请求, 两个方式均未获取到正常拿. sync: {} number: {}'
                               .format(sync, number))
        return block_height

    def get_block_by_hash(self, block_hash: str or list, details=True):
        """
        根据 block hash 获取一个或多个块
        :param block_hash: str or list
        :param details: 是否获取区块详情
        :return:
        """
        method = 'eth_getBlockByHash'
        func = self.choice_post_func(block_hash)
        return func(method, params=self.get_params(block_hash, details))

    def get_block_by_number(self, block_height, details=True):
        method = 'eth_getBlockByNumber'
        func = self.choice_post_func(block_height)
        return func(method, params=self.get_params(block_height, details))

    def get_transaction_by_hash(self, tx_hash, details=True):
        """
        details 表示是否获取收据, 可以一次获取很多个, 但如果结果会是 [tx, tx, tx, receipt, receipt, receipt ...]
        位置是固定不变的, 前半为 tx, 后半为 receipt. 请注意！！！
        :param tx_hash: tx hash
        :param details: receipt
        :return:
        """
        func = self.choice_post_func(tx_hash, details)
        tx_method = 'eth_getTransactionByHash'
        method = tx_method
        params = tx_hash
        if details:
            find_length = len(tx_hash) if isinstance(tx_hash, (list, set, tuple)) else 1
            method = [method] * find_length
            # method *= len(tx_hash)
            receipt_method = 'eth_getTransactionReceipt'
            method.extend([receipt_method] * find_length)
            method = method * find_length
            params = [tx_hash] * 2 if find_length <= 1 else tx_hash * 2
        return func(method, self.get_params(params))

    def get_transaction_receipt(self, tx_hash):
        func = self.choice_post_func(tx_hash)
        method = 'eth_getTransactionReceipt'
        return func(method, self.get_params(tx_hash))

    def get_transactions(self, count, offset=True):
        """
        这个方法是为了兼容比特币的, 所以这个方法在 eth 中 count 改为 tx_hash, offset 改为 details
        然后请求：get_transaction_by_hash
        :param count: mock tx_hash
        :param offset: mock details
        :return:
        """
        return self.get_transaction_by_hash(count, offset)

    def unlock_wallet(self) -> bool:
        return True

    def open_wallet(self, passphrase, timeout=None, address=None) -> bool:
        """暂时这里的 timeout 参数不使用, 使用后解锁会失败"""
        method = 'personal_unlockAccount'
        result = self._single_post(method, [address, passphrase, None])
        if result:
            return True
        return False

    def send_transaction(self, sender: str, receiver: str, value: int, passphrase: str, gas: int = None,
                         gas_price: int = None, fee: int = None,
                         contract: str = None, comment: str = None, **kwargs):
        """目前只支持单交易发送, 暂时没有想到更好的数据结构"""
        method = 'personal_signAndSendTransaction'
        if gas is None:
            gas = 21000
        if gas_price is None:
            gas_price = digit.hex_to_int(self.gas_price())
        params = EthereumResolver.get_transfer_body(sender, receiver, int(gas), int(gas_price), value, contract)
        payload = self.get_params(params, passphrase)
        return self._single_post(method, payload, ignore_err=False)

    def new_address(self, passphrase, count=1):
        method = 'personal_newAccount'
        func = self.choice_post_func(count)
        addresses = func(method, [passphrase] if count <= 1 else [passphrase] * count)
        self.logger.info('生成地址 {} 个, 结果为：{}'.format(count, addresses))
        return addresses

    def get_balance(self, address, contract=None, block_height='latest'):
        eth_method = 'eth_getBalance'
        contract_method = 'eth_call'
        func = self.choice_post_func(address)
        if contract is None:
            method = eth_method
            params = self.get_params(address, block_height)
        else:
            method = contract_method
            if isinstance(address, (list, tuple, set)):
                address = [EthereumResolver.get_balance_body(address=addr, contract=contract) for addr in address]
            else:
                address = EthereumResolver.get_balance_body(address=address, contract=contract)
            params = self.get_params(address, block_height)
        balance = func(method, params)
        return balance

    def personal_list_accounts(self):
        method = "personal_listAccounts"
        return self._single_post(method)

    def get_wallet_balance(self, contract=None, block_height='latest', *, exclude: list = None):
        if exclude is None:
            exclude = set()
        else:
            exclude = set(exclude)
        addresses = self.personal_list_accounts()
        if isinstance(addresses, list):
            addresses = set(addresses)
        else:
            self.logger.warning("personal_listAccounts address list not is list, it's {}".format(addresses))
            return 0
        check_addresses = list((exclude ^ addresses) & addresses)
        balance = 0
        offset = 100
        for s in range(0, len(check_addresses), offset):
            batch_address = check_addresses[s:s + offset]
            balances = self.get_balance(batch_address, contract, block_height)
            for _ in balances:
                if _:
                    balance += digit.hex_to_int(_)
                else:
                    self.logger.error("地址获取余额错误： {}".format(_))
        return balance

    def get_smart_fee(self, confirm_height="latest",  contract=None):
        method = 'eth_estimateGas'
        if contract is None:
            return digit.int_to_hex(21000)
        payload = EthereumResolver.get_transfer_body(contract=contract)
        return self._single_post(method, payload)

    def gas_price(self):
        return self._single_post("eth_gasPrice")

    def send_raw_transaction(self, raw):
        method = 'eth_sendRawTransaction'
        func = self.choice_post_func(raw)
        return func(method, self.get_params(raw))


if __name__ == '__main__':
    import json
    rpc = EthereumRpcBase('http://192.168.10.201:37001')
    # print(rpc.get_block_height())
    # print(rpc.get_block_by_hash('0x1a2f'))
    # print(rpc.get_block_by_hash(['0x1a2f', '0x9878']))
    # print(rpc.get_transaction_by_hash(['0x529bad6226fa1c843ea2b8cf70a2e4eaf95098783a3ee575994c87a6b726cb37',
    #                                    "0xcf13c31e274f7494d90ca996b26a64ce9e41b06c6a4cad6e37e2ddf04b81e47f"]))
    #
    # print(rpc.get_transaction_by_hash('0x529bad6226fa1c843ea2b8cf70a2e4eaf95098783a3ee575994c87a6b726cb37'))
    # print(rpc.get_transaction_by_hash('0x529bad6226fa1c843ea2b8cf70a2e4eaf95098783a3ee575994c87a6b726cb37',
    #                                   details=False))
    # print(rpc.get_transaction_receipt('0x529bad6226fa1c843ea2b8cf70a2e4eaf95098783a3ee575994c87a6b726cb37'))
    # print(rpc.get_transaction_receipt(['0x529bad6226fa1c843ea2b8cf70a2e4eaf95098783a3ee575994c87a6b726cb37',
    #                                    "0xcf13c31e274f7494d90ca996b26a64ce9e41b06c6a4cad6e37e2ddf04b81e47f"]))

    # print(rpc.get_wallet_balance())

    blocks = rpc.get_block_by_number([digit.int_to_hex(height) for height in range(5000000, 5000010)])
    print(json.dumps(blocks))
