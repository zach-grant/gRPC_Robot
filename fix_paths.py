#!/usr/bin/env python3

import os
import sys

# without this the generated protobuf and gRPC python files cannot be imported
sys.path.append(os.path.join(os.path.abspath('.'), 'protos_gen'))
