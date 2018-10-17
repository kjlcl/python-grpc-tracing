import sys
from jaeger_client import Config


PY3 = sys.version_info >= (3,)

_tracer = None


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
    global _tracer
    _tracer = config.initialize_tracer()
    return _tracer

