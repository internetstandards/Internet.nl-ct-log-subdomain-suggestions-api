SHELL = /bin/bash

ctlssa = docker compose run -ti app
dev = docker compose run -i -v ${PWD}/.root:/root --rm dev
db = docker compose exec -i db

# run this before/after checking in/out the source
all: build lint test

# run the entire project
run up: requirements
	COMPOSE_PROJECT_NAME=internetnl-ctlssa docker compose up --remove-orphans --watch

# make migration files
makemigrations:
	${ctlssa} makemigrations

# run development shell
dev dev-shell shell:
	${dev}

dbshell:
	${db} psql --user ctlssa

# fix/check linting issues
lint fix:
	${dev} "isort ."
	${dev} "black ."

# run test suite
test:
	${dev} "pytest ./tests/"

# updates requirements.txt files when requirements.in files have changes
requirements_files = $(subst .in,.txt,$(wildcard requirements*.in))
requirements: ${requirements_files}
${requirements_files}: %.txt: %.in
	${dev} pip-compile $< --output-file $@

# build docker container images
build: .build
.build: Dockerfile compose.yml pyproject.toml $(shell find src/) ${requirements_files}
	docker compose build ${build_args}
	touch $@

push_images:
	docker compose --push app certstream
