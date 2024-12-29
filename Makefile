PWD := $(shell pwd)

start:
	PYTHONPATH=${PWD} ./.venv/bin/python app/main.py

test:
	PYTHONPATH=${PWD} ./.venv/bin/python test.py

proto:
	./.venv/Scripts/python -m grpc_tools.protoc --proto_path=. --python_out=. --pyi_out=. --grpc_python_out=. ./app/input.proto

init-gadget:
	sudo ./otg/init-usb-gadget.sh

remove-gadget:
	sudo ./otg/remove-usb-gadget.sh

reload-gadget: remove-gadget init-gadget
