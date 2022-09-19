# pyscaffold-eric-extension

Attempting to create an extension for the production python course

## Usage

Just install this package with `pip install ${project}` and note that `putup -h` shows a new option `--eric_ext`. Use this flag to ...

```bash
#!/bin/bash

# git clone <this repo>
# pip install -e /path/to/where/you/cloned/<this repo>

PARENT_DIR_NAME="my-cool-package"

putup ./$PARENT_DIR_NAME/ \
    --name "my-cool-package" \
    --package "my_cool_pkg" \
    --description "A description for your package" \
    --license MIT \
    --url "https://ericriddoch.info" \
    --github-actions \
    --venv ./venv/ \
    --force \
    --very-verbose \
    --eric-ext

# By inheriting from pyscaffold.extensions.Extension, a default CLI option that 
# already activates the extension will be created, based on the dasherized version 
# of the name in the setuptools entry point. In the example above, the automatically 
# generated option will be --awesome-files.
```


## Making Changes & Contributing


This project uses [pre-commit](https://pre-commit.com/), please make sure to install it before making any
changes:

```bash
pip install pre-commit
cd pyscaffoldext-pyscaffold-eric-extension
pre-commit install
```

It is a good idea to update the hooks to the latest version::

```bash
pre-commit autoupdate
```

Don't forget to tell your contributors to also install and use pre-commit.

## Note

This project has been set up using PyScaffold 4.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
