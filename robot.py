#!/usr/bin/env python3

import grpc
from concurrent.futures import ThreadPoolExecutor

import fix_paths
import logging
import protos_gen as pg
import google


class RobotServicer(pg.estop_pb2_grpc.StopServiceServicer,
                    pg.goto_pb2_grpc.GoToControllerServicer,
                    pg.metadata_pb2_grpc.MetaServiceServicer,
                    pg.photo_pb2_grpc.PhotoServiceServicer,
                    pg.photo_pb2_grpc.TakePhotoServiceServicer,
                    pg.remoteControl_pb2_grpc.RcServiceServicer,
                    pg.telem_pb2_grpc.TelemServiceServicer,
                    ):
    def Stop(self, request, context):
        return pg.estop_pb2.StopReply()

    def GoToCoordinates(self, request, context):
        return pg.goto_pb2.GoToResponse()

    def GetMetadata(self, request, context):
        return pg.metadata_pb2.Metadata()

    def GetPhoto(self, request, context):
        return pg.photo_pb2.PhotoReply()

    def TakePhoto(self, request, context):
        return pg.photo_pb2.NewGeoPhotoTakenReply()

    def Move(self, request_iterator, context):
        return google.protobuf.empty_pb2.Empty()

    def SetMode(self, request, context):
        return pg.telem_pb2.SetModeResponse()


if __name__ == '__main__':
    logging.info(f'Using the following path for importing the proto/gRPC imports: {fix_paths}')

    server = grpc.server(ThreadPoolExecutor(max_workers=5))
    robot_servicer = RobotServicer()
    pg.estop_pb2_grpc.add_StopServiceServicer_to_server(robot_servicer, server)
    pg.goto_pb2_grpc.add_GoToControllerServicer_to_server(robot_servicer, server)
    pg.metadata_pb2_grpc.add_MetaServiceServicer_to_server(robot_servicer, server)
    pg.photo_pb2_grpc.add_PhotoServiceServicer_to_server(robot_servicer, server)
    pg.photo_pb2_grpc.add_TakePhotoServiceServicer_to_server(robot_servicer, server)
    pg.remoteControl_pb2_grpc.add_RcServiceServicer_to_server(robot_servicer, server)
    pg.telem_pb2_grpc.add_TelemServiceServicer_to_server(robot_servicer, server)

    server.add_insecure_port('[::]:9000')
    server.start()
    server.wait_for_termination()
