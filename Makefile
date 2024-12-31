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

install-service:
	sudo cp pi-remote.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable pi-remote.service
	sudo systemctl start pi-remote.service

remove-service:
	sudo systemctl stop pi-remote.service
	sudo systemctl disable pi-remote.service
	sudo rm /etc/systemd/system/pi-remote.service

install-gadget-service:
	sudo cp pi-remote.usb-gadget.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable pi-remote.usb-gadget.service
	sudo systemctl start pi-remote.usb-gadget.service

remove-gadget-service:
	sudo systemctl stop pi-remote.usb-gadget.service
	sudo systemctl disable pi-remote.usb-gadget.service
	sudo rm /etc/systemd/system/pi-remote.usb-gadget.service
