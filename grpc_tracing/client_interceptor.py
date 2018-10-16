import grpc
import grpc_tracing.tags as tags
from grpc._interceptor import _ClientCallDetails
import logging
import opentracing

from six import iteritems


class _ConcreteValue(grpc.Future):

    def __init__(self, result):
        self._result = result

    def cancel(self):
        return False

    def cancelled(self):
        return False

    def running(self):
        return False

    def done(self):
        return True

    def result(self, timeout=None):
        return self._result

    def exception(self, timeout=None):
        return None

    def traceback(self, timeout=None):
        return None

    def add_done_callback(self, fn):
        fn(self._result)


class TracingClientInterceptor(grpc.UnaryUnaryClientInterceptor,
                               grpc.StreamUnaryClientInterceptor):

    def __init__(self, tracer):
        self._tracer = tracer

    def _inject_span_context(self, span, metadata):
        headers = {}
        try:
            self._tracer.inject(span.context, opentracing.Format.HTTP_HEADERS, headers)
        except (opentracing.UnsupportedFormatException,
                opentracing.InvalidCarrierException,
                opentracing.SpanContextCorruptedException) as e:
            logging.exception('tracer.inject() failed')
            span.log_kv({'event': 'error', 'error.object': e})
            return metadata
        metadata = () if metadata is None else tuple(metadata)
        return metadata + tuple((k.lower(), v) for (k, v) in iteritems(headers))

    def _start_span(self, method):
        client_tags = {
            tags.COMPONENT: 'grpc',
            tags.SPAN_KIND: tags.SPAN_KIND_RPC_CLIENT
        }
        return self._tracer.start_span(
            operation_name=method, tags=client_tags)

    def _intercept_call(self, continuation,
                        client_call_details, request_or_iterator):
        if self._tracer:
            with self._start_span(client_call_details.method) as span:
                metadata = self._inject_span_context(span, client_call_details.metadata)
                new_call_detial = _ClientCallDetails(
                    client_call_details.method,
                    client_call_details.timeout,
                    metadata,
                    client_call_details.credentials)
                # setattr(client_call_details, 'metadata', metadata)
                return continuation(new_call_detial, request_or_iterator)

        return continuation(client_call_details, request_or_iterator)

    def intercept_unary_unary(
            self, continuation, client_call_details, request):
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_stream_unary(
            self, continuation, client_call_details, request_iterator):
        return self._intercept_call(
            continuation, client_call_details, request_iterator)
