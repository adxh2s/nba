import json
import os
from pathlib import Path

import pytest
import yaml
from packages.tools import file_tools_proc


def test_load_from_json_and_yaml(tmp_path: Path):
    # Créer fichier JSON temporaire
    json_path = tmp_path / "test.json"
    data_json = {"key": "value"}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_json, f)

    # Créer fichier YAML temporaire
    yaml_path = tmp_path / "test.yaml"
    data_yaml = {"key": "value"}
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data_yaml, f)

    # Test load_from_json
    content_json = file_tools_proc.load_from_json(str(json_path))
    assert content_json == data_json

    # Test load_from_yaml
    content_yaml = file_tools_proc.load_from_yaml(str(yaml_path))
    assert content_yaml == data_yaml

    # Test load_from avec extension json
    assert file_tools_proc.load_from(str(json_path)) == data_json

    # Test load_from avec extension yaml
    assert file_tools_proc.load_from(str(yaml_path)) == data_yaml

    # Test load_from extension invalide
    bad_path = tmp_path / "file.txt"
    with open(bad_path, "w") as f:
        f.write("test")
    with pytest.raises(ValueError):
        file_tools_proc.load_from(str(bad_path))


def test_is_path_in_root(tmp_path: Path):
    root = str(tmp_path)
    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    file_path = sub_dir / "file.txt"
    file_path.touch()

    assert file_tools_proc.is_path_in_root(str(file_path), root) is True
    assert file_tools_proc.is_path_in_root("/not/in/root", root) is False


def test_build_file_path():
    assert file_tools_proc.build_file_path(
        "dir", "file", "txt"
    ) == os.path.join("dir", "file.txt")
    assert file_tools_proc.build_file_path("", "file", ".json") == "file.json"
    assert file_tools_proc.build_file_path(None, "file", "csv") == "file.csv"


def test_build_project_tree_and_get_node_path(tmp_path: Path):
    structure = {
        "docs": {
            "type": "folder",
            "content": {
                "reports": {
                    "type": "folder",
                    "content": {
                        "html": {
                            "type": "folder",
                            "pattern": "*.html",
                            "description": "Rapports HTML",
                            "content": [],
                        }
                    },
                }
            },
        }
    }
    base_path = str(tmp_path)
    tree = file_tools_proc.build_project_tree(base_path, structure)
    assert "docs" in tree
    path = file_tools_proc.get_node_path(tree, "docs", "reports", "html")
    expected_path = os.path.join(base_path, "docs", "reports", "html")
    assert path == expected_path

    # test key error
    with pytest.raises(KeyError):
        file_tools_proc.get_node_path(tree, "docs", "missing")


def test_format_report_filename():
    template = "{date:%Y%m%d%H%M}_{input}_report.html"
    name = "mydata.csv"
    filename = file_tools_proc.format_report_filename(template, name)
    assert filename.startswith("20") and filename.endswith(
        "_mydata_report.html"
    )


def test_get_config_param():
    dict_app = {"param1": "value1"}
    project_structure = {
        "docs": {
            "children": {
                "reports": {
                    "children": {"html": {"param2": "value2", "path": "/tmp"}},
                    "path": "/tmp/reports",
                }
            },
            "path": "/tmp/docs",
        }
    }

    assert (
        file_tools_proc.get_config_param(
            "param1", dict_app, project_structure, "docs", "reports", "html"
        )
        == "value1"
    )
    assert (
        file_tools_proc.get_config_param(
            "param2", {}, project_structure, "docs", "reports", "html"
        )
        == "value2"
    )
    with pytest.raises(KeyError):
        file_tools_proc.get_config_param(
            "missing", {}, project_structure, "docs", "reports", "html"
        )
