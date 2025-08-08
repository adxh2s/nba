import os
from typing import Any


class PathUtils:
    """
    Utilitaires statiques pour gestion des chemins dans la structure projet.
    """

    @staticmethod
    def find_project_root(script_path: str, root_dir_name: str) -> str:
        current_dir = os.path.abspath(os.path.dirname(script_path))
        while True:
            if os.path.basename(current_dir) == root_dir_name:
                return current_dir
            parent = os.path.dirname(current_dir)
            if parent == current_dir:
                raise FileNotFoundError(
                    f"Root dir '{root_dir_name}' not found"
                )
            current_dir = parent

    @staticmethod
    def find_project_structure(project_root: str) -> str:
        candidate = os.path.join(project_root, "project_structure.yaml")
        if os.path.exists(candidate):
            return candidate
        else:
            raise FileNotFoundError("project_structure.yaml not found in root")

    @staticmethod
    def is_path_in_root(path: str, root: str) -> bool:
        abs_path = os.path.abspath(path)
        abs_root = os.path.abspath(root)
        return abs_path.startswith(abs_root)

    @staticmethod
    def get_node_path(structure: dict, *nodes: str) -> str:
        current = structure
        for node in nodes:
            if node in current:
                current = current[node]
            else:
                raise KeyError(f"Node '{node}' not found in structure")
        if isinstance(current, dict) and "path" in current:
            return current["path"]
        elif isinstance(current, str):
            return current
        else:
            raise ValueError(f"No path found for nodes {nodes}")

    @staticmethod
    def get_config_param(
        param_name: str,
        script_config: dict,
        project_structure: dict,
        *path_nodes: str,
    ) -> Any:
        if param_name in script_config:
            return script_config[param_name]
        try:
            node = PathUtils.get_node_path(project_structure, *path_nodes)
            if isinstance(node, dict) and param_name in node:
                return node[param_name]
        except Exception:
            pass
        raise KeyError(f"Parameter '{param_name}' not found.")

    @staticmethod
    def build_project_tree(
        root: str,
        structure: dict[str, Any],
    ) -> dict[str, str | dict[str, Any]]:
        """
        Construit récursivement l’arborescence complète du projet
        en ajoutant les chemins absolus basés sur la structure partielle.

        Args:
            root (str): Chemin racine courant pour concaténation.
            structure (dict[str, Any]): Dictionnaire représentant la
                structure du projet sans chemins complets.

        Returns:
            dict[str, str | dict[str, Any]]: Structure enrichie avec
            chemins absolus sous la clé 'path' à chaque niveau.

        Exemple:
            >>> struct = {
            ...    "src": {
            ...        "main.py": None,
            ...        "utils": {}
            ...    }
            ... }
            >>> PathUtils.build_project_tree('/home/user/proj', struct)
            {
                "src": {
                    "main.py": "/home/user/proj/src/main.py",
                    "utils": {
                        "path": "/home/user/proj/src/utils"
                    },
                    "path": "/home/user/proj/src"
                },
                "path": "/home/user/proj"
            }
        """
        tree: dict[str, str | dict[str, Any]] = {}

        for key, val in structure.items():
            if isinstance(val, dict):
                # Recurse into sub-dict
                subtree = PathUtils.build_project_tree(
                    os.path.join(root, key), val
                )
                tree[key] = subtree
            else:
                # val est un nom de fichier/dossier simple (ou None)
                if val is None:
                    # Si valeur None, on suppose clé seule = nom
                    # fichier/dossier
                    tree[key] = os.path.join(root, key)
                else:
                    tree[key] = (
                        os.path.join(root, val)
                        if not os.path.isabs(val)
                        else val
                    )
        tree["path"] = root
        return tree
