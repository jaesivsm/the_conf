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
