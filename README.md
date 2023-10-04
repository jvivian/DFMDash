# covid19-drDFM

[![Release](https://img.shields.io/github/v/release/jvivian/covid19-drDFM)](https://img.shields.io/github/v/release/jvivian/covid19-drDFM)
[![Build status](https://img.shields.io/github/actions/workflow/status/jvivian/covid19-drDFM/main.yml?branch=main)](https://github.com/jvivian/covid19-drDFM/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/jvivian/covid19-drDFM/graph/badge.svg?token=RVT01PK8TT)](https://codecov.io/gh/jvivian/covid19-drDFM)
[![Commit activity](https://img.shields.io/github/commit-activity/m/jvivian/covid19-drDFM)](https://img.shields.io/github/commit-activity/m/jvivian/covid19-drDFM)
[![License](https://img.shields.io/github/license/jvivian/covid19-drDFM)](https://img.shields.io/github/license/jvivian/covid19-drDFM)

Repository for Covid-19 Dynamic Factor Model

- **Github repository**: <https://github.com/jvivian/covid19-drDFM/>
- **Documentation** <https://jvivian.github.io/covid19-drDFM/>

# Quickstart
> Tested on Ubuntu, Windows WSL2: Ubuntu, and Mac OSX (M1)

## Python
- Download and install [Anaconda]() to your PATH and run:

```bash
git Vclone https://github.com/jvivian/covid19-drDFM/ # Get source code
cd covid19-drDFM
conda env update -f environment.yml  # Create python env for project
conda activate py3.10  # Activate env
poetry install  # Install dependencies and package
c19dfm --help  # Run tool's help message
```

## Docker

`docker run jvivian/covid19-dfm`

or to build locally

```bash
git clone https://github.com/jvivian/covid19-drDFM/ # Get source code
cd covid19-drDFM
docker build -t covid19-dfm .
docker run covid19-dfm
```

# Development

Clone repo and install the environment and the pre-commit hooks using `make`

```bash
make install
```

- The virtual environment will be created locally at `.venv/bin/python` (or you can use the conda env)
- CI pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.
- Pre-commit hooks will prevent and fix various linting errors

# Repository Features
- Poetry for dependency management
- CI with GitHub Actions
- Pre-commit hooks with pre-commit
- Code quality with black & ruff
- Testing and coverage with pytest and codecov
- Documentation with MkDocs
- Compatibility testing for multiple versions of Python with Tox
- Containerization with Docker
