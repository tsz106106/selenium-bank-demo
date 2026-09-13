# Validation record

Validated on 12 September 2026 with Python 3.12.

## Passed

- Python compilation (`python -m py_compile bank_demo.py`).
- Local fixture self-test (`python bank_demo.py --self-test`).
- All three fictional portals rejected incorrect credentials.
- Unauthenticated statement requests redirected to login.
- Correct dummy credentials opened each dashboard and statement page.
- June, July and August CSV files were generated and validated for every bank (9 files total).
- Unsupported statement months returned an error.
- Selenium 4.49.0 and python-dotenv 1.2.3 were installed for compatibility checks.

## Environment limitation

The full Chrome/WebDriver run was not completed in the build environment because no Chrome or ChromeDriver binary was installed. Selenium Manager then attempted external driver discovery, and the environment blocked an unexpected third-party network request. No bypass was attempted.

The browser workflow remains runnable on a normal machine with Chrome installed. The local portal and data layer were tested without external network access. This record intentionally distinguishes those checks from an end-to-end browser result.
