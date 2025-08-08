@echo off
REM Usage : run_script.bat script_name.py [args...]

REM Chemin absolu vers le dossier src
set "SRC_DIR=%~dp0src"

REM Nom du script à exécuter (ex : load_data_from_api.py)
set SCRIPT_NAME=%1
shift

if "%SCRIPT_NAME%"=="" (
    echo Usage: %0 script_name.py [args...]
    exit /b 1
)

REM Extraire nom module sans extension pour python -m
for %%I in (%SCRIPT_NAME%) do set SCRIPT_MODULE=%%~nI

REM Lancement avec python -m depuis src pour que "packages" soit racine
pushd "%SRC_DIR%"
python -m scripts.%SCRIPT_MODULE% %*
popd
