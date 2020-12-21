# RNA (Remote Network Automation)

![Test](https://github.com/will7200/RNA/workflows/Test/badge.svg)
[![codecov](https://codecov.io/gh/will7200/RNA/branch/main/graph/badge.svg?token=NE0A9AXBRS)](https://codecov.io/gh/will7200/RNA)

## Goal

Test application – Simple 3 Tier, Network Automation.

+ Webapp that grabs routes from other Linux machines (ssh host “ip route”) and stores into a database for later viewing.
    + User authentication
    + CRUD (Each user has their own set of machines)
        + Add Machine
        + Show results
    + UI
        + Login page
        + Hosts list
        + Route detail page
    + Deployment for CI/CD (Github, Jenkins, ECS)

## CI Tools

1. Lint with flake8
2. Static Analysis with mypy
   sqlalchemy-stubs to check database creation
3. Testing with pytest
4. Coverage with Codecov generated from pytest-cov
