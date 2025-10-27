import logging
import json
from typing import Dict, Any
import datetime
from dataclasses import dataclass
from enum import Enum
import hmac
import hashlib
import base64

class LogLevel(Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

@dataclass
class LogEntry:
    timestamp: datetime.datetime
    level: LogLevel
    message: str
    context: Dict[str, Any]
    signature: str

class AdvancedSecureLogger:
    def __init__(self, log_file: str, secret_key: str):
        self.logger = logging.getLogger('advanced_secure_logger')
        self.log_file = log_file
        self.secret_key = secret_key
        
    def _generate_signature(self, log_entry: LogEntry) -> str:
        log_data = json.dumps({
            'timestamp': log_entry.timestamp.isoformat(),
            'level': log_entry.level.value,
            'message': log_entry.message,
            'context': log_entry.context
        })
        
        return hmac.new(
            self.secret_key.encode(),
            log_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
    def log(self, level: LogLevel, message: str, context: Dict[str, Any] = None) -> None:
        entry = LogEntry(
            timestamp=datetime.datetime.now(),
            level=level,
            message=message,
            context=context or {},
            signature=''
        )
        
        entry.signature = self._generate_signature(entry)
        
        log_str = json.dumps({
            'timestamp': entry.timestamp.isoformat(),
            'level': entry.level.value,
            'message': entry.message,
            'context': entry.context,
            'signature': entry.signature
        })
        
        if level == LogLevel.ERROR or level == LogLevel.CRITICAL:
            print(log_str)
            
        with open(self.log_file, 'a') as f:
            f.write(log_str + '\n')
            
    def verify_log_entry(self, log_entry: LogEntry) -> bool:
        expected_signature = self._generate_signature(log_entry)
        return hmac.compare_digest(log_entry.signature, expected_signature)

# Usage
logger = AdvancedSecureLogger('app.log', 'secret-key-for-signing')
logger.log(LogLevel.INFO, 'Application started', {'version': '1.0'})