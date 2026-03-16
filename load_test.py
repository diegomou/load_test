"""
Script to perform a load test using Locust. It simulates multiple users accessing a specified URL with randomized headers to mimic real-world traffic patterns. The test includes a custom load shape to ramp up and down the number of users over time, and it handles responses to identify successful requests and rate limiting.
"""

import os
import random
from locust import FastHttpUser, task, between, events, LoadTestShape


class WebsiteUser(FastHttpUser):
    wait_time = between(1.0, 3.0)
    host = os.getenv("SITE_URL", "https://www.your_testing_url.com")

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0",
    ]

    def _generate_fake_ip(self) -> str:
        """
        Generate a random fake IP address for the X-Forwarded-For header.

        Returns:
            str: A randomly generated IP address in the format "X.X.X.X"
        """
        return f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    def _generate_random_user_agent(self) -> str:
        """
        Select a random User-Agent string from the predefined list.

        Returns:
            str: A randomly selected User-Agent string.
        """
        return random.choice(self.user_agents)

    @task
    def load_test_endpoint(self):
        headers = {
            "User-Agent": self._generate_random_user_agent(),
            "X-Forwarded-For": self._generate_fake_ip(),
            "Accept-Language": "en-US,en;q=0.9",
        }

        # stream=True tells Locust NOT to download the page content. This saves massive amounts of bandwidth.
        with self.client.get(url="/", headers=headers, catch_response=True, timeout=30, stream=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.failure("Rate Limited (429)")
            else:
                # We use .content_iter() or just check status because we didn't download .text
                response.failure(f"Status code: {response.status_code}")


# --- Load Shape Logic (Kept as requested) ---


class StressTestShape(LoadTestShape):
    stages = [
        {"duration": 30, "users": 500, "spawn_rate": 100},
        {"duration": 60, "users": 2000, "spawn_rate": 200},
        {"duration": 90, "users": 10000, "spawn_rate": 500},
        {"duration": 120, "users": 1000, "spawn_rate": 100},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        return None


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    if environment.host:
        print(f"🚀 Optimized test starting on {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("📊 Load test complete")
