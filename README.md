# covid19-drDFM

[![Release](https://img.shields.io/github/v/release/jvivian/covid19-drDFM)](https://img.shields.io/github/v/release/jvivian/covid19-drDFM)
[![Build status](https://img.shields.io/github/actions/workflow/status/jvivian/covid19-drDFM/main.yml?branch=main)](https://github.com/jvivian/covid19-drDFM/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/jvivian/covid19-drDFM/branch/main/graph/badge.svg)](https://codecov.io/gh/jvivian/covid19-drDFM)
[![Commit activity](https://img.shields.io/github/commit-activity/m/jvivian/covid19-drDFM)](https://img.shields.io/github/commit-activity/m/jvivian/covid19-drDFM)
[![License](https://img.shields.io/github/license/jvivian/covid19-drDFM)](https://img.shields.io/github/license/jvivian/covid19-drDFM)

Repository for Covid-19 Dynamic Factor Model

- **Github repository**: <https://github.com/jvivian/covid19-drDFM/>
- **Documentation** <https://jvivian.github.io/covid19-drDFM/>

# Quickstart
## Dependencies

- Python 3.10

> Tested on Ubuntu, Windows WSL2: Ubuntu, and Mac OSX (M1)

## Install and Run

Install `poetry` using `pipx` (recommended) or `pip`
```bash
pipx install poetry
poetry install
```

If not already inside a virtualenv, one will be created at `./venv`


{% note %}

**Note:** If you don't have Python 3.10, download [Anaconda]() and run

{% endnote%}

```bash
conda env update -f environment.yml
conda activate py3.10
poetry install
```

# Development

Install the environment and the pre-commit hooks using `make`

```bash
make install
```

- The virtual environment will be created locally at `.venv/bin/python`
- CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.
