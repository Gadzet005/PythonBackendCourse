PIP := venv/bin/pip
PYTHON3 := venv/bin/python3

clear:
	rm -rf venv

venv:
	${PYTHON3} -m venv venv

requirements:
	${PIP} install -r requirements.txt

run:
	${PYTHON3} project/manage.py runserver

makemigrations:
	${PYTHON3} project/manage.py makemigrations

migrate:
	${PYTHON3} project/manage.py migrate

setup:
	make clear
	make venv
	make requirements
	make migrate
