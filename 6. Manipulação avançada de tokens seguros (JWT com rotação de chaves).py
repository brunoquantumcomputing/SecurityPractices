import jwt
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from typing import Optional
import secrets

class TokenManager:
    def __init__(self, key_rotation_interval: int = 3600):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        self.key_rotation_interval = key_rotation_interval
        self.last_rotation_time = datetime.datetime.utcnow()
        
    def rotate_keys(self) -> None:
        if (datetime.datetime.utcnow() - self.last_rotation_time).total_seconds() > self.key_rotation_interval:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.public_key = self.private_key.public_key()
            self.last_rotation_time = datetime.datetime.utcnow()
            
    def create_token(self, user_id: int, expiry_minutes: int = 60) -> str:
        self.rotate_keys()
        
        payload = {
            'sub': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry_minutes),
            'iat': datetime.datetime.utcnow(),
            'jti': secrets.token_hex(16)  # Unique token identifier
        }
        return jwt.encode(payload, self.private_key, algorithm='RS256')
        
    def verify_token(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, self.public_key, algorithms=['RS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

# Usage
token_manager = TokenManager(key_rotation_interval=3600)
token = token_manager.create_token(user_id=123)
decoded = token_manager.verify_token(token)