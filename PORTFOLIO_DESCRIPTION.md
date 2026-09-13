# Multi-Bank e-Statement Automation Demo

## Short description

Reconstructed Python/Selenium work sample demonstrating a multi-site finance workflow: log in to three fictional banking portals, open e-Statements, select a reporting month, download CSV statements, and validate every result.

## Full description

This runnable demo shows how I structure browser automation for repetitive finance operations while keeping site-specific behaviour isolated.

The automation:

- Processes three fictional bank portals with different selectors.
- Loads dummy credentials and runtime settings from environment configuration.
- Uses explicit waits for reliable browser interaction.
- Selects a statement month and downloads each CSV into a separate run folder.
- Validates the downloaded schema, bank, month, row count, and file contents.
- Records a per-bank result and continues when one bank fails.
- Produces screenshots, a run log, and a JSON summary for auditability.

All websites, accounts, transactions, and credentials are synthetic. This is a newly reconstructed portfolio demonstration based on the type of workflow I have automated professionally; it does not contain employer-owned source code or confidential financial data.

**Technology:** Python, Selenium WebDriver, HTML, CSV, environment-based configuration.

**Relevant professional result:** I previously built a Python/Selenium solution that reduced a Finance team's daily manual workflow time by 95%.
