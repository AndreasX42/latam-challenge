.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")

.PHONY: help
help:             	## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: venv
venv:			## Create a virtual environment
	@echo "Creating virtualenv ..."
	@rm -rf .venv
	@python3 -m venv .venv
	@./.venv/bin/pip install -U pip
	@echo
	@echo "Run 'source .venv/bin/activate' to enable the environment"

.PHONY: install
install:		## Install dependencies
	pip install -r requirements-dev.txt
	pip install -r requirements-test.txt
	pip install -r requirements.txt

STRESS_URL = http://34.42.13.236/test/api
.PHONY: stress-test
stress-test:
	# change stress url to your deployed app 
	mkdir reports/stress || true
		locust -f tests/stress/api_stress.py --print-stats --html reports/stress/stress-test.html --run-time 60s --headless --users 100 --spawn-rate 1 -H $(STRESS_URL)

.PHONY: model-test
model-test:			## Run tests and coverage
	mkdir reports/model || true
		pytest --cov-config=.coveragerc --cov-report term --cov-report html:reports/model/html --cov-report xml:reports/model/coverage.xml --junitxml=reports/model/junit.xml --cov=challenge tests/model

.PHONY: api-test
api-test:			## Run tests and coverage
	mkdir reports/api || true
		pytest --cov-config=.coveragerc --cov-report term --cov-report html:reports/api/html --cov-report xml:reports/api/coverage.xml --junitxml=reports/api/junit.xml --cov=challenge tests/api
		
.PHONY: build
build:			## Build locally the python artifact
	python setup.py bdist_wheel

.PHONY: local-tests
local-tests: model-test api-test