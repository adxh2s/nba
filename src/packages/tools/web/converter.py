from bs4 import BeautifulSoup, NavigableString, Tag


class HtmlConverter:
    """
    Convert HTML content to plain text, preserving whitespace in given tags.
    """

    def html_to_text(
        self,
        html_content: str,
        parser: str = "lxml",
        from_encoding: str = "utf-8",
        preserve_whitespace_tags: list[str] | None = None,
    ) -> str:
        """
        Extract text from HTML, preserving whitespace inside some tags.

        Args:
            html_content: HTML content string.
            parser: BS4 parser type, e.g. 'lxml', 'html.parser'.
            from_encoding: Input encoding.
            preserve_whitespace_tags: List of tags where whitespace
            is preserved.

        Returns:
            Extracted text string.
        """
        if preserve_whitespace_tags is None:
            preserve_whitespace_tags = []

        soup = BeautifulSoup(html_content, parser, from_encoding=from_encoding)

        for tagname in preserve_whitespace_tags:
            for tag in soup.find_all(tagname):
                # Vérifie que tag est bien un Tag
                # et que string est NavigableString
                if isinstance(tag, Tag) and isinstance(
                    tag.string, NavigableString
                ):
                    tag.string.replace_with(tag.string)

        return soup.get_text(separator="\n", strip=True)
