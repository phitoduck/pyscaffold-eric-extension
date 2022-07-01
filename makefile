PACKAGE = pyscaffoldext/eric_ext

install:
	python -m pip install -e .[dev]

build-package:
	python -m build \
		--outdir ./dist/ \
		--wheel \
		--sdist

validate-readme-for-pypi:
	twine check ./dist/*

# you'll need to create an account at https://test.pypi.org
# and verify your email address

# If you get this error, you need to stash your changes or run this from CI:
# HTTPError: 400 Bad Request from https://test.pypi.org/legacy/
# '0.0.post1.dev1+g69b2d70.d20220629' is an invalid value for Version.
# Error: Can't use PEP 440 local versions. See https://packaging.python.org/specifications/core-metadata
# for more information.

# we may consider just moving this into the github actions yaml;
# local users would almost never be able to run this successfully.
# we'll just show users how to add github secrets
publish-package-to-test-pypi:
	twine upload ./dist/* \
		--repository-url https://test.pypi.org/legacy/ \
		--username eriddoch \
		--password 'Qyv0rZEOL!OstAwcPy4A'

get-local-git-version:
	python setup.py --version

clean:
	rm -rf ./dist/
	rm -rf ./.pytest_cache/
	rm -rf src/*.egg-info
	rm -rf src/$(PACKAGE)/*__pycache__
	rm -rf ./build/ ./dist/ ./docs/_build/
	rm .coverage
