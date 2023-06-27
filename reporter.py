import time
import notifier_pb2_grpc
import notifier_pb2
import grpc
from loguru import logger

while True:
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            notifier_stub = notifier_pb2_grpc.NotifierStub(channel)
            while True:
                notifier_stub.SetStatusBox(notifier_pb2.StatusBox(Id=0, Value="Sus"))
    except Exception as err:
        logger.error(err)
    time.sleep(1)