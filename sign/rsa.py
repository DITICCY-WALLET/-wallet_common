import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP

from exceptions import RsaCryptoError


class RsaCrypto(object):
    def __init__(self, key_pair=None, private_key=None, public_key=None):
        self.key_pair = key_pair
        self.private_key = private_key
        self.public_key = public_key

    def import_key(self, private_key):
        self.key_pair = RSA.importKey(private_key)

    def import_public_key(self, public_key):
        self.public_key = public_key
        self._create_pri_pub_key()

    def _create_pri_pub_key(self):
        if self.key_pair is not None:
            self.private_key = self.key_pair.exportKey()
            self.public_key = self.key_pair.publickey()

    def generate_key(self, bits=1024):
        self.key_pair = RSA.generate(bits)
        self._create_pri_pub_key()

    def encrypt(self, message: bytes or str, is_base64=True) -> str:
        if isinstance(message, str):
            message = message.encode(encoding='utf-8')
        if self.public_key is None:
            if self.private_key is not None:
                self.import_key(self.private_key)
            else:
                raise RsaCryptoError('public is None, please import public before encrypt.')
        cipher = PKCS1_v1_5.new(self.public_key)
        sign_data = cipher.encrypt(message)
        if is_base64:
            return base64.b64encode(sign_data).decode(encoding='utf-8')
        return sign_data.decode(encoding='utf-8')

    def decrypt(self, encrypt_text: bytes or str, is_base64=True) -> str:
        if isinstance(encrypt_text, str):
            encrypt_text = encrypt_text.encode(encoding='utf-8')
        if self.key_pair is None:
            if self.private_key is not None:
                self.import_key(self.private_key)
            else:
                raise RsaCryptoError('private is None, please import private before decrypt.')
        cipher = PKCS1_v1_5.new(self.key_pair)
        if is_base64:
            encrypt_text = base64.b64decode(encrypt_text)
        return cipher.decrypt(encrypt_text, PKCS1_OAEP.PKCS1OAEP_Cipher).decode(encoding='utf-8')

    def export_public_key(self):
        return self.public_key.export_key()

    def export_private_key(self):
        return self.private_key


if __name__ == '__main__':
    msg = 'hello, world'
    cp = RsaCrypto()
    cp.generate_key()
    crypto_text = cp.encrypt(msg)
    print(crypto_text)
    text = cp.decrypt(crypto_text)
    print(text)
