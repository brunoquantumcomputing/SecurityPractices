import os
from typing import Dict, Any
import yaml
from pathlib import Path
import hashlib
from dataclasses import dataclass
from enum import Enum

class ConfigType(Enum):
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'

@dataclass
class AppConfig:
    database_url: str
    secret_key: str
    api_endpoints: Dict[str, str]
    log_level: str
    max_connections: int
    timeout: int

class ConfigManager:
    def __init__(self, config_dir: Path, config_type: ConfigType):
        self.config_dir = config_dir
        self.config_type = config_type
        self.config = self._load_config()
        
    def _load_config(self) -> AppConfig:
        config_file = self.config_dir / f"{self.config_type.value}.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
            
        with open(config_file, 'r') as f:
            raw_config = yaml.safe_load(f)
            
        # Validate config
        if not all(k in raw_config for k in [
            'database_url', 'secret_key', 'api_endpoints',
            'log_level', 'max_connections', 'timeout'
        ]):
            raise ValueError("Invalid config format")
            
        return AppConfig(
            database_url=raw_config['database_url'],
            secret_key=raw_config['secret_key'],
            api_endpoints=raw_config['api_endpoints'],
            log_level=raw_config['log_level'],
            max_connections=raw_config['max_connections'],
            timeout=raw_config['timeout']
        )
        
    def get_database_url(self) -> str:
        return self.config.database_url
        
    def get_secret_key(self) -> str:
        return self.config.secret_key
        
    def get_api_endpoint(self, name: str) -> Optional[str]:
        return self.config.api_endpoints.get(name)
        
    def get_log_level(self) -> str:
        return self.config.log_level
        
    def get_max_connections(self) -> int:
        return self.config.max_connections
        
    def get_timeout(self) -> int:
        return self.config.timeout
        
    def reload(self) -> None:
        self.config = self._load_config()

# Usage
config_manager = ConfigManager(Path('configs'), ConfigType.PRODUCTION)
db_url = config_manager.get_database_url()