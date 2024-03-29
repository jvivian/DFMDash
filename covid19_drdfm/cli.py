"""Command-Line Interface for project

Main command
    - `c19_dfm`

Help
    - `c19_dfm --help`

Process data and generate parquet DataFrame
    - `c19_dfm process ./outfile.xlsx`
"""
import anndata as ann

import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich import print

from covid19_drdfm.covid19 import get_project_h5ad

from covid19_drdfm.io import DataLoader
from covid19_drdfm.dfm import ModelRunner

app = typer.Typer()


@app.command("run")
def run_dfm(
    h5ad: Path,
    outdir: Path,
    batch: str = typer.Option(help="Name of column in h5ad.obs to use as batch variable"),
    global_multiplier: int = 1,
    maxiter: int = 10_000,
):
    ad = ann.read_h5ad(h5ad)
    model = ModelRunner(ad, outdir, batch)
    model.run(maxiter, global_multiplier)


@app.command("create_input_data")
def create_input_h5ad(
    h5ad_out: Path,
    data_path: Path,
    factor_path: Path,
    metadata_path: Optional[Path] = typer.Option(help="Path to metadata (needed if batching data)"),
):
    """
    Convert data, factor, and metadata CSVs to H5AD and save output

    Example: c19dfm create_input_h5ad data.h5ad ./data.csv ./factors.csv --metadata ./metadata.csv
    """
    print(f"Creating H5AD at {h5ad_out}")
    data = DataLoader().load(data_path, factor_path, metadata_path)
    data.write_h5ad(h5ad_out)


@app.command("create_covid_project_data")
def create_project_data(outdir: Path):
    """
    Create H5AD object of covid19 response and economic data
    """
    ad = get_project_h5ad()
    ad.write(outdir / "data.h5ad")
    print(f"Project data successfully created at {outdir}/data.h5ad !")


@app.command("launch_dashboard")
def launch_dashboard():
    """
    Launch the Dashboard
    """
    current_dir = Path(__file__).resolve().parent
    dashboard_path = current_dir / "streamlit" / "Dashboard.py"
    subprocess.run(["streamlit", "run", dashboard_path])
