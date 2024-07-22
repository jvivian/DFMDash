# DFMDash

[![Release](https://img.shields.io/github/v/release/jvivian/DFMDash)](https://img.shields.io/github/v/release/jvivian/DFMDash)
[![Build status](https://img.shields.io/github/actions/workflow/status/jvivian/DFMDash/main.yml?branch=main)](https://github.com/jvivian/DFMDash/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/jvivian/DFMDash/graph/badge.svg?token=RVT01PK8TT)](https://codecov.io/gh/jvivian/DFMDash)
[![Commit activity](https://img.shields.io/github/commit-activity/m/jvivian/DFMDash)](https://img.shields.io/github/commit-activity/m/jvivian/DFMDash)
[![License](https://img.shields.io/github/license/jvivian/DFMDash)](https://img.shields.io/github/license/jvivian/DFMDash)

Repository for Covid-19 Dynamic Factor Model

- **Github repository**: <https://github.com/jvivian/DFMDash/>
- **Documentation** <https://jvivian.github.io/DFMDash/>

# Quickstart
> Tested on Ubuntu, Windows WSL2: Ubuntu, and Mac OSX (M1)

## Python
- Download and install [Anaconda]() to your PATH and run:

```bash
git clone https://github.com/jvivian/DFMDash/ # Get source code
cd DFMDash
conda env update -f environment.yml  # Create python env for project
conda activate py3.10  # Activate env
poetry install  # Install dependencies and package
c19dfm --help  # Run tool's help message
```

## Docker

`docker run jvivian/covid19-dfm`

or to build locally

```bash
git clone https://github.com/jvivian/DFMDash/ # Get source code
cd DFMDash
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
