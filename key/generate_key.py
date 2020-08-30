import uuid
from sign.rsa import RsaCrypto


def generate_ack():
    return {"access_key": str(uuid.uuid4()), "secret_key": uuid.uuid4().hex}


def generate_rsa_key(bites=1024):
    rsa = RsaCrypto()
    rsa.generate_key(bites)
    return {"public_key": rsa.export_public_key(), "private_key": rsa.export_private_key()}


