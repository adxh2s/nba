import os

import pandas as pd
from ydata_profiling import ProfileReport


def enrich_dataframe_for_ydata(
    df: pd.DataFrame, description_schema: dict
) -> pd.DataFrame:
    """
    Crée un DataFrame temporaire avec une ligne supplémentaire contenant
    les descriptions
    (commentaires) des colonnes issues du schema JSON.

    Args:
        df (pd.DataFrame): DataFrame initial.
        description_schema (dict): Description JSON, avec clé "columns".

    Returns:
        pd.DataFrame: Nouveau DataFrame enrichi, original préservé.
    """
    if not description_schema or "columns" not in description_schema:
        return df.copy()

    descr_map = {
        col: description_schema["columns"][col].get("description")
        or description_schema["columns"][col].get("commentaire")
        or ""
        for col in df.columns
        if col in description_schema["columns"]
    }

    descr_row = {col: descr_map.get(col, "") for col in df.columns}

    df_copy = df.copy()
    df_descr = pd.DataFrame([descr_row])
    df_descr.index = [-1]  # ligne 'description' en premier

    df_enriched = pd.concat([df_descr, df_copy], ignore_index=False)
    df_enriched = df_enriched.sort_index().reset_index(drop=True)

    return df_enriched


def generate_report(
    df: pd.DataFrame,
    output_path: str,
    title: str = None,
    description_schema: dict = None,
):
    """
    Génère un rapport HTML complet avec ydata-profiling,
    en intégrant les descriptions des colonnes si fournies.
    Le titre du rapport est personnalisé.

    Args:
        df (pd.DataFrame): DataFrame d’analyse.
        output_path (str): Chemin du fichier HTML de sortie.
        title (str, optional): Titre du rapport. Par défaut, pris depuis le
        nom du fichier output_path.
        description_schema (dict, optional): Description JSON des colonnes.

    Returns:
        None. Sauvegarde le rapport HTML.
    """
    if title is None:
        title = os.path.splitext(os.path.basename(output_path))[0]

    variables = {}
    if description_schema:
        desc_cols = (
            description_schema.get("columns")
            or description_schema.get("column_descriptions")
            or {}
        )
        descriptions = {
            col: desc_cols.get(col, "")
            for col in df.columns
            if col in desc_cols
        }
        if descriptions:
            variables["descriptions"] = descriptions

    profile = ProfileReport(df, title=title, variables=variables)
    profile.to_file(output_path)
