import hashlib
import os


class Hash:
    def hash(target, salt=None):
        # bytes:
        #     salt: 16 bytes
        #     hashed_target: 32 bytes
        if salt is None:
            salt = os.urandom(16)
        hashed_target = hashlib.pbkdf2_hmac("sha256", target.encode(), salt, 100000)
        return salt.hex(), hashed_target.hex()
