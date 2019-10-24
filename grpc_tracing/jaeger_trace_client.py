import sys
import threading
from jaeger_client.config import Config


PY3 = sys.version_info >= (3,)

_tracer = None


class TracerProxy(object):
    __span_container = threading.local()

    def __init__(self, tracer):
        self._tracer = tracer
        TracerProxy.__span_container.span_list = []

    def start_span(self,
                   operation_name=None,
                   child_of=None,
                   references=None,
                   tags=None,
                   start_time=None):
        return self._tracer.start_span(
            operation_name=operation_name,
            child_of=child_of,
            references=references,
            tags=tags,
            start_time=start_time
        )

    def inject(self, span_context, formatter, carrier):
        return self._tracer.inject(span_context, formatter, carrier)

    def extract(self, formatter, carrier):
        return self._tracer.extract(formatter, carrier)

    def close(self):
        return self._tracer.close()

    def report_span(self, span):
        self._tracer.report_span(span)

    def random_id(self):
        return self._tracer.random_id()

    def is_debug_allowed(self, *args, **kwargs):
        return self._tracer.is_debug_allowed(*args, **kwargs)

    @classmethod
    def add_seq_span(cls, span):
        cls.__span_container.span_list.append(span)

    @classmethod
    def quit_span(cls, span):
        span_list = cls.__span_container.span_list
        count = len(span_list)
        for i in range(count - 1, -1, -1):
            if span_list[i] == span:
                cls.__span_container.span = span_list[:i]
                return

    @classmethod
    def get_latest_span(cls):
        count = len(cls.__span_container.span_list)
        if count:
            return cls.__span_container.span_list[count - 1]
        return None


def init_tracer(
        service_name, host_ip, reporting_port=6831, sampling_port=5778):
    """init jaeger client"""
    global _tracer
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
            'propagation': 'b3',
        }, service_name=service_name, validate=True)
    jaeger_tracer = config.initialize_tracer()
    if jaeger_tracer:
        _tracer = TracerProxy(jaeger_tracer)
    return _tracer

