import os
from datetime import datetime


class FileUtils:
    """
    Divers utilitaires liés aux fichiers : construction de chemins,
    extraction de paramètres de config, formatage de noms, etc.
    """

    @staticmethod
    def build_file_path(
        dir_path: str | None, filename: str, extension: str
    ) -> str:
        """
        Construire un chemin complet de fichier.

        Args:
            dir_path: chemin du dossier, optionnel.
            filename: nom du fichier sans extension.
            extension: extension de fichier (avec ou sans point).

        Returns:
            Chemin complet du fichier.
        """
        if extension and not extension.startswith("."):
            extension = "." + extension
        full_filename = filename + extension
        if dir_path:
            return os.path.join(dir_path, full_filename)
        else:
            return full_filename

    @staticmethod
    def get_node_path(project_structure: dict, *keys: str) -> str:
        """
        Parcourir récursivement la dict project_structure via une séquence de
        clés pour retourner la valeur associée à la clé 'path' du nœud final.

        Args:
            project_structure: dictionnaire imbriqué de la structure projet.
            *keys: suite ordonnée de clés pour descendre dans la structure.

        Returns:
            Chemin de type str correspondant au nœud.

        Raises:
            KeyError si une clé n’est pas trouvée, ou si 'path' est absent.
        """
        node = project_structure
        for depth, key in enumerate(keys):
            if key not in node:
                raise KeyError(f"Clé '{key}' introuvable au niveau {depth}")
            node = node[key]
            if depth < len(keys) - 1:
                if "children" not in node:
                    raise KeyError(
                        f"Nœud '{key}' sans 'children' au niveau {depth}"
                    )
                node = node["children"]
        if "path" not in node:
            raise KeyError(f"Nœud final '{keys[-1]}' sans 'path'")
        return node["path"]

    @staticmethod
    def get_config_param(
        param_name: str,
        dict_app: dict,
        project_structure: dict,
        *path_keys: str,
    ) -> object:
        """
        Recherche un paramètre dans dict_app, puis dans la structure projet.

        Args:
            param_name: nom du paramètre recherché.
            dict_app: dictionnaire de config appli.
            project_structure: structure projet.
            *path_keys: chemin clé dans la structure projet.

        Returns:
            Valeur associée au paramètre.

        Raises:
            KeyError si le paramètre n’est pas trouvé.
        """
        if param_name in dict_app:
            return dict_app[param_name]
        try:
            node = project_structure
            for key in path_keys:
                node = node[key]
                if "children" in node:
                    node = node["children"]
            if param_name in node:
                return node[param_name]
        except KeyError:
            pass
        raise KeyError(
            f"Paramètre '{param_name}' introuvable dans dict_app "
            f"ou project_structure"
        )

    @staticmethod
    def format_report_filename(
        template: str, input_filename: str | None = None
    ) -> str:
        """
        Formater un nom de fichier rapport selon un template.

        Args:
            template: exemple '{date:%Y%m%d%H%M}_{input}_report.html'
            input_filename: fichier source optionnel pour utiliser son nom
            de base.

        Returns:
            Nom formatté en chaîne de caractères.
        """
        now = datetime.now()
        base_input = (
            os.path.splitext(os.path.basename(input_filename))[0]
            if input_filename
            else "report"
        )
        return template.format(date=now, input=base_input)
