from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Prometheus metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_sessions = Gauge(
    'active_sessions_total',
    'Number of active sessions'
)

agent_executions = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['status']
)

agent_duration = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration'
)

def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()

