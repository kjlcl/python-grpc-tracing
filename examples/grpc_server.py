import grpc
import os
import time
from concurrent import futures
from grpc_tracing.jaeger_trace_client import init_tracer
from grpc_tracing.server_interceptor import TracingInterceptor
import helloworld_pb2_grpc
import helloworld_pb2


class Greeter(helloworld_pb2_grpc.GreetingServicer):
    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message="greeting")


def serving():
    host_ip = os.environ.get('HOST_IP')
    if host_ip:
        tracer = init_tracer("sdk_tracing", "127.0.0.1")
        interceptor = TracingInterceptor(tracer)
    else:
        interceptor = None

    addr = "[::]:50051"
    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=10), interceptors=(interceptor,))
    helloworld_pb2_grpc.add_GreetingServicer_to_server(Greeter(), server)
    server.add_insecure_port(addr)
    server.start()
    try:
        while True:
            time.sleep(24 * 3600)
    except KeyboardInterrupt:
        server.stop(0)


stopped = False
if __name__ == '__main__':

    serving()


