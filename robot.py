#!/usr/bin/env python3

import random
from google.protobuf.timestamp_pb2 import Timestamp
import grpc
from concurrent.futures import ThreadPoolExecutor

import fix_paths
import logging
import protos_gen as pg
import google


class Robot:
    def __init__(self):
        # the robot needs its own instance of the random number generator
        self.random = random.Random()

        # used to create the UIDs of the messages (part of the header)
        self.current_message_id = self.random.randint(0, 1_000_000)

        # used for the timestamp of the messages (part of the header)
        self.timestamp = Timestamp()

        logging.info('A robot created successfully!')

    def create_header(self):
        header = pg.header_pb2.Header(uid=str(self.current_message_id).rjust(20, '0'),
                                      time=self.timestamp.GetCurrentTime()
                                      )
        logging.info(f'Header created: UID={header.uid}, TIME={header.time}')
        self.current_message_id += 1 # use the next number as an UID for the next message
        return header

    def handle_estop(self, request):
        # fail the emergency stop randomly 1 out of 5 times
        logging.info(f'EStop request received: header={request.header}')
        stop_success = pg.estop_pb2.FAIL if self.random.randint(0, 5) == 0 else pg.estop_pb2.SUCCESS
        reply = pg.estop_pb2.StopReply(header=self.create_header(), success=stop_success)
        logging.info(f'EStop reply created: success={reply.success}')
        return reply


class RobotServicer(Robot,
                    pg.estop_pb2_grpc.StopServiceServicer,
                    pg.goto_pb2_grpc.GoToControllerServicer,
                    pg.metadata_pb2_grpc.MetaServiceServicer,
                    pg.photo_pb2_grpc.PhotoServiceServicer,
                    pg.photo_pb2_grpc.TakePhotoServiceServicer,
                    pg.remoteControl_pb2_grpc.RcServiceServicer,
                    pg.telem_pb2_grpc.TelemServiceServicer,
                    ):
    def Stop(self, request, context):
        return self.handle_estop(request)

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
    logging.basicConfig(level=logging.INFO)

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
