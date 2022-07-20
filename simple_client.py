#!/usr/bin/env python3

import grpc
import fix_paths
import protos_gen as pg

if __name__ == '__main__':
    with grpc.insecure_channel('localhost:9000') as channel:
        stub = pg.estop_pb2_grpc.StopServiceStub(channel)
        reply = stub.Stop(pg.estop_pb2.StopRequest())
        print(type(reply))
