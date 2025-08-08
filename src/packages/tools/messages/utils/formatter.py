def format_message(template: str, **kwargs) -> str:
    """
    Formatte un message avec les arguments fournis.

    Ex : format_message("Bonjour {name}", name="Alice") => "Bonjour Alice"
    """
    return template.format(**kwargs)
