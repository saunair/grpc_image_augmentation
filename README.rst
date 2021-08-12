curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
source $HOME/.poetry/env

poetry add requests numpy
poetry add requests opencv-python
poetry add requests imutils
poetry add requests ipython
poetry add requests grpcio
poetry add requests grpcio-tools
poetry add requests fire

poetry build && poetry lock && poetry install && poetry shell
python -m grpc_tools.protoc data/proto/image.proto --python_out=src/image_manipulation/ --proto_path=data/proto/
