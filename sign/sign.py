import hmac
import base64
from hashlib import sha256


def sign_data(data, secret):
    data = data.encode('utf8')
    secret = secret.encode('utf8')
    signature = base64.b64encode(hmac.new(secret, data, digestmod=sha256).digest())
    return signature.decode()


if __name__ == '__main__':
    # sd = 'abc=123&timestamp=1597854783'
    # sd = 'timestamp=1597854783'
    sd = 'address=0xd0ff839fe6f793073f04fa06fa6e02f11b057e53&timestamp=1597854783'
    ss = '123'
    print(sign_data(sd, ss))
