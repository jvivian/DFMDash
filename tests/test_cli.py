import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from covid19_drdfm.cli import PreprocessingFailure, app, process_data
from covid19_drdfm.processing import get_df

runner = CliRunner()


def test_process():
    res = runner.invoke(app, ["process", "test.xlsx"])
    path = Path("./test.xlsx")
    assert res.exit_code == 0
    assert path.exists()
    os.remove(path)
    with pytest.raises(PreprocessingFailure):
        process_data("/foo/bar/zoobar/file.pq")


def test_run():
    res = runner.invoke(app, ["run", "foo.parquet", "outdir"])
    assert res.exit_code == 0
