from pathlib import Path
from typing import Optional

import fastparquet
import pandas as pd
from anndata import AnnData


def parse_csvs_to_ad(data: Path, factors: Path, metadata: Optional[Path]) -> AnnData:
    """
    Parses the input numerical data, factors variable, and observational metadata
    to create an AnnData object.

    Parameters:
        data (str): Path to the numerical data CSV file.
        factors (str): Path to the factors variable CSV file.
        metadata (Optional[str]): Path to the observational metadata CSV file.

    Returns:
        AnnData: The created AnnData object.
    """
    data_df = pd.read_csv(data)
    factors_df = pd.read_csv(factors, index_col=0)
    metadata_df = pd.read_csv(metadata, index_col=0) if metadata else None
    return dfs_to_ad(data_df, factors_df, metadata_df)


def dfs_to_ad(data: pd.DataFrame, factors: pd.DataFrame, metadata: Optional[pd.DataFrame]) -> AnnData:
    """
    Parses the input numerical data, factors variable, and observational metadata
    to create an AnnData object.

    Parameters:
        data (pd.DataFrame): The numerical data DataFrame.
        factors (pd.DataFrame): The factors variable DataFrame.
        metadata (Optional[pd.DataFrame]): The observational metadata DataFrame.

    Returns:
        AnnData: The created AnnData object.
    """
    return AnnData(X=data, obs=metadata, var=factors)


def write_df(df: pd.DataFrame, outpath: Path) -> None:
    """
    Write a pandas DataFrame to a file.

    Parameters:
        df (pd.DataFrame): The DataFrame to be written.
        outpath (Path): The path to the output file.

    Raises:
        OSError: If the file extension is not supported.

    Returns:
        None
    """
    ext = outpath.suffix
    if ext == ".xlsx":
        df.to_excel(outpath)
    elif ext == ".csv":
        df.to_csv(outpath)
    elif ext == ".parq" or ext == ".parquet":
        fastparquet.write(df, outpath)
    elif ext == ".tsv":
        df.to_csv(outpath, sep="\t")
    else:
        raise OSError
