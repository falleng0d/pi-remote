

proto:
	./.venv/Scripts/python -m grpc_tools.protoc --proto_path=. --python_out=. --pyi_out=. --grpc_python_out=. ./app/input.proto
