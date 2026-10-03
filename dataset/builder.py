"""
Module for LoLdle analysis.

Users may run this to create a dataset (CSV) with the most
recent LoLdle properties and work with the `loldle_df`
(Pandas DataFrame) below.
"""
from pathlib import Path
import json

import pandas as pd

from solver.utils import paths
from solver.champ_pipeline.loader import load_champions, create_champions_json
from solver.champ_pipeline.champions import Champion


def create_csv_metrics(load: Path, output: Path) -> None:
    """
    Fetch the most recent LoLdle properties and write data
    to a CSV file and store it in the `results` directory.
    """
    # ----------------------------
    # Load data
    # ----------------------------
    create_champions_json(load, overwrite=True)
    champions = load_champions(load)

    # ----------------------------
    # Build table
    # ----------------------------
    with open(load, "r") as f:
        champions_json = json.load(f)
        champion_data = champions_json["champions"]

    df = pd.DataFrame.from_dict(champion_data)

    properties = list(Champion.properties())
    champ_map = {champ.name: champ for champ in champions}

    df = df.rename(columns={"championName": "champion"})

    for prop in properties:
        df[prop] = df["champion"].map(
            lambda name: _serialize_value(getattr(champ_map[name], prop))
        )

    df = df.sort_values("champion")[["champion"] + properties]

    # ----------------------------
    # Save
    # ----------------------------
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)


def _serialize_value(v):
    if v is None:
        return None
    if isinstance(v, frozenset):
        return json.dumps(sorted(v))
    return v


if __name__ == "__main__":
    output_path = paths.results / "loldle_dataset.csv"
    create_csv_metrics(load=paths.champion_data, output=output_path)

    loldle_df = pd.read_csv(output_path)

    # Can do analysis with 'loldle_df'
