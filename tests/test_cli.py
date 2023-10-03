import os
from pathlib import Path

from typer.testing import CliRunner

from covid19_drdfm.cli import app

runner = CliRunner()


def test_process():
    res = runner.invoke(app, ["process", "test.xlsx"])
    path = Path("./test.xlsx")
    assert res.exit_code == 0
    assert path.exists()
    os.remove(path)


def test_run():
    res = runner.invoke(app, ["run", "foo.parquet", "outdir"])
    assert res.exit_code == 0
