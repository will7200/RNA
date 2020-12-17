# RNA (Remote Network Automation)

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

1. mypy with sqlalchemy-stubs to check database creation
