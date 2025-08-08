from .i18n import _


class MessageService:
    """
    Service simple pour récupérer les messages traduits par code.
    """

    def get_message(self, code: str) -> str:
        """
        Retourne le message traduit correspondant au code.

        Args:
            code: Identifiant du message (chaîne source dans les fichiers .po)

        Returns:
            Message traduit selon la locale configurée.
        """
        return _(code)
