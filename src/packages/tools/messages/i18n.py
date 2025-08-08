import gettext
import os
from collections.abc import Callable


def setup_i18n(
    localedir: str | None = None,
    languages: list[str] | None = None,
) -> Callable[[str], str]:
    """
    Initialise gettext avec la locale désirée, fallback activé.

    Args:
        localedir: chemin vers dossier locales contenant sous-dossiers langue.
        languages: liste de codes langue ISO (ex. ["fr"], ["en"]).

    Returns:
        Fonction _() effectuant la traduction.
    """
    if localedir is None:
        localedir = os.path.join(os.path.dirname(__file__), "locales")

    translation = gettext.translation(
        domain="messages",
        localedir=localedir,
        languages=languages,
        fallback=True,
    )
    return translation.gettext


_ = setup_i18n()
