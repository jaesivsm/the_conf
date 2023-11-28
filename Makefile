install:
	poetry update

test:
	@PYTHONPATH=$(PYTHONPATH):$(shell pwd) poetry run pytest

lint:
	@echo -n "mypy "
	@PYTHONPATH=$(PYTHONPATH):$(shell pwd) poetry run mypy the_conf
	@echo -n "pycodestyle "
	@PYTHONPATH=$(PYTHONPATH):$(shell pwd) poetry run pycodestyle the_conf
	@echo "done"
	@echo -n "black "
	@PYTHONPATH=$(PYTHONPATH):$(shell pwd) poetry run black --check the_conf

clean:
	rm -rf build dist

build: clean lint test
	poetry build

deploy: build
	poetry publish
	git tag $(shell poetry version -s)
	git push --tags
