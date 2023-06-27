from concurrent import futures
import grpc
import robot_pb2_grpc
import robot_impl
import notifier_pb2_grpc
# import browser


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    robot_pb2_grpc.add_RobotServicer_to_server(
        robot_impl.RobotServicer(), server)
    # notifier_pb2_grpc.add_NotifierServicer_to_server(
    #     browser.NotifierServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()