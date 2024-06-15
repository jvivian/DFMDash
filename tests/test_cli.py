import shutil
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dfmdash.cli import app
from dfmdash.covid19 import DATA_DIR

runner = CliRunner()

# TODO: Change to be test.h5ad with small state subset
def test_run_dfm(tmpdir):
    result = runner.invoke(app, ["run", str(DATA_DIR / "test.h5ad"), str(tmpdir), "--batch", "State"])
    assert result.exit_code == 0
    assert (Path(tmpdir) / "AK").exists()


def test_create_input_h5ad(tmpdir):
    data_path = DATA_DIR / "data.csv"
    factor_path = DATA_DIR / "factors.csv"
    metadata_path = DATA_DIR / "metadata.csv"
    result = runner.invoke(
        app,
        [
            "create_input_data",
            f"{tmpdir}/test.h5ad",
            str(data_path),
            str(factor_path),
            "--metadata-path",
            str(metadata_path),
        ],
    )
    assert result.exit_code == 0


def test_create_project_data(tmpdir):
    result = runner.invoke(app, ["create_covid_project_data", str(tmpdir)])
    assert result.exit_code == 0


#! Dashboard is not easily testable
# def test_launch_dashboard():
#     result = runner.invoke(app, ["launch_dashboard"])
#     assert result.exit_code == 0
#     assert "Launching dashboard..." in result.output
