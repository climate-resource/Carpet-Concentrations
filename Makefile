# Makefile to help automate key steps

.DEFAULT_GOAL := help
TEMP_FILE := $(shell mktemp)

# A helper script to get short descriptions of each target in the Makefile
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([\$$\(\)a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-30s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


help:  ## print short description of each target
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: checks
checks:  ## run all the linting checks of the codebase
	@echo "=== pre-commit ==="; poetry run pre-commit run --all-files || echo "--- pre-commit failed ---" >&2; \
		echo "=== mypy ==="; MYPYPATH=stubs poetry run mypy src || echo "--- mypy failed ---" >&2; \
		echo "======"

.PHONY: black
black:  ## format the code using black
	poetry run black src tests docs/source/conf.py scripts docs/source/notebooks/*.py
	poetry run blackdoc src

.PHONY: ruff-fixes
ruff-fixes:  ## fix the code using ruff
	poetry run ruff src tests scripts docs/source/conf.py docs/source/notebooks/*.py --fix


.PHONY: test
test:  ## run the tests
	poetry run pytest src tests -r a -v --doctest-modules --cov=src

# Note on code coverage and testing:
# You must specify cov=src as otherwise funny things happen when doctests are
# involved.
# If you want to debug what is going on with coverage, we have found
# that adding COVERAGE_DEBUG=trace to the front of the below command
# can be very helpful as it shows you if coverage is tracking the coverage
# of all of the expected files or not.
# We are sure that the coverage maintainers would appreciate a PR that improves
# the coverage handling when there are doctests and a `src` layout like ours.

.PHONY: docs
docs:  ## build the docs
	poetry run sphinx-build -b html docs/source docs/build/html

.PHONY: check-commit-messages
check-commit-messages:  ## check commit messages
	poetry run cz check --rev-range HEAD

.PHONY: changelog-draft
changelog-draft:  ## compile a draft of the next changelog
	poetry run towncrier build --draft

.PHONY: licence-check
licence-check:  ## Check that licences of the dependencies are suitable
	poetry export --only=main --extras=cfxarray --extras=netcdf --extras=notebooks --extras=plots > $(TEMP_FILE)
	poetry run liccheck -r $(TEMP_FILE) -R licence-check.txt
	rm -f $(TEMP_FILE)

.PHONY: virtual-environment
virtual-environment:  ## update virtual environment, create a new one if it doesn't already exist
	poetry lock
	# Put virtual environments in the project
	poetry config virtualenvs.in-project true
	poetry install --all-extras
	poetry run pre-commit install
