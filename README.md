# Multi-Bank e-Statement Automation (Upwork Portfolio Demo)

![Multi-Bank e-Statement Automation Demo](assets/bank-selenium-cover.png)

**Python + Selenium** demo you can run locally and link in Upwork proposals for browser automation, web scraping, and finance-ops scripting.

**Workflow:** open portal → log in → e-Statements → pick month → download CSV → validate.

Three fictional banks (**Harbour**, **Summit**, **Cedar**) use different element IDs, separate browser sessions, and isolated download folders — same pattern as multi-site production automation.

> **Synthetic mock only.** Not a real bank integration. No real credentials, customer data, or bank branding. Reconstructed portfolio sample that shows how I engineer this class of workflow. For measured business impact from past client work, see proposal text / CV (e.g. prior Finance automation reducing manual effort by ~95%) — that claim is not measured from *this* demo.

## Why this is useful on Upwork

Use this repo when a job asks for Selenium, multi-site login flows, statement/file download automation, or “prove you can automate a browser workflow.”

**What a client can verify in minutes:**

| Capability | How this demo shows it |
| --- | --- |
| Login + navigation automation | Full happy path per bank |
| Site-specific selectors | `Bank` configs with different IDs per portal |
| Config outside code | Dummy credentials & month via `.env` |
| Reliable waits | Explicit waits (not fixed sleeps for correctness) |
| Download + validation | Schema, bank, month, rows, SHA-256 in `summary.json` |
| Failure isolation | One bank can fail; others still complete (`--fail-bank`) |
| Unattended / CI-style | `--headless` |
| Screen-ready walkthrough | `--slow 1.5` for recordings |

**Suggested one-liner for proposals:**  
*“Runnable Selenium sample: three fictional bank portals, login → monthly e-statement CSV download → validation, with per-site selectors and failure isolation — https://github.com/tsz106106/selenium-bank-demo”*

Longer portfolio blurb: see [`PORTFOLIO_DESCRIPTION.md`](PORTFOLIO_DESCRIPTION.md).

## Quick start

**Requirements:** Python 3.10+, Google Chrome. First run may need network so Selenium Manager can fetch the driver.

### Windows PowerShell

```powershell
cd selenium-bank-demo
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe bank_demo.py
```

### macOS / Linux

```bash
cd selenium-bank-demo
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python bank_demo.py
```

Chrome opens and processes each bank in sequence. Each run creates a new timestamped folder under `output/`. Default month: **August 2026** (June / July also available).

## Useful commands

```bash
# Default: mock portals + all three banks
python bank_demo.py

# Presentation / screen-recording pace
python bank_demo.py --slow 1.5

# One bank / other month
python bank_demo.py --month 2026-07 --bank summit

# Headless
python bank_demo.py --headless --slow 0

# Inject failure on Summit; Harbour + Cedar should still succeed
python bank_demo.py --headless --slow 0 --fail-bank summit

# Browse mocks manually: http://127.0.0.1:8765
python bank_demo.py --serve --port 8765

# HTTP fixture checks (not a Selenium browser test)
python bank_demo.py --self-test
```

Automation starts its own server on a free local port (`127.0.0.1` only). You do **not** need `--serve` first.

## Dummy login details

| Bank | Username | Password |
| --- | --- | --- |
| Harbour Demo Bank | `harbour_demo` | `HarbourDemo123!` |
| Summit Demo Bank | `summit_demo` | `SummitDemo123!` |
| Cedar Demo Bank | `cedar_demo` | `CedarDemo123!` |

The mock **server** accepts these fixed accounts. `.env` configures the **client**. Changing a client password causes login failure; it does not change the server.

## Configuration

Copy `.env.example` → `.env`. Shell env vars override `.env`; CLI flags override env defaults. `.env` and `output/` are gitignored.

Optional: `CHROME_BINARY`, `CHROMEDRIVER_PATH` for offline / locked-down machines. `--port` for manual serve mode (default automation picks a free port).

## What to inspect in a review

- `bank_demo.py` — bank selectors, `run_bank` flow, embedded mock HTTP server
- `.env.example` — config surface
- `requirements.txt` / `requirements-tested.txt`
- `sample-output/` + [`VALIDATION.md`](VALIDATION.md) — evidence of checks run
- Per run: `output/<run>/summary.json`, `run.log`, screenshots, CSVs

## Engineering notes (short)

- **Explicit waits** for UI readiness; `--slow` is presentation-only.
- **Isolated browsers/downloads** per bank; overall exit `0` only if all selected banks succeed.
- **Fresh output dir** every run so downloads cannot collide with older files.
- **Scope:** CSV statements, HTML forms, month dropdowns. Not MFA, CAPTCHA, real bank APIs, scheduling, email, or cloud hosting.

## 60–90s client walkthrough

1. Point at the disclosure above + `.env.example`.
2. Run `python bank_demo.py --slow 1.5`.
3. Open a CSV + `summary.json`.
4. Optional: `--fail-bank summit` to show isolation.

## Troubleshooting

- **ModuleNotFoundError** — install with the same Python you run.
- **Driver / Session errors** — install Chrome; allow Selenium Manager, or set `CHROME_BINARY` / `CHROMEDRIVER_PATH`.
- **No GUI** — use `--headless`.
- **Login fails** — restore `.env.example` credentials; check shell overrides.
- **Port in use** — change `--port` or omit it.

## 中文使用摘要

安裝 Python 同 Chrome，跟住上方指令跑。程式會自動開三間虛構銀行本機頁，逐間登入、揀月份、下載 CSV。全部係 dummy 資料。`--slow 1.5` 適合錄示範；`--fail-bank` 展示一間失敗都繼續做其餘。呢個係作品集 mock demo，唔係真實銀行系統。Upwork 提案可直接連呢個 GitHub repo。

## References

- Selenium waits: https://www.selenium.dev/documentation/webdriver/waits/
- Selenium Manager: https://www.selenium.dev/documentation/selenium_manager/
