import random
import time
import urllib.robotparser
from urllib.parse import urljoin


class Crawler:
    """Web crawling utilities: delays and robots.txt handling."""

    def delay_between_requests(
        self, min_delay: float = 1, max_delay: float = 3
    ) -> None:
        """Sleep random seconds between requests to respect server load."""
        sleep_time = random.uniform(min_delay, max_delay)
        time.sleep(sleep_time)

    def get_robots_parser(
        self, base_url: str, user_agent: str = "*"
    ) -> urllib.robotparser.RobotFileParser:
        """Download and parse robots.txt."""
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urljoin(base_url, "/robots.txt"))
        rp.read()
        return rp

    def can_fetch(
        self,
        rp: urllib.robotparser.RobotFileParser,
        url: str,
        user_agent: str = "*",
    ) -> bool:
        """Check if URL can be fetched according to robots.txt."""
        return rp.can_fetch(user_agent, url)
