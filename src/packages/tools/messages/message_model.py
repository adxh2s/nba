from dataclasses import dataclass


@dataclass
class MessageModel:
    """
    Modèle de données représentant un message.
    """

    code: str
    text: str
    locale: str = "en"
