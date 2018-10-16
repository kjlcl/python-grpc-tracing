import sys
from jaeger_client import Config


PY3 = sys.version_info >= (3,)

_server_tracer = None
_client_tracer = None


def init_server_tracer(
        service_name, host_ip, reporting_port=6831, sampling_port=5778):
    tracer = _init_tracer(
        service_name, host_ip,
        reporting_port=reporting_port, sampling_port=sampling_port)
    global _server_tracer
    _server_tracer = tracer
    return tracer


def init_client_tracer(
        service_name, host_ip, reporting_port=6831, sampling_port=5778):
    tracer = _init_tracer(
        service_name, host_ip,
        reporting_port=reporting_port, sampling_port=sampling_port)
    global _client_tracer
    _client_tracer = tracer
    return tracer


def _init_tracer(
        service_name, host_ip, reporting_port=6831, sampling_port=5778):
    """init jaeger client"""
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'sampling_port': sampling_port,
                'reporting_port': reporting_port,
                'reporting_host': host_ip
            },
            'logging': True,
        }, service_name=service_name, validate=True)
    return config.initialize_tracer()

