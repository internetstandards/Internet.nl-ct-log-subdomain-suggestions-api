SHELL = /bin/bash

ctlssa = docker compose run -ti app
dev = docker compose run -ti -v ${PWD}/.root:/root --rm dev

# run this before/after checking in/out the source
all: build lint test

# run the entire project
run up: requirements
	docker compose up --build --remove-orphans --watch

# make migration files
makemigrations: build
	${ctlssa} makemigrations

# run development shell
dev dev-shell shell: build
	${dev}

# fix/check linting issues
lint fix: build
	${dev} "isort ."
	${dev} "black ."

# run test suite
test: build
	${dev} "pytest ./tests/"

# build docker container images
build: requirements
	docker compose build

# updates requirements.txt files when requirements.in files have changes
requirements_files = $(subst .in,.txt,$(wildcard requirements*.in))
requirements: ${requirements_files}
${requirements_files}: %.txt: %.in
	${dev} pip-compile $< --output-file $@

dev dev-shell shell: requirements
	${dev}

lint fix:
	${dev} "isort ."
	${dev} "black ."
