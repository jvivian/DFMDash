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

import pandas as pd
import typer
from rich import print

from covid19_drdfm.constants import DIFF_COLS, GROUPED_FACTORS, LOG_DIFF_COLS

# from covid19_drdfm.dfm import run_parameterized_model
from covid19_drdfm.processing import get_df, parse_csvs_to_ad, write_df

app = typer.Typer()


# # TODO: Change to support "batching" based on observational column (e.g. "State")
# @app.command("run")
# def run_dfm(
#     outdir: Path,
#     state: str = typer.Option("NY", help="State to run the model for"),
#     global_multiplier: int = 1,
#     maxiter: int = 10_000,
# ):
#     """Run Model"""
#     raw = get_df()
#     # ? Add multiprocessing step here
#     run_parameterized_model(raw, state, outdir, global_multiplier=global_multiplier, maxiter=maxiter)


@app.command("create_input_data")
def create_input_h5ad(output: Path, data_path: Path, factor_path: Path, metadata_path: Optional[Path]):
    """
    Convert data, factor, and metadata CSVs to H5AD and save output
    """
    parse_csvs_to_ad(data_path, factor_path, metadata_path).write(output)


@app.command("create_covid_project_data")
def create_project_data(outdir: Path):
    """
    Create H5AD object of covid19 response and economic data
    """
    df = get_df()
    data_path = outdir / "data.csv"
    meta_path = outdir / "metadata.csv"
    factor_path = outdir / "factors.csv"
    df.drop(columns=["Time", "State"]).to_csv(data_path, index=None)
    write_df(df.set_index("Time")[["State"]], meta_path)
    factors = pd.Series(GROUPED_FACTORS).to_frame(name="factor")
    factors.index.name = "variable"
    factors["difference"] = [x in DIFF_COLS for x in factors.index]
    factors["logdiff"] = [x in LOG_DIFF_COLS for x in factors.index]
    write_df(factors, factor_path)
    parse_csvs_to_ad(data_path, factor_path, meta_path).write(outdir / "data.h5ad")
    print(f"Project data successfully created at {outdir}/data.h5ad !")


@app.command("launch_dashboard")
def launch_dashboard():
    """
    Launch the Dashboard
    """
    current_dir = Path(__file__).resolve().parent
    dashboard_path = current_dir / "streamlit" / "Dashboard.py"
    subprocess.run(["streamlit", "run", dashboard_path])
