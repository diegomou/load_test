"""Script to perform a load test using Locust.

It simulates multiple users accessing a specified URL with randomized headers to mimic real-world \
traffic patterns. The test includes a custom load shape to ramp up and down the number of users \
over time, and it handles responses to identify successful requests and rate limiting.
"""

import logging
import os
import random
from typing import Any

from locust import FastHttpUser, LoadTestShape, between, events, task
from locust.env import Environment

logger = logging.getLogger(__name__)

SUCCESS_STATUS_CODE = 200
RATE_LIMIT_STATUS_CODE = 429


class WebsiteUser(FastHttpUser):
    """User class for the load test."""

    wait_time = between(1.0, 3.0)
    host = os.getenv("SITE_URL", "https://www.your_testing_url.com")

    user_agents = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # noqa: E501
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",  # noqa: E501
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0",
    )

    def _generate_fake_ip(self) -> str:
        """Generate a random fake IP address for the X-Forwarded-For header.

        Returns:
            str: A randomly generated IP address in the format "X.X.X.X"

        """
        return f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"  # noqa: S311

    def _generate_random_user_agent(self) -> str:
        """Generate a random User-Agent string from the predefined list.

        Returns:
            str: A randomly selected User-Agent string.

        """
        return random.choice(self.user_agents)  # noqa: S311

    @task
    def load_test_endpoint(self) -> None:
        """Load test the endpoint."""
        headers = {
            "User-Agent": self._generate_random_user_agent(),
            "X-Forwarded-For": self._generate_fake_ip(),
            "Accept-Language": "en-US,en;q=0.9",
        }

        # stream=True tells Locust NOT to download the page content. This saves massive amounts of bandwidth.
        with self.client.get(url="/", headers=headers, catch_response=True, timeout=30, stream=True) as response:
            if response.status_code == SUCCESS_STATUS_CODE:
                response.success()
            elif response.status_code == RATE_LIMIT_STATUS_CODE:
                response.failure(f"Rate Limited ({RATE_LIMIT_STATUS_CODE})")
            else:
                response.failure(f"Status code: {response.status_code}")


class StressTestShape(LoadTestShape):
    """Load shape for the stress test - Ramping up and down the number of users over time.

    Args:
        LoadTestShape: LoadTestShape class from Locust.

    """

    stages = (
        {"duration": 30, "users": 500, "spawn_rate": 100},
        {"duration": 60, "users": 2000, "spawn_rate": 200},
        {"duration": 90, "users": 10000, "spawn_rate": 500},
        {"duration": 120, "users": 1000, "spawn_rate": 100},
    )

    def tick(self) -> tuple[int, int] | None:
        """Tick method for the load shape.

        Returns:
            tuple: A tuple containing the number of users and the spawn rate.
            None: If the run time is greater than the duration of the last stage.

        """
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        return None


@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs: dict[str, Any]) -> None:  # noqa: ARG001
    """Event listener for the test start.

    Args:
        environment: The environment object.
        **kwargs: Additional keyword arguments.

    """
    if environment.host:
        logger.info("Optimized test starting on %s", environment.host)


@events.test_stop.add_listener
def on_test_stop(environment: Environment, **kwargs: dict[str, Any]) -> None:  # noqa: ARG001
    """Event listener for the test stop.

    Args:
        environment: The environment object.
        **kwargs: Additional keyword arguments.

    """
    logger.info("Load test complete")
