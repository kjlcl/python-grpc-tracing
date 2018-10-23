import grpc
import helloworld_pb2_grpc
import helloworld_pb2
import time
from grpc_tracing.client_interceptor import TracingClientInterceptor
from grpc_tracing.jaeger_client import init_tracer


if __name__ == '__main__':
    tracer = init_tracer("greeter", '127.0.0.1')
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        intercept_channel = grpc.intercept_channel(
            channel, TracingClientInterceptor(tracer))
        stub = helloworld_pb2_grpc.GreetingStub(intercept_channel)
        response = stub.SayHello(helloworld_pb2.HelloRequest(name='spongebob'))
        print("Greeter client received: " + response.message)

    time.sleep(2)
    tracer.close()
    time.sleep(3)

