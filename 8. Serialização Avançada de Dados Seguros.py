import pickle
import zlib
from typing import Any
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class AdvancedSecureSerializer:
    def __init__(self, master_password: str):
        self.master_password = master_password
        self.salt = os.urandom(16)
        self.key = self._derive_key()
        
    def _derive_key(self) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        
    def serialize(self, data: Any) -> bytes:
        serialized = pickle.dumps(data)
        compressed = zlib.compress(serialized)
        encrypted = Fernet(self.key).encrypt(compressed)
        return self.salt + encrypted
        
    def deserialize(self, data: bytes) -> Any:
        salt = data[:16]
        encrypted = data[16:]
        
        # Re-derive key using the stored salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        
        decrypted = Fernet(key).decrypt(encrypted)
        decompressed = zlib.decompress(decrypted)
        return pickle.loads(decompressed)

# Usage
serializer = AdvancedSecureSerializer('super-secret-master-password')
data = {'secret': 'confidential_info'}
serialized = serializer.serialize(data)
deserialized = serializer.deserialize(serialized)