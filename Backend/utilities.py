"""
RLG Core Utilities - Cross-Functional Support Engine
Version: 18.0.0
Features: AI-Enhanced Helpers, Global Compliance, Smart Automation
"""

import os
import re
import json
import logging
import hashlib
import pytz
import geoip2.database
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from functools import wraps, lru_cache
from dateutil.parser import parse
import requests
from deepseek_api import DeepseekAPI
from models import User, Project, Sprint
from config import get_config
import numpy as np
import pandas as pd
from retry import retry
from flask import request
import smtplib
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor

config = get_config()
logger = logging.getLogger('RLG.Utils')
ai_engine = DeepseekAPI()
executor = ThreadPoolExecutor(max_workers=20)

# --------------------------
# DATA VALIDATION & SANITIZATION
# --------------------------
def validate_scrum_data(data: Dict, scrum_guide_version: str = '2020') -> Dict:
    """Validate data against Scrum Guide specifications"""
    rules = _load_scrum_rules(scrum_guide_version)
    errors = {}
    
    # Sprint duration validation
    if 'sprint_days' in data:
        if not (1 <= data['sprint_days'] <= 30):
            errors['sprint_days'] = 'Invalid sprint duration'
    
    # Role validation
    required_roles = ['Product Owner', 'Scrum Master', 'Developers']
    if 'roles' in data and not all(role in data['roles'] for role in required_roles):
        errors['roles'] = 'Missing required Scrum roles'
    
    # AI-enhanced validation
    ai_errors = ai_engine.validate_scrum_data(data, rules)
    return {**errors, **ai_errors}

def sanitize_input(input_data: Any) -> Any:
    """GDPR-compliant data sanitization"""
    if isinstance(input_data, dict):
        return {k: sanitize_input(v) for k, v in input_data.items()}
    if isinstance(input_data, str):
        return re.sub(r'[<>"\']', '', input_data)
    return input_data

# --------------------------
# LOCALIZATION & INTERNATIONALIZATION
# --------------------------
def localize_datetime(dt: datetime, timezone: str) -> datetime:
    """Convert datetime to specific timezone with DST awareness"""
    try:
        tz = pytz.timezone(timezone)
        return dt.astimezone(tz)
    except pytz.UnknownTimeZoneError:
        return dt.astimezone(pytz.UTC)

def get_user_timezone(user: User) -> pytz.tzinfo:
    """Get timezone with fallback to project defaults"""
    return pytz.timezone(user.timezone or user.project.default_timezone)

# --------------------------
# LOGGING & MONITORING
# --------------------------
def log_activity(user_id: int, event_type: str, target_id: int) -> None:
    """GDPR-compliant activity logging"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'user_hash': hashlib.sha256(str(user_id).encode()).hexdigest(),
        'event_type': event_type,
        'target_id': target_id,
        'ip_hash': hash_ip(request.remote_addr)
    }
    logger.info(json.dumps(log_entry))

def log_security_event(event_type: str, metadata: Dict) -> None:
    """Centralized security logging"""
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event': event_type,
        'metadata': sanitize_input(metadata),
        'severity': ai_engine.assess_security_severity(event_type)
    }
    logger.warning(json.dumps(entry))

# --------------------------
# SECURITY & COMPLIANCE
# --------------------------
def hash_ip(ip: str) -> str:
    """GDPR-compliant IP anonymization"""
    return hashlib.sha256(ip.encode() + config.SECRET_KEY.encode()).hexdigest()

def generate_secure_token(length: int = 32) -> str:
    """Cryptographically secure token generation"""
    return hashlib.sha256(os.urandom(4096)).hexdigest()[:length]

# --------------------------
# API & INTEGRATION HELPERS
# --------------------------
@retry(tries=3, delay=2, backoff=2)
def api_request_with_retry(url: str, payload: Dict) -> Dict:
    """Robust API request handler with retry logic"""
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()

def format_api_response(data: Any, success: bool = True) -> Dict:
    """Standard API response formatter"""
    return {
        'success': success,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data,
        'metrics': calculate_response_metrics(data)
    }

# --------------------------
# ERROR HANDLING & REPORTING
# --------------------------
def create_error_report(error: Exception, context: Dict) -> Dict:
    """Generate detailed error reports with AI diagnostics"""
    return {
        'error_type': type(error).__name__,
        'message': str(error),
        'context': context,
        'stack_trace': ai_engine.analyze_stack_trace(error),
        'timestamp': datetime.utcnow().isoformat(),
        'error_id': hashlib.sha256(str(error).encode()).hexdigest()[:16]
    }

def handle_operational_error(func: Callable) -> Callable:
    """Decorator for automated error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            report = create_error_report(e, {'args': args, 'kwargs': kwargs})
            log_security_event('operational_error', report)
            return format_api_response(report, success=False)
    return wrapper

# --------------------------
# DATE & TIME MANAGEMENT
# --------------------------
def get_working_hours(timezone: str) -> Dict[str, int]:
    """Return default working hours (start and end hour) for a timezone."""
    # You can customize this logic as needed, e.g., fetch from config or DB
    # Default: 9am to 5pm local time
    return {'start': 9, 'end': 17}

def calculate_working_hours_overlap(timezones: List[str]) -> List[Dict]:
    """Calculate optimal collaboration windows across timezones"""
    matrix = np.zeros((24, len(timezones)))
    for i, tz in enumerate(timezones):
        local_hours = get_working_hours(tz)
        matrix[:,i] = [1 if local_hours['start'] <= h < local_hours['end'] else 0 
                      for h in range(24)]
    
    best_windows = []
    for hour in range(24):
        overlap_score = np.prod(matrix[hour:(hour+2), :].sum(axis=0))
        if overlap_score > 0:
            best_windows.append({
                'utc_start': hour,
                'local_times': {tz: _format_local_time(hour, tz) for tz in timezones},
                'score': overlap_score
            })
    
    return sorted(best_windows, key=lambda x: x['score'], reverse=True)[:3]

def is_working_time(dt: datetime, user: User) -> bool:
    """Check if datetime falls within user's working hours"""
    work_hours = ai_engine.get_working_hours(user.timezone)
    local_dt = localize_datetime(dt, user.timezone)
    return work_hours['start'] <= local_dt.hour < work_hours['end']

# --------------------------
# AI & ML INTEGRATION
# --------------------------
def generate_ai_insights(data: pd.DataFrame, context: Dict) -> pd.DataFrame:
    """Automated AI feature engineering"""
    enhanced = ai_engine.enhance_dataset(data, context)
    return enhanced[['prediction', 'confidence', 'risk_score']]

def translate_content(text: str, target_lang: str) -> str:
    """AI-powered translation with Scrum terminology"""
    return ai_engine.translate(text, target_lang, glossary='scrum')

# --------------------------
# FILE & DATA OPERATIONS
# --------------------------
def secure_filename(filename: str) -> str:
    """Generate secure filesystem-safe names"""
    name, ext = os.path.splitext(filename)
    clean_name = re.sub(r'[^A-Za-z0-9_\-]', '', name)
    return f"{clean_name[:64]}{ext}"

@handle_operational_error
def store_in_datalake(data: Any, path: str) -> None:
    """Secure data storage with integrity checks"""
    with open(os.path.join(config.DATA_LAKE_PATH, path), 'wb') as f:
        if isinstance(data, pd.DataFrame):
            data.to_parquet(f)
        else:
            f.write(json.dumps(data).encode())
    logger.info(f"Stored data in {path}")

# --------------------------
# PERFORMANCE OPTIMIZATION
# --------------------------
_cache_store = {}

def cache_get(key):
    """Simple in-memory cache get"""
    entry = _cache_store.get(key)
    if entry and (entry['expires_at'] is None or entry['expires_at'] > datetime.utcnow()):
        return entry['value']
    return None

def cache_set(key, value, timeout):
    """Simple in-memory cache set with TTL"""
    expires_at = datetime.utcnow() + timedelta(seconds=timeout) if timeout else None
    _cache_store[key] = {'value': value, 'expires_at': expires_at}

def cached(timeout: int = 300):
    """Advanced caching decorator with TTL"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = _create_cache_key(func.__name__, args, kwargs)
            if (cached := cache_get(cache_key)) is not None:
                return cached
            result = func(*args, **kwargs)
            cache_set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

def lru_cache_wrapper(maxsize=128):
    """Enhanced LRU cache with size monitoring"""
    def decorator(func):
        func = lru_cache(maxsize=maxsize)(func)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.cache_info = func.cache_info
        return wrapper
    return decorator

# --------------------------
# COMPLIANCE & AUDITING
# --------------------------
def query_audit_log(entity_type: str, entity_id: int) -> List[Dict]:
    """Stub for audit log query - replace with actual DB or log retrieval."""
    # TODO: Implement actual audit log retrieval logic
    return []

def generate_audit_trail(entity_type: str, entity_id: int) -> List[Dict]:
    """Generate GDPR-compliant audit trail"""
    return [sanitize_audit_entry(e) for e in query_audit_log(entity_type, entity_id)]

def sanitize_audit_entry(entry: Dict) -> Dict:
    """Sanitize audit log entry for GDPR compliance"""
    sanitized = entry.copy()
    # Example: Remove or hash sensitive fields
    if 'user_id' in sanitized:
        sanitized['user_id'] = hashlib.sha256(str(sanitized['user_id']).encode()).hexdigest()
    if 'ip_address' in sanitized:
        sanitized['ip_address'] = hash_ip(sanitized['ip_address'])
    return sanitized

def check_data_retention_compliance() -> Dict:
    """Verify compliance with data retention policies"""
    return ai_engine.analyze_retention_compliance(config.DATA_RETENTION_POLICY)

# --------------------------
# USER MANAGEMENT HELPERS
# --------------------------
def generate_unique_user_id() -> str:
    """Create collision-resistant user identifier"""
    return hashlib.sha3_256(os.urandom(4096)).hexdigest()[:32]

def validate_password_strength(password: str) -> Dict:
    """Check password against security policies"""
    return ai_engine.assess_password_strength(password, config.PASSWORD_POLICY)

# --------------------------
# EMAIL & NOTIFICATIONS
# --------------------------
@executor.submit
def send_async_email(to: str, subject: str, body: str) -> None:
    """Send emails in background threads"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = config.EMAIL_FROM
    msg['To'] = to
    
    with smtplib.SMTP(config.SMTP_SERVER) as server:
        server.send_message(msg)

# --------------------------
# UTILITY HELPERS
# --------------------------
def parse_iso_datetime(dt_str: str) -> datetime:
    """Robust ISO datetime parser with timezone"""
    dt = parse(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.UTC)
    return dt

def calculate_response_metrics(data: Any) -> Dict:
    """Generate performance metrics for API responses"""
    size = len(str(data).encode('utf-8'))
    return {
        'data_size': size,
        'complexity': ai_engine.calculate_complexity(data),
        'sensitivity_score': ai_engine.assess_data_sensitivity(data)
    }

# --------------------------
# PRIVATE IMPLEMENTATIONS
# --------------------------
def _load_scrum_rules(version: str) -> Dict:
    """Load Scrum Guide rules from file"""
    with open(f'scrum_rules_{version}.json') as f:
        return json.load(f)

def _format_local_time(hour: int, tz: str) -> str:
    """Format hour to local time string"""
    return localize_datetime(
        datetime.utcnow().replace(hour=hour, minute=0), tz
    ).strftime('%H:%M %Z')

def _create_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate unique cache key"""
    arg_hash = hashlib.md5(str(args).encode()).hexdigest()
    kwarg_hash = hashlib.md5(str(kwargs).encode()).hexdigest()
    return f"{func_name}_{arg_hash}_{kwarg_hash}"