#!/usr/bin/env python3

import random
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
import grpc
from concurrent.futures import ThreadPoolExecutor
import fix_paths
import logging
import protos_gen as pg
import google
import robot_config as cfg


class Robot:
    def __init__(self):
        # the robot needs its own instance of the random number generator
        self.random = random.Random()

        # used to create the UIDs of the messages (part of the header)
        self.current_message_id = self.random.randint(cfg.message_uid_start_min, cfg.message_uid_start_max)

        # used for the timestamp of the messages (part of the header)
        self.timestamp = Timestamp()

        # set the initial mode of the robot
        self.current_mode = pg.telem_pb2.MODE_UNKNOWN

        # define some identity for the robot
        robot = self.random.choice(cfg.robot_templates)
        self.name = robot['name']
        self.firmware_version = f'{robot["model"]}#{self.__random_string(6)}'
        self.birthday = str(datetime.now())
        self.serial_id = self.__random_string(20)
        self.batteryType = f'{self.random.randint(1,4)}-cell {robot["model"]} battery'

        # define the initial position of the robot in 2D space
        self.x, self.y = cfg.robot_init_position

        # set initial state of the arms
        self.left_arm = pg.telem_pb2.ARM_UNKNOWN_STATE
        self.right_arm = pg.telem_pb2.ARM_UNKNOWN_STATE

        logging.info(f'A new {robot["description"]} robot created successfully! '
                     f'Name: {self.name}, Model: {robot["model"]}')

    def __random_string(self, length):
        # use only capital letters hence the range from 65 to 90
        result = [chr(self.random.randint(65, 90)) for _ in range(length)]
        return ''.join(result)

    def __create_header(self):
        header = pg.header_pb2.Header(uid=str(self.current_message_id).rjust(20, '0'),
                                      time=self.timestamp.GetCurrentTime()
                                      )
        logging.info(f'Header created: UID={header.uid}, TIME={header.time}')
        self.current_message_id += 1  # use the next number as an UID for the next message
        return header

    def fail_once_in_n_times(self, n):
        return False if self.random.randint(0, n-1) == 0 else True

    def handle_estop(self, request):
        logging.info(f'EStop request received: header={request.header}')
        self.current_mode = pg.telem_pb2.MODE_UNKNOWN  # what estop requested set the robot to unknown state
        # fail the emergency stop randomly 1 out of 5 times
        stop_success = pg.estop_pb2.STOP_SUCCESS if self.fail_once_in_n_times(5) else pg.estop_pb2.STOP_FAIL
        reply = pg.estop_pb2.StopReply(header=self.__create_header(), success=stop_success)
        logging.info(f'EStop reply created: success={reply.success}')
        return reply

    def handle_goto(self, request):
        logging.info(f'GoTo request received: header={request.header}, x_coord={request.x_coord}, '
                     f'y_coord={request.y_coord}')
        go_to_result = pg.goto_pb2.GOTO_UNDEFINED
        if self.current_mode != pg.telem_pb2.MODE_GUIDED:
            go_to_result = pg.goto_pb2.GOTO_CANNOT_MOVE
        elif (request.x_coord < 0) or (request.y_coord < 0):
            go_to_result = pg.goto_pb2.GOTO_INVALID_COORDINATES
        else:
            go_to_result = pg.goto_pb2.GOTO_SUCCESS
            # TODO: for the moment the robot doesn't move but teleports instantaneously. This needs to be fixed!
            self.x = request.x_coord
            self.y = request.y_coord

        response = pg.goto_pb2.GoToResponse(header=self.__create_header(), gotoResult=go_to_result)
        logging.info(f'GoTo response created: result={response.gotoResult}')
        return response

    def handle_metadata(self):
        logging.info(f'Metadata request received.')
        metadata = pg.metadata_pb2.Metadata(name=self.name,
                                            firmwareVersion=self.firmware_version,
                                            birthday=self.birthday,
                                            serialID=self.serial_id,
                                            batteryType=self.batteryType,
                                            )
        logging.info(f'Metadata response created: metadata={metadata}')
        return metadata

    def handle_move(self, request_iterator):
        if self.current_mode == pg.telem_pb2.MODE_MANUAL:
            # accept moves from the remote control only in manual mode
            logging.info('The robot is in MANUAL mode so the RC commands are accepted!')

            for request in request_iterator:
                # TODO: xAxis and yAxis should be the rates at which the robot moves and currently it just teleports
                #  to the specified position. The same goes for the arms as well. Their positioning should not be
                #  instantaneous but should happen slowly in time.
                self.x = request.xAxis
                self.y = request.yAxis
                self.left_arm = request.leftArmCommand
                self.right_arm = request.rightArmCommand
                logging.info(f'The state of the robot after the RC command x:{self.x}, y:{self.y},'
                             f'left arm:{self.left_arm}, right arm:{self.right_arm}')

        return google.protobuf.empty_pb2.Empty()

    def handle_set_mode(self, request):
        logging.info(f'SetMode request received: header={request.header}, mode={request.mode}')
        success = False
        if request.mode != pg.telem_pb2.MODE_UNKNOWN:
            self.current_mode = request.mode
            success = True

        response = pg.telem_pb2.SetModeResponse(header=self.__create_header(), modeSetSuccess=success)
        logging.info(f'SetMode response created: success={response.modeSetSuccess}')

        return response


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
        return self.handle_goto(request)

    def GetMetadata(self, request, context):
        return self.handle_metadata()

    def GetPhoto(self, request, context):
        return pg.photo_pb2.PhotoReply()

    def TakePhoto(self, request, context):
        return pg.photo_pb2.NewGeoPhotoTakenReply()

    def Move(self, request_iterator, context):
        return self.handle_move(request_iterator)

    def SetMode(self, request, context):
        return self.handle_set_mode(request)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    logging.info(f'Using the following path for importing the proto/gRPC imports: {fix_paths}')

    server = grpc.server(ThreadPoolExecutor(max_workers=cfg.server_max_workers))
    robot_servicer = RobotServicer()
    pg.estop_pb2_grpc.add_StopServiceServicer_to_server(robot_servicer, server)
    pg.goto_pb2_grpc.add_GoToControllerServicer_to_server(robot_servicer, server)
    pg.metadata_pb2_grpc.add_MetaServiceServicer_to_server(robot_servicer, server)
    pg.photo_pb2_grpc.add_PhotoServiceServicer_to_server(robot_servicer, server)
    pg.photo_pb2_grpc.add_TakePhotoServiceServicer_to_server(robot_servicer, server)
    pg.remoteControl_pb2_grpc.add_RcServiceServicer_to_server(robot_servicer, server)
    pg.telem_pb2_grpc.add_TelemServiceServicer_to_server(robot_servicer, server)

    server.add_insecure_port(f'{cfg.server_url}:{cfg.server_port}')
    server.start()
    server.wait_for_termination()
