import grpc
import logging
import opentracing
import grpc_tracing.tags as tags


def _unary_unary_rpc_terminator(code, details):

    def terminate(ignored_request, context):
        context.abort(code, details)

    return grpc.unary_unary_rpc_method_handler(terminate)


def _wrap_rpc_behavior(handler, fn):
    if handler is None:
        return None

    if handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.stream_stream
        handler_factory = grpc.stream_stream_rpc_method_handler
    elif handler.request_streaming and not handler.response_streaming:
        behavior_fn = handler.stream_unary
        handler_factory = grpc.stream_unary_rpc_method_handler
    elif not handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.unary_stream
        handler_factory = grpc.unary_stream_rpc_method_handler
    else:
        behavior_fn = handler.unary_unary
        handler_factory = grpc.unary_unary_rpc_method_handler

    return handler_factory(fn(behavior_fn,
                              handler.request_streaming,
                              handler.response_streaming),
                           request_deserializer=handler.request_deserializer,
                           response_serializer=handler.response_serializer)


class TracingInterceptor(grpc.ServerInterceptor):

    def __init__(self, tracer):
        self._tracer = tracer

    def _start_span(self, servicer_context, method):
        span_context = None
        error = None
        metadata = servicer_context.invocation_metadata()
        try:
            if metadata:
                span_context = self._tracer.extract(
                    opentracing.Format.HTTP_HEADERS, dict(metadata))
        except (opentracing.UnsupportedFormatException,
                opentracing.InvalidCarrierException,
                opentracing.SpanContextCorruptedException) as e:
            logging.exception('tracer.extract() failed')
            error = e
        peer_tags = {
            tags.COMPONENT: 'grpc',
            tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER
        }
        tags.add_peer_tags(servicer_context.peer(), peer_tags)
        span = self._tracer.start_span(
            operation_name=method, child_of=span_context, tags=peer_tags)
        if error is not None:
            span.log_kv({'event': 'error', 'error.object': error})
        return span

    def intercept_service(self, continuation, handler_call_details):
        def tracing_wrapper(behavior, request_streaming, response_streaming):
            def new_behavior(request_or_iterator, servicer_context):
                with self._start_span(
                        servicer_context, handler_call_details.method) as span:
                    try:
                        return behavior(request_or_iterator, servicer_context)
                    except Exception as e:
                        span.set_tag('error', True)
                        span.log_kv({'event': 'error', 'error.object': e})
            return new_behavior

        return _wrap_rpc_behavior(
            continuation(handler_call_details), tracing_wrapper)
