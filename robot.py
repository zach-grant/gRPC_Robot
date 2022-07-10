#!/usr/bin/env python3

import grpc
from concurrent.futures import ThreadPoolExecutor

import fix_paths
import logging
import protos_gen as pg


class RobotServicer(pg.estop_pb2_grpc.stopServiceServicer,
                    pg.goto_pb2_grpc.GoTo_ControllerServicer,
                    pg.metadata_pb2_grpc.metaServiceServicer,
                    pg.photo_pb2_grpc.photoServiceServicer,
                    pg.photo_pb2_grpc.takePhotoServiceServicer,
                    pg.remoteControl_pb2_grpc.rcServiceServicer,
                    pg.telem_pb2_grpc.telemServiceServicer,
                    ):
    def stop(self, request, context):
        return pg.estop_pb2.stopReply()

    def GoToCoordinates(self, request, context):
        return pg.goto_pb2.GoToResponse()

    def getMetadata(self, request, context):
        return pg.metadata_pb2.metadata()

    def getPhoto(self, request, context):
        return pg.photo_pb2.photoReply()

    def takePhoto(self, request, context):
        return pg.photo_pb2.newGeoPhotoTakenReply()

    def move(self, request_iterator, context):
        return pg.remoteControl_pb2_grpc.google_dot_protobuf_dot_empty__pb2

    def setMode(self, request, context):
        return pg.telem_pb2.setModeResponse()


if __name__ == '__main__':
    logging.info(f'Using the following path for importing the proto/gRPC imports: {fix_paths}')

    server = grpc.server(ThreadPoolExecutor(max_workers=5))
    robot_servicer = RobotServicer()
    pg.estop_pb2_grpc.add_stopServiceServicer_to_server(robot_servicer, server)
    pg.goto_pb2_grpc.add_GoTo_ControllerServicer_to_server(robot_servicer, server)
    pg.metadata_pb2_grpc.add_metaServiceServicer_to_server(robot_servicer, server)
    pg.photo_pb2_grpc.add_photoServiceServicer_to_server(robot_servicer, server)
    pg.photo_pb2_grpc.add_takePhotoServiceServicer_to_server(robot_servicer, server)
    pg.remoteControl_pb2_grpc.add_rcServiceServicer_to_server(robot_servicer, server)
    pg.telem_pb2_grpc.add_telemServiceServicer_to_server(robot_servicer, server)
    server.add_insecure_port('[::]:9000')
    server.start()
    server.wait_for_termination()
