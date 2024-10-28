from pathlib import Path

import pandas as pd
from rich import print


def parse_results(file_path: Path):
    """
    Parse the results file and extract the desired values.

    Parameters:
    file_path (Path): The path to the results file.

    Returns:
    pandas.DataFrame: A DataFrame containing the extracted values.
    """
    # Read the file
    with open(file_path) as file:
        lines = file.readlines()

    # Extract the desired values
    log_likelihood = float(lines[2].split(",")[3])
    aic = float(lines[3].split(",")[3])
    em_iterations = int(lines[6].split(",")[3])

    # Create a DataFrame
    df = pd.DataFrame({"Log Likelihood": [log_likelihood], "AIC": [aic], "EM Iterations": [em_iterations]})

    return df


def parse_run_results(directory: Path):
    """
    Parse the run results from a directory containing subdirectories with results.csv files.

    Parameters:
    directory (Path): The path to the directory containing the subdirectories with results.csv files.

    Returns:
    pandas.DataFrame: A DataFrame containing the parsed results from all subdirectories.

    """
    # Initialize an empty DataFrame
    all_results = []

    # Iterate through all subdirectories in the directory
    for path in directory.iterdir():
        if path.is_dir():
            # Get the state initials from the directory name
            state_initials = path.name

            # Apply parse_results to the results.csv file in the subdirectory
            path = path / "results.csv"
            if not path.exists():
                print(f"{state_initials} has no results!")
                continue
            df = parse_results(path)

            # Add the state initials as a column
            df["Batch"] = state_initials

            # Append the result to all_results
            all_results.append(df)

    return pd.concat(all_results, axis=0)


def parse_multiple_runs(directory: Path):
    """
    Parses the results of multiple runs stored in subdirectories of the given directory.

    Args:
        directory (Path): The directory containing the subdirectories with the run results.

    Returns:
        pd.DataFrame: A DataFrame containing the parsed results of all runs.
    """
    # Initialize an empty DataFrame
    all_runs = []

    # Iterate through all subdirectories in the directory
    for path in Path(directory).iterdir():
        if path.is_dir():
            # Get the run name from the directory name
            run_name = path.name

            # Apply parse_run_results to the subdirectory
            df = parse_run_results(path)

            # Add the run name as a column
            df["Run"] = run_name

            # Append the result to all_runs
            all_runs.append(df)

    return pd.concat(all_runs, axis=0)
