from typing import Any

from pydantic import BaseModel, Extra


class RootMetaSchema(BaseModel):
    """
    Schéma Pydantic pour la section racine ('root') du fichier
    project_structure.yaml ou JSON.

    Attributs :
        name (str) : Nom de la racine du projet. Obligatoire.
        app_name (Optional[str]) : Nom de l'application. Facultatif.
        structure (Dict[str, Any]) : Structure détaillée du projet,
        sous forme de dictionnaire.
    """

    name: str
    app_name: str | None
    structure: dict[str, Any]

    class Config:
        extra = Extra.forbid
        # Interdit les champs supplémentaires inconnus afin d'éviter
        # erreurs silencieuses
