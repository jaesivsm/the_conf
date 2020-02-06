PACKAGE=dist/$(shell ls dist | tail -n 1)
TWINE_USERNAME ?=
TWINE_PASSWORD ?=

install:
	pipenv sync --dev

test:
	pipenv run python setup.py test

clean:
	rm -rf build dist
	pipenv run python setup.py clean

build: clean
	pipenv run python setup.py sdist

deploy: build
	pipenv run twine upload $(PACKAGE)
