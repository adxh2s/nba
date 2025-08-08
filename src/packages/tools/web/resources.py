import os
from urllib.parse import urljoin, urlparse

from playwright.sync_api import Page  # à adapter selon l'installation réelle


class ResourceManager:
    """
    Manage extraction and downloading of static resources (CSS, JS, images)
    from a web page.
    """

    def download_resource(
        self, page: Page, resource_url: str, output_dir: str
    ) -> str | None:
        """
        Download and save a single resource.

        Args:
            page: Playwright Page object.
            resource_url: URL of the resource.
            output_dir: Local directory where to save resource.

        Returns:
            Relative path of saved resource or None if fails.
        """
        try:
            response = page.request.get(resource_url)
            if response.ok:
                parsed_url = urlparse(resource_url)
                path = parsed_url.path.lstrip("/")
                full_path = os.path.join(output_dir, path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "wb") as f:
                    f.write(response.body())
                return path
        except Exception:
            pass
        return None

    def extract_and_download_resources(
        self, page: Page, base_url: str, output_dir: str
    ) -> list[str]:
        """
        Extract resources URLs and download only those belonging
        to base domain.

        Args:
            page: Playwright Page loaded with content.
            base_url: Base URL for filtering resources.
            output_dir: Directory to save resources.

        Returns:
            List of relative paths of successfully downloaded resources.
        """
        from bs4 import BeautifulSoup, Tag

        soup = BeautifulSoup(page.content(), "html.parser")
        resource_urls = set()

        # Gather CSS, fonts
        for link in soup.find_all("link", href=True):
            if not isinstance(link, Tag):
                continue
            href = link.attrs.get("href")
            if not isinstance(href, str):
                continue
            if href.endswith((".css", ".woff2", ".woff", ".ttf")):
                resource_urls.add(urljoin(base_url, href))

        # Scripts
        for script in soup.find_all("script", src=True):
            if not isinstance(script, Tag):
                continue
            src = script.attrs.get("src")
            if not isinstance(src, str):
                continue
            resource_urls.add(urljoin(base_url, src))

        # Images
        for img in soup.find_all("img", src=True):
            if not isinstance(img, Tag):
                continue
            src = img.attrs.get("src")
            if not isinstance(src, str):
                continue
            resource_urls.add(urljoin(base_url, src))

        downloaded: list[str] = []
        base_netloc = urlparse(base_url).netloc
        for res_url in resource_urls:
            parsed_url = urlparse(res_url)
            if parsed_url.netloc == base_netloc:
                path = self.download_resource(page, res_url, output_dir)
                if path:
                    downloaded.append(path)

        return downloaded
