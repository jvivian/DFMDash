import fastparquet
import typer

from covid19_drdfm import run

app = typer.Typer()


@app.command()
def process_data(output_file: str = "./outfile.parq"):
    """
    Process the data.
    """
    df = run()
    try:
        fastparquet.write(output_file, df)
        typer.echo(f"Data processed successfully and saved to {output_file}.")
    except Exception as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()
