import logging
import os
import time
from pathlib import Path

import pytest
from modules.utils.logger_tools import init_logger, log_function_call


def test_init_logger_creates_file_and_logger(tmp_path: Path):
    """
    Teste que init_logger crée un logger valide et un fichier log dans le
    dossier spécifié.
    """
    log_dir = tmp_path / "logs"
    app_name = "testapp"
    script_name = "testscript"
    log_ext = "log"
    project_root = str(tmp_path)

    logger = init_logger(
        str(log_dir), app_name, script_name, log_ext, project_root
    )

    # Vérifier que la fonction retourne un logger
    assert isinstance(logger, logging.Logger)
    assert logger.name == app_name

    # Vérifier que le fichier log est bien créé dans le dossier
    files = list(log_dir.glob(f"*.{log_ext}"))
    assert len(files) == 1
    log_file = files[0]
    assert log_file.exists()

    # Vérifier que le fichier log contient la ligne d'initialisation
    with open(log_file, encoding="utf-8") as f:
        content = f.read()
    assert "Logger initialisé" in content


def test_init_logger_path_out_of_root_raises(tmp_path: Path):
    """
    Teste que init_logger lève une RuntimeError si le dossier ou
    fichier log n'est pas dans la racine projet.
    """
    # log_dir = tmp_path / "logs"
    app_name = "app"
    script_name = "script"
    project_root = str(tmp_path)

    # Test avec log_dir hors racine projet
    # (simulate avec chemin absolu différent)
    outside_dir = (
        "/tmp/logs_outside" if os.name != "nt" else "C:\\logs_outside"
    )

    # Ce test s'exécute seulement si outside_dir existe ou sous Unix
    if os.path.exists(outside_dir) or os.name != "nt":
        with pytest.raises(RuntimeError):
            init_logger(
                outside_dir, app_name, script_name, "log", project_root
            )

    # Le contrôle sur log_path (fichier) hors racine projet est difficile
    # à reproduire ici, car le nom de fichier est construit dans init_logger


def test_log_function_call_decorator_logs(caplog: pytest.LogCaptureFixture):
    """
    Teste que le décorateur log_function_call écrit bien les
    logs début et fin de fonction.
    """
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)

    @log_function_call(logger)
    def dummy_function(x, y):
        time.sleep(0.1)
        return x + y

    with caplog.at_level(logging.INFO):
        result = dummy_function(2, 3)

    assert result == 5

    logs = [record.getMessage() for record in caplog.records]

    assert any("Début de la fonction 'dummy_function'" in m for m in logs)
    assert any("Fin de la fonction 'dummy_function'" in m for m in logs)
