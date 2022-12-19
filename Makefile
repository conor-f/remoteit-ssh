PYTHON=python3.8

ENV_DIR=.env_$(PYTHON)
IN_ENV=. $(ENV_DIR)/bin/activate &&

env: $(ENV_DIR)

clean:
	rm -fr build/
	rm -fr dist/

lint:
	black src/

build:
	$(IN_ENV) $(PYTHON) -m pip install --editable .
	rm -fr dist/
	$(IN_ENV) $(PYTHON) setup.py sdist bdist_wheel

setup:
	$(PYTHON) -m pip install --upgrade virtualenv
	$(PYTHON) -m virtualenv -p $(PYTHON) $(ENV_DIR)
	$(IN_ENV) $(PYTHON) -m pip install --upgrade -r requirements.txt
	$(IN_ENV) $(PYTHON) -m pip install --editable .


# CI Specific Rules:
ci_build:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install --user --upgrade -r requirements.txt
	$(PYTHON) -m pip install --user --editable .
	rm -fr dist/
	$(PYTHON) setup.py sdist

ci_deploy: ci_build
	$(PYTHON) -m pip install --user twine
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
