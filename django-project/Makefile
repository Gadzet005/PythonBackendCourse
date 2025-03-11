PIP := venv/bin/pip
PYTHON3 := venv/bin/python3

clear:
	rm -rf venv

venv:
	python3 -m venv venv

requirements:
	${PIP} install -r requirements.txt

run:
	${PYTHON3} project/manage.py runserver

makemigrations:
	${PYTHON3} project/manage.py makemigrations

migrate:
	${PYTHON3} project/manage.py migrate

setup: clear venv requirements migrate
