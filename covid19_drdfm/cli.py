"""Command-Line Interface for project

Main command
    - `c19_dfm`
Help
    - `c19_dfm --help`
Process data and generate parquet DataFrame
    - `c19_dfm process ./outfile.parq`


"""
import fastparquet
import typer

app = typer.Typer()


@app.command("run")
def run_state_model(parquet_path: str, outdir: str):
    print(parquet_path)
    print(outdir)
    pass


@app.command("process")
def process_data(output_file: str = "./outfile.parquet"):
    """
    Process input data into single `outfile.parquet` DataFrame
    """
    df = run()
    try:
        fastparquet.write(output_file, df)
        typer.echo(f"Data processed successfully and saved to {output_file}.")
    except Exception as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()
