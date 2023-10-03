"""Command-Line Interface for project

Main command
    - `c19_dfm`
Help
    - `c19_dfm --help`
Process data and generate parquet DataFrame
    - `c19_dfm process ./outfile.parq`


"""
from pathlib import Path

import typer

from covid19_drdfm.processing import run, write

app = typer.Typer()


class PreprocessingFailure(Exception):
    """Raised when preprocessing has failed"""

    pass


@app.command("run")
def run_state_model(parquet_path: str, outdir: str):
    print(parquet_path)
    print(outdir)
    pass


@app.command("process")
def process_data(output_file: str):
    """
    Process input data into single `outfile.{xlsx|csv|parquet}` DataFrame
    """
    try:
        df = run()
        write(df, Path(output_file))
    except PreprocessingFailure as e:
        typer.echo(f"Preprocessing Failed: {e}")
    # try:
    #     fastparquet.write(output_file, df)
    #     typer.echo(f"Data processed successfully and saved to {output_file}.")
    # except Exception as e:
    #     typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()
