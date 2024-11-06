SHELL = /bin/bash

ctlssa = docker compose run -ti app
dev = docker compose run -i --rm dev
db = docker compose exec -i db

project_name = internetnl-ctlssa

# run this before/after checking in/out the source
all: build lint test

# run the entire project
run up:
	COMPOSE_PROJECT_NAME=${project_name} docker compose up --remove-orphans --watch

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
	${dev} "pytest --verbose ."

test-watch:
	${dev} "ptw --clear . -- --verbose"

check: requirements
	@if [ ! -z "$(shell git status --porcelain requirements*.txt)" ];then \
	  echo "Requirements .in files have not all been compiled into .txt files and commited to Git!"; \
	  git status --porcelain requirements*.txt; \
	  exit 1; \
	fi

testcase:
	# support extra verbosity in testcases so differences can be copy-pasted when needed and to see exactly
	# what is happening.
	# make testcase case=filter condition
	${dev} "pytest -vvv -k ${case} ./tests/"

# updates requirements.txt files when requirements.in files have changes
requirements_files = $(subst .in,.txt,$(wildcard requirements*.in))
requirements: ${requirements_files}
${requirements_files}: %.txt: %.in
	${dev} "pip-compile $< --output-file $@"

# build docker container images
.PHONY: build
build:
	docker compose build ${build_args}

push_images:
	docker compose --push app certstream

# remove all runtime state and cache from the project
mrproper:
	docker compose rm --volumes --force --stop
	docker system prune --filter label=com.docker.compose.project=${project_name} --all --force --volumes
	rm -fr build/ src/*.egg-info
