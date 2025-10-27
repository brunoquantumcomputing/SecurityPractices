from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator, ValidationError, conint, constr
from datetime import datetime
import re
from enum import Enum

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class EmailStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("Email must be a string")
            
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", value):
            raise ValueError("Invalid email format")
            
        return value

class PasswordStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("Password must be a string")
            
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
            
        if not re.search(r'[A-Z]', value):
            raise ValueError("Password must contain at least one uppercase letter")
            
        if not re.search(r'[a-z]', value):
            raise ValueError("Password must contain at least one lowercase letter")
            
        if not re.search(r'[0-9]', value):
            raise ValueError("Password must contain at least one digit")
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("Password must contain at least one special character")
            
        return value

class UserRegistration(BaseModel):
    username: constr(min_length=3, max_length=32, regex=r'^[a-zA-Z0-9_-]+$')
    email: EmailStr
    password: PasswordStr
    age: conint(gt=12, lt=120)
    roles: List[UserRole]
    metadata: Dict[str, Any]
    
    @validator('birthdate')
    def validate_birthdate(cls, value: datetime) -> datetime:
        now = datetime.now()
        age = now.year - value.year - ((now.month, now.day) < (value.month, value.day))
        
        if age < 13:
            raise ValueError("User must be at least 13 years old")
            
        return value
        
    @validator('roles')
    def validate_roles(cls, values: List[UserRole]) -> List[UserRole]:
        if UserRole.ADMIN in values and len(values) > 1:
            raise ValueError("Admin role cannot be combined with other roles")
            
        return values
        
    @validator('metadata')
    def validate_metadata(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        allowed_keys = {'bio', 'location', 'website', 'avatar_url'}
        
        for key in values.keys():
            if key not in allowed_keys:
                raise ValueError(f"Metadata key '{key}' is not allowed")
                
        return values

# Example usage
try:
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "SecureP@ssw0rd!",
        "age": 25,
        "roles": ["user"],
        "metadata": {
            "bio": "Software engineer",
            "location": "New York"
        }
    }
    
    user = UserRegistration(**user_data)
    print("Valid user registration:", user.dict())
    
except ValidationError as e:
    print("Validation error:", e.errors())