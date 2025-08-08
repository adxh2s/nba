import os
import random
import re
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page


class WebUtils:
    """
    Miscellaneous utility functions for web scraping tasks.
    """

    @staticmethod
    def delay_between_requests(
        min_delay: float = 1, max_delay: float = 3
    ) -> None:
        """Pause between requests, random within limits."""
        time.sleep(random.uniform(min_delay, max_delay))

    @staticmethod
    def is_cached(output_dir: str, filename: str) -> bool:
        """
        Check if a file already exists in the output directory (cache).
        """
        filepath = os.path.join(output_dir, filename)
        return os.path.exists(filepath)

    @staticmethod
    def save_content(output_dir: str, filename: str, content: str) -> None:
        """
        Save content to a file with UTF-8 encoding; create parent folders
        if needed.
        """
        os.makedirs(output_dir, exist_ok=True)
        with open(
            os.path.join(output_dir, filename), "w", encoding="utf-8"
        ) as f:
            f.write(content)

    @staticmethod
    def generate_filename_from_url(url: str) -> str:
        """
        Make a safe filename from a URL by replacing problematic chars.
        """
        return re.sub(r"[:/?#]+", "_", url)

    @staticmethod
    def fetch_page_with_playwright(page: "Page", url: str) -> str:
        """
        Use Playwright to load a URL and return the HTML content.
        """
        page.goto(url)
        return page.content()

    @staticmethod
    def html_to_text(
        html: str,
        parser: str = "lxml",
        from_encoding: str = "utf-8",
        preserve_whitespace_tags: list[str] | None = None,
    ) -> str:
        """
        Convert HTML to plain text using the HtmlConverter from this package.
        """
        from .converter import HtmlConverter

        converter = HtmlConverter()
        return converter.html_to_text(
            html, parser, from_encoding, preserve_whitespace_tags
        )
