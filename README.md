# Carpet - Concentrations

<!--- sec-begin-description -->

Core tools for the development of greenhouse gas concentration input files (i.e. flying carpets).

**Repository health :**
[![CI](https://github.com/climate-resource/Carpet-Concentrations/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/climate-resource/Carpet-Concentrations/actions/workflows/ci.yaml)
[![Coverage](https://codecov.io/gh/climate-resource/Carpet-Concentrations/branch/main/graph/badge.svg)](https://codecov.io/gh/climate-resource/Carpet-Concentrations)
[![Docs](https://readthedocs.org/projects/carpet-concentrations/badge/?version=latest)](https://carpet-concentrations.readthedocs.io)

**PyPI :**
[![PyPI](https://img.shields.io/pypi/v/carpet-concentrations.svg)](https://pypi.org/project/carpet-concentrations/)
[![PyPI: Supported Python versions](https://img.shields.io/pypi/pyversions/carpet-concentrations.svg)](https://pypi.org/project/carpet-concentrations/)
[![PyPI install](https://github.com/climate-resource/Carpet-Concentrations/actions/workflows/install.yaml/badge.svg?branch=main)](https://github.com/climate-resource/Carpet-Concentrations/actions/workflows/install.yaml)

**Other info :**
[![License](https://img.shields.io/github/license/climate-resource/carpet-concentrations.svg)](https://github.com/climate-resource/carpet-concentrations/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/climate-resource/carpet-concentrations.svg)](https://github.com/climate-resource/carpet-concentrations/commits/main)
[![Contributors](https://img.shields.io/github/contributors/climate-resource/carpet-concentrations.svg)](https://github.com/climate-resource/carpet-concentrations/graphs/contributors)

<!---
Can use start-after and end-before directives in docs, see
https://myst-parser.readthedocs.io/en/latest/syntax/organising_content.html#inserting-other-documents-directly-into-the-current-document
-->

<!--- sec-end-description -->

Full documentation can be found at: [carpet-concentrations.readthedocs.io](https://carpet-concentrations.readthedocs.io). We recommend reading the docs there because the internal documentation links don't render correctly on GitHub's viewer.

## Installation

<!--- sec-begin-installation -->

Carpet - Concentrations can be installed with conda or pip:

```bash
pip install carpet-concentrations
conda install -c conda-forge carpet-concentrations
```

Additional dependencies can be installed using

```bash
# To add plotting dependencies
pip install carpet-concentrations[plots]
# To add notebook dependencies
pip install carpet-concentrations[notebooks]

# If you are installing with conda, we recommend
# installing the extras by hand because there is no stable
# solution yet (issue here: https://github.com/conda/conda/issues/7502)
```

<!--- sec-end-installation -->

### For developers

<!--- sec-begin-installation-dev -->

For development, we rely on [poetry](https://python-poetry.org) for all our
dependency management. To get started, you will need to make sure that poetry
is installed
([instructions here](https://python-poetry.org/docs/#installing-with-the-official-installer),
we found that pipx and pip worked better to install on a Mac).

For all of work, we use our `Makefile`.
You can read the instructions out and run the commands by hand if you wish,
but we generally discourage this because it can be error prone.
In order to create your environment, run `make virtual-environment`.

If there are any issues, the messages from the `Makefile` should guide you
through. If not, please raise an issue in the [issue tracker][issue_tracker].

For the rest of our developer docs, please see [](development-reference).

[issue_tracker]: https://gitlab.com/climate-resource/carpet-concentrations/issues

<!--- sec-end-installation-dev -->
