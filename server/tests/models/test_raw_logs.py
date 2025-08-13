from datetime import datetime, timezone
from typing import Dict, Any

# Test Raw Log Data Fixtures
def get_test_raw_log_base() -> Dict[str, Any]:
    """Base raw log data for testing"""
    return {
        "api_key": "test_api_key_123456789",
        "level": "INFO",
        "message": "Test log message",
        "data": {"key": "value", "number": 42, "boolean": True},
        "metadata": {"service": "test-service", "version": "1.0.0", "environment": "development"},
        "timestamp": "2024-01-15T10:30:00Z",
        "trace_id": "trace-123456789",
        "span_id": "span-987654321"
    }

def get_test_raw_log_create() -> Dict[str, Any]:
    """RawLog model test data for creation"""
    return get_test_raw_log_base()

def get_test_raw_log_minimal() -> Dict[str, Any]:
    """Minimal raw log with only required fields"""
    return {
        "api_key": "test_api_key_minimal",
        "message": "Minimal log message"
    }

def get_test_raw_log_with_source_id() -> Dict[str, Any]:
    """Raw log with source_id (for consumer testing)"""
    base_data = get_test_raw_log_base()
    base_data.update({
        "source_id": 1,
        "api_key": "test_api_key_with_source"
    })
    return base_data

def get_test_raw_log_debug() -> Dict[str, Any]:
    """Debug level log for testing different log levels"""
    base_data = get_test_raw_log_base()
    base_data.update({
        "level": "DEBUG",
        "message": "Debug log message for testing",
        "api_key": "test_api_key_debug"
    })
    return base_data

def get_test_raw_log_error() -> Dict[str, Any]:
    """Error level log for testing different log levels"""
    base_data = get_test_raw_log_base()
    base_data.update({
        "level": "ERROR",
        "message": "Error log message for testing",
        "data": {"error_code": 500, "error_message": "Internal server error", "stack_trace": "..."},
        "api_key": "test_api_key_error"
    })
    return base_data

def get_test_raw_log_critical() -> Dict[str, Any]:
    """Critical level log for testing different log levels"""
    base_data = get_test_raw_log_base()
    base_data.update({
        "level": "CRITICAL",
        "message": "Critical system failure",
        "data": {"system": "database", "failure_type": "connection_lost", "impact": "high"},
        "api_key": "test_api_key_critical"
    })
    return base_data

def get_test_raw_log_with_complex_data() -> Dict[str, Any]:
    """Raw log with complex nested data structures"""
    base_data = get_test_raw_log_base()
    base_data.update({
        "message": "Complex data structure log",
        "data": {
            "user": {
                "id": 123,
                "profile": {
                    "name": "John Doe",
                    "preferences": {
                        "theme": "dark",
                        "language": "en",
                        "notifications": {
                            "email": True,
                            "push": False,
                            "sms": True
                        }
                    }
                },
                "activity": {
                    "last_login": "2024-01-15T10:30:00Z",
                    "login_count": 42,
                    "sessions": [
                        {"id": "sess_1", "duration": 3600},
                        {"id": "sess_2", "duration": 1800}
                    ]
                }
            },
            "request": {
                "method": "POST",
                "endpoint": "/api/users",
                "headers": {"Content-Type": "application/json", "Authorization": "Bearer ..."},
                "body": {"name": "Jane Doe", "email": "jane@example.com"}
            },
            "performance": {
                "response_time": 150,
                "memory_usage": "256MB",
                "cpu_usage": "15%"
            }
        },
        "metadata": {
            "service": "user-service",
            "version": "2.1.0",
            "deployment": "production",
            "region": "us-east-1",
            "instance_id": "i-1234567890abcdef0",
            "tags": ["user-management", "api", "production", "monitoring"]
        },
        "api_key": "test_api_key_complex"
    })
    return base_data

def get_test_raw_log_with_trace_context() -> Dict[str, Any]:
    """Raw log with comprehensive tracing context"""
    base_data = get_test_raw_log_base()
    base_data.update({
        "message": "Request processed with full trace context",
        "trace_id": "trace-abc123def456ghi789",
        "span_id": "span-xyz987uvw654rst321",
        "data": {
            "request_id": "req-123456789",
            "correlation_id": "corr-987654321",
            "parent_span_id": "span-parent-123",
            "trace_flags": "01",
            "sampled": True
        },
        "metadata": {
            "service": "gateway-service",
            "operation": "process_request",
            "trace_sampled": True,
            "distributed_tracing": True
        },
        "api_key": "test_api_key_trace"
    })
    return base_data

def get_test_raw_log_performance() -> Dict[str, Any]:
    """Performance-focused log for testing monitoring scenarios"""
    base_data = get_test_raw_log_base()
    base_data.update({
        "level": "INFO",
        "message": "Performance metrics collected",
        "data": {
            "metrics": {
                "cpu_percent": 45.2,
                "memory_percent": 67.8,
                "disk_io": {
                    "read_bytes": 1024000,
                    "write_bytes": 512000,
                    "read_count": 150,
                    "write_count": 75
                },
                "network": {
                    "bytes_sent": 2048000,
                    "bytes_recv": 4096000,
                    "packets_sent": 300,
                    "packets_recv": 600
                }
            },
            "thresholds": {
                "cpu_warning": 70,
                "cpu_critical": 90,
                "memory_warning": 80,
                "memory_critical": 95
            }
        },
        "metadata": {
            "service": "monitoring-service",
            "collection_interval": 60,
            "metric_type": "system_performance"
        },
        "api_key": "test_api_key_performance"
    })
    return base_data

def get_test_raw_log_security() -> Dict[str, Any]:
    """Security-focused log for testing security monitoring"""
    base_data = get_test_raw_log_base()
    base_data.update({
        "level": "WARN",
        "message": "Suspicious login attempt detected",
        "data": {
            "security_event": {
                "type": "failed_login",
                "severity": "medium",
                "user_id": "user_123",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "location": "New York, US",
                "attempt_count": 5,
                "time_window": "300s"
            },
            "risk_indicators": {
                "unusual_location": True,
                "multiple_failures": True,
                "suspicious_user_agent": False,
                "vpn_detected": False
            }
        },
        "metadata": {
            "service": "security-service",
            "event_source": "authentication",
            "threat_level": "medium",
            "requires_review": True
        },
        "api_key": "test_api_key_security"
    })
    return base_data 