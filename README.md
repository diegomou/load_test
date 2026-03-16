# Load Testing Project

## Overview

This is a load testing project designed to stress test and analyze the performance of websites under heavy concurrent load. In this case, the target website is **rendimientos.co**.

The project uses **Locust**, a modern, open-source load testing framework written in Python, to simulate multiple concurrent users and measure response times, throughput, and failure rates.

## Purpose

This tool is used to:
- Simulate concurrent user traffic
- Identify performance bottlenecks
- Test server capacity and limits
- Monitor response times under load
- Generate performance reports

## Author

**Diego Agustín Mouriño**
- Email: diegomou92@gmail.com
- LinkedIn: https://www.linkedin.com/in/diego-mourino/?locale=en_US
- GitHub: https://github.com/diegomou

## Disclaimer

⚠️ **Educational Purposes Only**

This project is intended **exclusively for educational and authorized testing purposes**. No harmful or unauthorized use is promoted. 

Ensure you have explicit written permission from the website owner before conducting any load tests. Unauthorized load testing may violate laws and regulations including the Computer Fraud and Abuse Act (CFAA) and similar legislation in other countries.

## Requirements

- Python 3.7+
- uv
- pre-commit

## Setting up.

1. Install uv ``(brew install uv)``
2. Instal pre-commit ``(brew install pre-commit)``
3. To create the venv, please run ``uv sync``.
4. To source the venv, please run ``source .venv/bin/activate``

## Usage

Run the load test:

```bash
make run_load_test
```

Then access the Locust web UI (default): `http://localhost:8089`

## Configuration

* Edit `.env`to edit the host URL (SITE_URL environment variable)
* Edit `load_test.py` to adjust:
- Number of concurrent users
- Task definitions and behavior
- Wait times between requests
