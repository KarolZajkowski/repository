from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class Decrypt:
    """ Password descriptor """
    def __init__(self):
        key = b"Karol Zajkowski kmz1989@gmail.com"
        salt = b"SALT"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        _key = base64.urlsafe_b64encode(kdf.derive(key))
        self.f = Fernet(_key)
        # print(_key)

    def encrypted_function(self, obj):
        """Object for encrypted - #write """
        message = obj.encode()
        # print("message", message)
        encrypted = self.f.encrypt(message)
        encrypted = encrypted.decode("utf-8")
        # print("encrypted", encrypted)
        return encrypted

    def decrypted(self, obj):
        """Object for decrypted - #read"""
        obj = obj.encode()
        decrypted = self.f.decrypt(obj)
        # print("decrypted", decrypted)
        decrypted = decrypted.decode("utf-8")
        return decrypted


if __name__ == '__main__':
    # Test
    decrypter = Decrypt()
    key = decrypter.encrypted_function("")
    secret = decrypter.encrypted_function("")
    # # print(key, secret)
    # start_trade.pickle_wride("..\\other\\key_enc", key)
    # start_trade.pickle_wride("..\\other\\secret_enc", secret)