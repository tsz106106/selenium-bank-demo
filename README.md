# Multi-Bank e-Statement Automation

![Multi-Bank e-Statement Automation Demo](assets/bank-selenium-cover.png)

A runnable **Python + Selenium** demonstration of a repetitive finance workflow:

**Open banking portal → log in → open e-Statements → select month → download → validate.**

Three fictional banks (**Harbour**, **Summit**, **Cedar**) use different element IDs, separate browser sessions, and isolated download folders — the same pattern used when automating multiple real portals with one shared engine and site-specific adapters.

> **Synthetic demo only.** These are fictional banks and dummy accounts. This project does not connect to any real bank, and includes no real credentials, customer records, or bank branding. It is a reconstructed portfolio sample that shows how the workflow is engineered — not a measured ROI study from this codebase.

## What this demonstrates

| Capability | In this demo |
| --- | --- |
| Login and navigation automation | Full happy path on each portal |
| Multi-site selectors | Per-bank `Bank` configs with different element IDs |
| Configuration outside code | Credentials and month via `.env` |
| Reliable browser waits | Explicit waits for visible / clickable elements |
| Download validation | Schema, bank, month, row count, and SHA-256 in `summary.json` |
| Failure isolation | One bank can fail while others still complete |
| Unattended runs | `--headless` |
| Walkthrough pacing | `--slow` for live or recorded demos |

Longer portfolio blurb: [`PORTFOLIO_DESCRIPTION.md`](PORTFOLIO_DESCRIPTION.md). Validation notes: [`VALIDATION.md`](VALIDATION.md).

## Quick start

**Requirements:** Python 3.10+ and Google Chrome. The first run may need network access so Selenium Manager can resolve the browser driver.

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

Chrome opens and processes each bank in sequence. Each run writes a new timestamped folder under `output/`. Default month: **August 2026** (June and July are also available).

## Useful commands

```bash
# Default: start mock portals and automate all three banks
python bank_demo.py

# Slower pace for a live or recorded walkthrough
python bank_demo.py --slow 1.5

# Different month / one bank
python bank_demo.py --month 2026-07 --bank summit

# Headless
python bank_demo.py --headless --slow 0

# Inject a failure on Summit; Harbour and Cedar should still succeed
python bank_demo.py --headless --slow 0 --fail-bank summit

# Browse the mock sites manually at http://127.0.0.1:8765
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

Copy `.env.example` → `.env`. Shell environment variables override `.env`; command-line flags override those defaults. `.env` and `output/` are gitignored.

Optional: `CHROME_BINARY` and `CHROMEDRIVER_PATH` for offline or locked-down machines. `--port` selects the mock-server port in manual mode; automation picks a free port by default.

## What to inspect

- `bank_demo.py` — bank selectors, shared `run_bank` flow, embedded mock HTTP server
- `.env.example` — configuration surface
- `requirements.txt` / `requirements-tested.txt`
- `sample-output/` and [`VALIDATION.md`](VALIDATION.md) — evidence of checks run
- Per run: `output/<run>/summary.json`, `run.log`, screenshots, and CSVs

## Engineering notes

- **Explicit waits** for UI readiness; `--slow` is presentation-only.
- **Isolated browsers and download folders** per bank; overall exit code is `0` only when all selected banks succeed.
- **Fresh output directory** every run so downloads cannot collide with older files.
- **Scope:** CSV statements, HTML forms, month dropdowns. Not MFA, CAPTCHA, real bank APIs, scheduling, email delivery, or cloud hosting.

## Suggested 60–90 second walkthrough

1. Note the synthetic-demo disclosure and `.env.example` (dummy data only).
2. Run `python bank_demo.py --slow 1.5`.
3. Open a downloaded CSV and `summary.json`.
4. Optionally run `--fail-bank summit` to show that Cedar is still processed.

## Troubleshooting

- **ModuleNotFoundError** — install requirements with the same Python executable used to run the script.
- **Driver / Session errors** — install Chrome; allow Selenium Manager, or set matching `CHROME_BINARY` / `CHROMEDRIVER_PATH`.
- **No graphical desktop** — use `--headless`.
- **Login failure** — restore dummy credentials from `.env.example`; check for shell variables overriding them.
- **Port already in use** — pick another `--port` or omit it.

## 中文使用摘要

安裝 Python 同 Chrome，跟住上方指令執行。程式會自動啟動三間虛構銀行嘅本機網頁，逐間登入、揀月份、下載 CSV 月結單。全部係 dummy 資料，無需真實銀行帳戶。`--slow 1.5` 適合現場或錄影示範；`--fail-bank` 展示一間失敗後仍處理其餘銀行。呢個係作品集用嘅合成示範，唔係真實銀行系統。

## References

- Selenium waits: https://www.selenium.dev/documentation/webdriver/waits/
- Selenium Manager: https://www.selenium.dev/documentation/selenium_manager/
