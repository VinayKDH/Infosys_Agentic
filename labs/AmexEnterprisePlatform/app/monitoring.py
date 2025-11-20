"""Monitoring and metrics"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time
import logging
from functools import wraps

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
    ['agent_type', 'status']
)

agent_duration = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration',
    ['agent_type']
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['operation']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['operation']
)

fraud_detections = Counter(
    'fraud_detections_total',
    'Total fraud detections',
    ['risk_level']
)

compliance_checks = Counter(
    'compliance_checks_total',
    'Total compliance checks',
    ['status']
)


def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()

