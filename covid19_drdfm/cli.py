"""Command-Line Interface for project

Main command
    - `c19_dfm`

Help
    - `c19_dfm --help`

Process data and generate parquet DataFrame
    - `c19_dfm process ./outfile.xlsx`
"""
from pathlib import Path

import typer

from covid19_drdfm.dfm import run_model
from covid19_drdfm.processing import get_df, write

app = typer.Typer()


class PreprocessingFailure(Exception):
    """Raised when preprocessing has failed"""

    pass


@app.command("run")
def run_dfm(outdir: str):
    """Run Model"""
    raw = get_df()
    # ? Add multiprocessing step here
    state = "NY"
    run_model(raw, state, Path(outdir))


@app.command("process")
def process_data(output_file: str):
    """
    Process input data into single `outfile.{xlsx|csv|parquet}` DataFrame
    """
    try:
        df = get_df()
        write(df, Path(output_file))
    except Exception as e:
        raise PreprocessingFailure(f"preprocessing failed!: {e}") from e
