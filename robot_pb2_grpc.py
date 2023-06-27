# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import robot_pb2 as robot__pb2


class RobotStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SetThrust = channel.unary_unary(
                '/Robot/SetThrust',
                request_serializer=robot__pb2.MotorsThrust.SerializeToString,
                response_deserializer=robot__pb2.Status.FromString,
                )
        self.SetGimbal = channel.unary_unary(
                '/Robot/SetGimbal',
                request_serializer=robot__pb2.GimbalPosition.SerializeToString,
                response_deserializer=robot__pb2.Status.FromString,
                )
        self.SetLaser = channel.unary_unary(
                '/Robot/SetLaser',
                request_serializer=robot__pb2.LaserState.SerializeToString,
                response_deserializer=robot__pb2.Status.FromString,
                )


class RobotServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SetThrust(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetGimbal(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetLaser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RobotServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SetThrust': grpc.unary_unary_rpc_method_handler(
                    servicer.SetThrust,
                    request_deserializer=robot__pb2.MotorsThrust.FromString,
                    response_serializer=robot__pb2.Status.SerializeToString,
            ),
            'SetGimbal': grpc.unary_unary_rpc_method_handler(
                    servicer.SetGimbal,
                    request_deserializer=robot__pb2.GimbalPosition.FromString,
                    response_serializer=robot__pb2.Status.SerializeToString,
            ),
            'SetLaser': grpc.unary_unary_rpc_method_handler(
                    servicer.SetLaser,
                    request_deserializer=robot__pb2.LaserState.FromString,
                    response_serializer=robot__pb2.Status.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Robot', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Robot(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SetThrust(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Robot/SetThrust',
            robot__pb2.MotorsThrust.SerializeToString,
            robot__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetGimbal(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Robot/SetGimbal',
            robot__pb2.GimbalPosition.SerializeToString,
            robot__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetLaser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Robot/SetLaser',
            robot__pb2.LaserState.SerializeToString,
            robot__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)