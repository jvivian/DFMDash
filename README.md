# DFMDash

> Easily drag-and-drop to build, run, and explore Dynamic Factor models in a browser-based GUI

[![Release](https://img.shields.io/github/v/release/jvivian/DFMDash)](https://img.shields.io/github/v/release/jvivian/DFMDash)
[![Build status](https://img.shields.io/github/actions/workflow/status/jvivian/DFMDash/main.yml?branch=main)](https://github.com/jvivian/DFMDash/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/jvivian/DFMDash/graph/badge.svg?token=RVT01PK8TT)](https://codecov.io/gh/jvivian/DFMDash)
[![Commit activity](https://img.shields.io/github/commit-activity/m/jvivian/DFMDash)](https://img.shields.io/github/commit-activity/m/jvivian/DFMDash)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

`DFMDash` is an open-source tool for running **Dynamic Factor Models (DFMs)**, primarily focused on pandemic intensity estimation through a combination of macroeconomic and epidemiological time-series data. `DFMDash` simplifies the process of building dynamic factor models using a user-friendly **`Streamlit`-based dashboard**, allowing researchers and policy makers to evaluate and compare pandemic dynamics across time and geography.

Designed initially for evaluating the impacts of **COVID-19**, `DFMDash` is flexible enough to be adapted to other pandemics or scenarios requiring dynamic factor models. The tool provides capabilities for:

- Running DFMs with custom datasets or using pre-loaded COVID-19 economic data.
- Visualizing factor analysis results.
- Performing comparative run analysis.
- Implementing synthetic control models for policy impact evaluation.

See our [Documentation](https://jvivian.github.io/DFMDash/) page for API details.

## Key Features

- **Dynamic Factor Models**: Build models that combine pandemic and economic series to estimate latent variables representing pandemic intensity.
- **Drag-and-Drop**: Drop in files - options are then dynamically generated from the input data.

## Installation

There are multiple ways to install and run `DFMDash`.

> **Note**: Due to PyPI constraints, the example data files are stored on the GitHub repository rather than in the pip-installed package. If you wish to use `DFMDash` with the provided example data, please clone the repository and follow the installation steps below.

### Prerequisites

- Python 3.10+ is required.
- Tested environments: **Ubuntu**, **WSL2 (Windows)**, **MacOS** (M1 compatible).

### Option 0: Using Pip

> **Advanced:** If you have a Python environment set up, prefer to install via `pip` and _do not_ want/need the example data.

1. Install the package:
   ```bash
   pip install dfmdash
   ```

### Option 1: Using Poetry

0. [Install Poetry](https://python-poetry.org/)

1. Clone the repository and move into the directory:

   ```bash
   git clone https://github.com/jvivian/DFMDash/
   cd DFMDash
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Launch the DFMDash dashboard:
   ```bash
   dfmdash launch
   ```
   or
   ```bash
   poetry run dfmdash launch
   ```

### Option 2: Using Anaconda / Mamba

> Convenient if Anaconda/Miniconda/Mamba already installed

0. [Install Anaconda](https://docs.anaconda.com/anaconda/install/)

1. Clone the repository:

   ```bash
   git clone https://github.com/jvivian/DFMDash/
   cd DFMDash
   ```

2. Create and activate the environment:

   ```bash
   conda env update -f environment.yml
   conda activate py3.10
   ```

3. Install dependencies:

   ```bash
   poetry install
   ```

4. Launch DFMDash:
   ```bash
   dfmdash launch
   ```

### Option 3: Using Docker (recommended if you have permissions)

Run the pre-built image:

```bash
docker run -p 8501:8501 jvivian/dfmdash
```

Or, build locally:

```bash
docker build -t dfmdash .
docker run -p 8501:8501 jvivian/dfmdash
```

Then, open your browser to `localhost:8501`.

## Usage

After installation, launch the tool by typing:

```bash
dfmdash launch
```

This will open the Streamlit dashboard in your default browser. From the dashboard, users can:

- **Main Page**: Select data series and define the dynamic factor model specifications.
  ![Dynamic Factor Model Runner](imgs/DFM.png)

- **Factor Analysis Page**: Review and visualize latent factor estimates based on the selected inputs.
  ![Analyze factors directly after generation](imgs/factor.png)

- **Comparative Run Analysis**: Compare different model runs to evaluate fit and consistency.
  ![Quantitatively compare models using different metrics](imgs/CA.png)

- **Synthetic Control Model Page** (Experimental): Test SCMs with user-defined counterfactuals.
  > Work in progress

## Troubleshooting

- If the dashboard does not automatically open, check the console where you typed the command. It should tell you what address the dashboard is being hosted at locally.
- If you encounter any bugs or issues while using the tool, feel free to [open an issue](https://github.com/jvivian/DFMDash/issues). Please try and provide as much detail (and the data if possible) to recreate the issue.

## Development

To contribute to `DFMDash`, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/jvivian/DFMDash/
   cd DFMDash
   ```

2. Set up the development environment:
   ```bash
   make install
   ```

This will:

- Install the virtual environment at `.venv/bin/python`.
- Set up pre-commit hooks for linting and formatting checks.

3. To run tests:

   ```bash
   pytest
   ```

4. Pre-commit hooks will automatically check for linting and formatting issues on each commit.

### CI/CD Pipeline

- CI pipeline is set up using **GitHub Actions**.
- On pull requests, merges to `main`, or releases, the pipeline will:
  - Run unit tests.
  - Check code quality with **black** and **ruff**.
  - Report code coverage via **codecov**.

## Documentation

Documentation is built using **MkDocs**. To generate the documentation locally, run:

```bash
mkdocs serve
```

<!-- Official documentation can be found [here](https://jvivian.github.io/DFMDash). -->

## Contributions

We welcome contributions to `DFMDash`! Please ensure that:

- All new code includes tests (if code coverage decreases, it will likely be rejected)
- Any modifications to the dashboard interface are reflected in the documentation.

For larger changes, please open an issue for discussion before submitting a PR.

## License

`DFMDash` is distributed under the MIT License. See [LICENSE](./LICENSE) for details.

# Citation

> If you use this tool in your research, please cite the following paper

```
Cooke, A., & Vivian, J. (2024). Pandemic Intensity Estimation using Dynamic Factor Modelling. Statistics, Politics and Policy. Manuscript under review.
```
