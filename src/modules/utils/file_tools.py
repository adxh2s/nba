import json
import os
from datetime import datetime

import yaml


def load_from_json(filepath):
    """
    Charge un fichier JSON et retourne son contenu sous forme de dictionnaire.

    Args:
        filepath (str): Chemin vers le fichier JSON.

    Returns:
        dict: Contenu du fichier JSON.
    """
    with open(filepath, encoding="utf-8") as file:
        return json.load(file)


def load_from_yaml(filepath):
    """
    Charge un fichier YAML et retourne son contenu sous forme de dictionnaire.

    Args:
        filepath (str): Chemin vers le fichier YAML.

    Returns:
        dict: Contenu du fichier YAML.
    """
    with open(filepath, encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_from(filepath):
    """
    Charge un fichier JSON ou YAML selon son extension.

    Args:
        filepath (str): Chemin vers le fichier à charger.

    Returns:
        dict: Contenu du fichier.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
        ValueError: Si l'extension du fichier n'est pas supportée.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Fichier introuvable : {filepath}")

    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        return load_from_json(filepath)
    elif ext in (".yaml", ".yml"):
        return load_from_yaml(filepath)
    else:
        raise ValueError(f"Extension non supportée : {ext}")


def is_path_in_root(path, root=None):
    """
    Vérifie si le chemin 'path' est contenu dans le répertoire 'root'.

    Args:
        path (str): Chemin à vérifier.
        root (str, optional): Répertoire racine autorisé.
            Par défaut, racine système ("/" sous Unix, lettre du disque
            sous Windows).

    Returns:
        bool: True si 'path' est dans 'root', False sinon.
    """
    path = os.path.abspath(path)
    if root is None:
        root = os.path.splitdrive(path)[0] + "\\" if os.name == "nt" else "/"
    else:
        root = os.path.abspath(root)

    try:
        common = os.path.commonpath([path, root])
    except ValueError:
        # Peut arriver si chemins incompatibles (relatif vs absolu)
        return False
    return common == root


def find_project_root(script_path, root_dir_name=None, explicit_root=None):
    """
    Recherche la racine du projet.

    Args:
        script_path (str): Chemin du script courant.
        root_dir_name (str, optional): Nom du répertoire racine à chercher.
        explicit_root (str, optional): Chemin racine explicite passé en
        paramètre.

    Returns:
        str: Chemin absolu vers la racine du projet.

    Raises:
        RuntimeError: Si racine recherchée et non trouvée.
    """
    if explicit_root:
        return os.path.abspath(explicit_root)

    current_dir = os.path.abspath(os.path.dirname(script_path))

    if root_dir_name is None:
        # Remonter jusqu’à la racine système
        while True:
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                return current_dir
            current_dir = parent_dir
    else:
        # Remonter jusqu’au dossier nommé root_dir_name
        while True:
            if os.path.basename(current_dir) == root_dir_name:
                return current_dir
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                raise RuntimeError(
                    f"Dossier racine '{root_dir_name}' introuvable "
                    f"à partir de {script_path}"
                )
            current_dir = parent_dir


def find_project_structure(project_root, filenames=None):
    """
    Recherche le premier fichier 'project_structure.yaml' dans la racine ou
    sous dossier 'conf'.

    Args:
        project_root (str): Chemin racine du projet.
        filenames (list[str], optional): Liste des chemins relatifs à tester.
            Par défaut : ['project_structure.yaml',
            'conf/project_structure.yaml']

    Returns:
        str: Chemin complet vers le fichier trouvé.

    Raises:
        FileNotFoundError: Si aucun fichier trouvé.
    """
    if filenames is None:
        filenames = [
            "project_structure.yaml",
            os.path.join("conf", "project_structure.yaml"),
        ]

    for fname in filenames:
        path = os.path.join(project_root, fname)
        if os.path.isfile(path) and is_path_in_root(path, project_root):
            return path
    raise FileNotFoundError(
        f"project_structure.yaml introuvable dans les chemins possibles"
        f"sous {project_root}"
    )


def build_file_path(dir_path, filename, extension):
    """
    Construit un chemin complet à partir du dossier, nom fichier et extension.

    Args:
        dir_path (str): Dossier parent (peut être vide ou None).
        filename (str): Nom du fichier sans extension.
        extension (str): Extension du fichier (avec ou sans point).

    Returns:
        str: Chemin complet construit.
    """
    if extension and not extension.startswith("."):
        extension = "." + extension
    full_filename = filename + extension
    if dir_path:
        return os.path.join(dir_path, full_filename)
    else:
        return full_filename


def build_project_tree(base_path, structure):
    """
    Construit récursivement l’arborescence complète du projet à partir
    de la structure YAML.

    Args:
        base_path (str): Chemin absolu du dossier parent.
        structure (dict): Dictionnaire représentant la structure YAML
        au niveau courant.

    Returns:
        dict: Dictionnaire récursif avec clés noms d’éléments,
            valeurs dict avec 'path', 'type', 'pattern', 'description',
            'children'.
    """
    tree = {}

    for name, props in structure.items():
        node_path = os.path.join(base_path, name)
        node = {
            "path": node_path,
            "type": props.get("type", "folder"),
            "pattern": props.get("pattern"),
            "description": props.get("description"),
            "children": {},
        }

        # Récupérer les enfants sous "content" ou "children"
        content = props.get("content") or props.get("children") or {}

        if isinstance(content, dict) and content:
            # Appel récursif si dict
            node["children"] = build_project_tree(node_path, content)

        elif isinstance(content, list) and content:
            # Si liste d’éléments dict, fusionner récursivement
            children = {}
            for child in content:
                if isinstance(child, dict):
                    children.update(build_project_tree(node_path, child))
            node["children"] = children

        # Sinon children vide

        tree[name] = node

    return tree


def get_node_path(project_structure, *keys):
    """
    Recherche un chemin dans PROJECT_STRUCTURE suivant la séquence keys,
    descend dans 'children' à chaque niveau et retourne le chemin ('path').

    Args:
        project_structure (dict): Structure projet.
        *keys: séquence des clés dans la hiérarchie.

    Returns:
        str: Chemin absolu du nœud demandé.

    Raises:
        KeyError: Si clé ou 'path' absent.
    """
    node = project_structure
    for i, key in enumerate(keys):
        if key not in node:
            raise KeyError(
                f"Clé '{key}' introuvable à la profondeur {i} "
                f"dans PROJECT_STRUCTURE"
            )
        node = node[key]
        if i < len(keys) - 1:
            if "children" not in node:
                raise KeyError(
                    f"Noeud '{key}' sans clé 'children' attendue à la "
                    f"profondeur {i}"
                )
            node = node["children"]
    if "path" not in node:
        raise KeyError(f"Noeud final '{keys[-1]}' sans clé 'path'")
    return node["path"]


def get_config_param(param_name, dict_app, project_structure, *path_keys):
    """
    Recherche param_name dans dict_app, sinon dans la structure
    projet selon path_keys.

    Args:
        param_name (str): Nom paramètre à chercher.
        dict_app (dict): Configuration globale dict_app.
        project_structure (dict): Structure projet.
        *path_keys: Chemin dans la structure pour chercher le paramètre.

    Returns:
        valeur du paramètre.

    Raises:
        KeyError: Si paramètre non trouvé.
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
        f"Paramètre '{param_name}' introuvable ni dans dict_app"
        f"ni dans PROJECT_STRUCTURE"
    )


def format_report_filename(template, input_filename=None):
    """
    Génère le nom formaté d’un fichier rapport à partir d’un template.

    Args:
        template (str): Template ex: "{date:%Y%m%d%H%M}_{input}_report.html"
        input_filename (str, optional): Nom fichier d'entrée.

    Returns:
        str: Nom formaté.
    """
    now = datetime.now()
    base_input = (
        os.path.splitext(os.path.basename(input_filename))[0]
        if input_filename
        else "report"
    )
    return template.format(date=now, input=base_input)
