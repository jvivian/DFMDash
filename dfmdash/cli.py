"""Command-Line Interface for project

Main command
    - `c19_dfm`

Help
    - `c19_dfm --help`

Process data and generate parquet DataFrame
    - `c19_dfm process ./outfile.xlsx`
"""

import subprocess
from pathlib import Path
from typing import Optional

import anndata as ann
import typer
from rich import print

from dfmdash.covid19 import get_project_h5ad
from dfmdash.dfm import ModelRunner
from dfmdash.io import DataLoader

app = typer.Typer()


@app.command("run")
def run_dfm(
    h5ad: Path,
    outdir: Path,
    batch: str = typer.Option(help="Name of column in h5ad.obs to use as batch variable"),
    global_multiplier: int = 1,
    maxiter: int = 10_000,
    update_h5ad: bool = True,
):
    ad = ann.read_h5ad(h5ad)
    model = ModelRunner(ad, outdir, batch)
    model.run(maxiter, global_multiplier)
    if update_h5ad:
        print(f"[bold green]:heavy_check_mark: Updating H5ad {h5ad}")
        model.ad.write_h5ad(h5ad)


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


@app.command("launch")
def launch(port: str = 8501):
    """
    Launch Dynamic Factor Dashboard
    """
    current_dir = Path(__file__).resolve().parent
    dashboard_path = current_dir / "streamlit" / "Dynamic_Factor_Model.py"
    subprocess.run(["streamlit", "run", dashboard_path, "--server.port", port])


if __name__ == "__main__":
    app()
