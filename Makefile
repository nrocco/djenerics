PACKAGE ?= djenerics
VIRTUAL_ENV ?= $(PWD)/env

PY = $(VIRTUAL_ENV)/bin/python


$(PY):
	virtualenv env
	$(eval VIRTUAL_ENV = $(PWD)/env)


build: $(PY) clean
	$(PY) setup.py sdist


upload: $(PY) clean
	$(PY) setup.py sdist register upload


bump:
	@echo "Current $(PACKAGE) version is: $(shell sed -E "s/__version__ = .([^']+)./\\1/" $(PACKAGE)/__init__.py)"
	@test ! -z "$(version)" || ( echo "specify a version number: make bump version=X.X.X" && exit 1 )
	@! git status --porcelain 2> /dev/null | grep -v "^??" || ( echo 'uncommited changes. commit them first' && exit 1 )
	@echo "Bumping to $(version)"
	sed -i'.bak' -e "/^__version__ = .*$$/s/'[^']*'/'$(version)'/" $(PACKAGE)/__init__.py
	rm -f $(PACKAGE)/__init__.py.bak
	git add $(PACKAGE)/__init__.py
	git commit -m 'Bumped version number to $(version)'
	git tag $(version)
	@echo "Version $(version) commited and tagged. Don't forget to push to github."
	@echo
	@echo "git push origin master && git push origin $(version)"


clean:
	rm -rf .tox *.egg dist build .coverage
	find $(PACKAGE) -name '__pycache__' -delete -print -o -name '*.pyc' -delete -print
