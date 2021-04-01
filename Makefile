PACKAGE=dist/$(shell ls dist | tail -n 1)
TWINE_USERNAME ?=
TWINE_PASSWORD ?=

install:
	poetry update

test:
	poetry run pytest

clean:
	rm -rf build dist

build: clean
	poetry build

deploy: build
	poetry publish
