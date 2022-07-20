#/bin/bash

# define the name of the directory for the generated files
PROTOS_GEN_DIR=protos_gen

# delete the old directory and recreate it
rm -rf $PROTOS_GEN_DIR
mkdir $PROTOS_GEN_DIR

# generate the protobuf and the gRPC files
python -m grpc_tools.protoc -I=protos/ --python_out=protos_gen/ --grpc_python_out=protos_gen/ protos/*.proto

# create an auxiliary file with all the imports of the generated protobuf and gRPC python files
for f in `ls -1 protos_gen/*.py`; do
    echo 'from . import ' `basename $f | cut -d '.' -f 1` >> protos_gen/aux
done

# rename the auxiliary file to __init__.py
mv protos_gen/aux protos_gen/__init__.py

# export the PYTHONPATH file
# export PYTHONPATH=$PYTHONPATH:"${PWD}"/protos_gen
