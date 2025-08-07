import os
from pathlib import Path
from typing import Literal

import pandas as pd
import pytest
from modules.utils import data_tools


def test_generate_report_creates_file_and_title(tmp_path: Path):
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})

    output_file = tmp_path / "report.html"

    # Test avec title fourni
    title = "Mon Rapport"
    data_tools.generate_report(df, str(output_file), title=title)
    assert output_file.exists()
    with open(output_file, encoding="utf-8") as f:
        content = f.read()
    assert "<html" in content.lower()
    assert title in content

    # Test sans title (doit prendre nom fichier)
    output_file2 = tmp_path / "rapport2.html"
    data_tools.generate_report(df, str(output_file2))
    assert output_file2.exists()
    with open(output_file2, encoding="utf-8") as f:
        content2 = f.read()
    assert os.path.splitext(os.path.basename(output_file2))[0] in content2


def test_generate_report_with_column_descriptions(tmp_path: Path):
    df = pd.DataFrame({"A": [10, 20], "B": [30, 40]})

    description_schema_columns = {
        "columns": {"A": "Description colonne A", "B": "Description colonne B"}
    }

    description_schema_col_desc = {
        "column_descriptions": {
            "A": "Description colonne A",
            "B": "Description colonne B",
        }
    }

    output_file1 = tmp_path / "report1.html"
    output_file2 = tmp_path / "report2.html"

    # Avec "columns"
    data_tools.generate_report(
        df, str(output_file1), description_schema=description_schema_columns
    )
    assert output_file1.exists()
    with open(output_file1, encoding="utf-8") as f1:
        content1 = f1.read()
    # Vérifier qu'une des descriptions est présente dans le HTML
    assert "Description colonne A" in content1

    # Avec "column_descriptions"
    data_tools.generate_report(
        df, str(output_file2), description_schema=description_schema_col_desc
    )
    assert output_file2.exists()
    with open(output_file2, encoding="utf-8") as f2:
        content2 = f2.read()
    assert "Description colonne B" in content2


def test_generate_report_empty_description(tmp_path: Path):
    df = pd.DataFrame({"C": [1, 2, 3]})

    description_schema_empty = {}

    output_file = tmp_path / "report_empty.html"

    # Pas de description fournie, devrait fonctionner sans erreur
    data_tools.generate_report(
        df, str(output_file), description_schema=description_schema_empty
    )
    assert output_file.exists()


@pytest.mark.parametrize("desc_key", ["columns", "column_descriptions"])
def test_descriptions_ignored_if_column_missing(
    tmp_path: Path,
    desc_key: Literal["columns"] | Literal["column_descriptions"],
):
    df = pd.DataFrame({"X": [1], "Y": [2]})
    description_schema = {desc_key: {"Z": "description absente"}}
    output_file = tmp_path / "report_missing.html"
    # Devrait ignorer 'Z' et ne rien planter
    data_tools.generate_report(
        df, str(output_file), description_schema=description_schema
    )
    assert output_file.exists()
