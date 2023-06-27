from time import time
import notifier_pb2
import notifier_pb2_grpc

class NotifierServicer(notifier_pb2_grpc.NotifierServicer):
    def SetStatusBox(self, request, context):
        return notifier_pb2.Status(Ok=True, Timestamp=time())