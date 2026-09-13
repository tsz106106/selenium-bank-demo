#!/usr/bin/env python3
"""Reconstructed portfolio demo. Fictional banks, local pages, synthetic CSVs only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import logging
import os
import secrets
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
LOG = logging.getLogger("bank_demo")


@dataclass(frozen=True)
class Bank:
    slug: str
    name: str
    color: str
    user_id: str
    password_id: str
    login_id: str
    statements_id: str
    period_id: str
    download_id: str
    username: str
    password: str


# Independent selectors illustrate how adapters accommodate different bank portals.
BANKS = (
    Bank("harbour", "Harbour Demo Bank", "#126b68", "customer-id", "access-code",
         "sign-in", "documents", "statement-month", "download-csv", "harbour_demo", "HarbourDemo123!"),
    Bank("summit", "Summit Demo Bank", "#3b51aa", "member-number", "member-password",
         "enter-banking", "e-statements", "period-select", "export-statement", "summit_demo", "SummitDemo123!"),
    Bank("cedar", "Cedar Demo Bank", "#8b5739", "online-user", "online-secret",
         "login-button", "statement-centre", "month-picker", "get-document", "cedar_demo", "CedarDemo123!"),
)
BY_SLUG = {b.slug: b for b in BANKS}
PERIODS = ("2026-06", "2026-07", "2026-08")
FIELDS = ["bank", "account", "date", "description", "currency", "debit", "credit", "balance"]


def statement_csv(bank: Bank, period: str) -> bytes:
    """All amounts and account identifiers are invented and deterministic."""
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(FIELDS)
    prefix = [bank.name, "DEMO-0001"]
    for day, description, debit, credit, balance in (
        ("01", "DUMMY opening balance", "0.00", "0.00", "10000.00"),
        ("05", "DUMMY customer receipt", "0.00", "2500.00", "12500.00"),
        ("12", "DUMMY supplier payment", "800.00", "0.00", "11700.00"),
        ("20", "DUMMY service fee", "25.00", "0.00", "11675.00"),
    ):
        writer.writerow(prefix + [f"{period}-{day}", description, "HKD", debit, credit, balance])
    return stream.getvalue().encode("utf-8")


def page(bank: Bank, title: str, body: str) -> bytes:
    return f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} | {bank.name}</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f2f5f7;color:#192936;font:16px/1.6 system-ui,sans-serif}}
header{{background:{bank.color};color:white;padding:27px 8%;font-weight:700;font-size:24px}}
header small{{float:right;font-size:12px;border:1px solid #ffffff88;padding:5px 12px;border-radius:20px}}
main{{max-width:940px;margin:45px auto;padding:0 24px}}.eyebrow{{font-size:12px;letter-spacing:2px;color:{bank.color};font-weight:700}}
h1{{font-size:34px;margin:8px 0}}.muted{{color:#62717c}}.card{{background:white;padding:32px;border:1px solid #dbe3e7;border-radius:14px;margin-top:24px}}
label{{display:block;font-size:14px;margin:16px 0 5px;font-weight:600}}input,select{{width:100%;padding:12px;border:1px solid #bccad2;border-radius:7px;font:inherit}}
button,.button{{display:inline-block;background:{bank.color};color:white;padding:12px 22px;border:0;border-radius:7px;font:inherit;text-decoration:none;cursor:pointer;margin-top:20px}}
form{{max-width:450px}}.amount{{font-size:38px;font-weight:700}}.badge{{background:#e8f3ee;color:#216646;padding:4px 10px;border-radius:5px;font-size:12px}}
footer{{margin-top:28px;font-size:12px;color:#62717c}}a{{color:{bank.color}}}table{{width:100%;border-collapse:collapse}}td,th{{padding:12px;text-align:left;border-bottom:1px solid #e4e9ed}}
</style><header>{bank.name}<small>FICTIONAL BANK · LOCAL DEMO</small></header>
<main><div class="eyebrow">AUTOMATED STATEMENT COLLECTION</div><h1>{title}</h1>{body}
<footer>Reconstructed portfolio demonstration. Synthetic data only. No connection to a real bank.</footer></main></html>'''.encode()


class DemoServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address):
        super().__init__(address, Portal)
        self.sessions: dict[str, str] = {}


class Portal(BaseHTTPRequestHandler):
    """Small, loopback-only mock portal. Not a production banking application."""
    def log_message(self, *_):
        pass  # Avoid logging form fields, cookies or credentials.

    def reply(self, data=b"", status=200, headers=None):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def route(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        return BY_SLUG.get(parts[0]), parts[1] if len(parts) == 2 else "login"

    def authorized(self, bank):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie", ""))
            token = cookie["demo_session"].value if "demo_session" in cookie else ""
        except Exception:
            return False
        return self.server.sessions.get(token) == bank.slug

    def do_GET(self):
        if self.path == "/":
            body = '<p class="muted">Choose a fictional portal to explore manually.</p><div class="card">'
            body += "<br>".join(f'<a href="/{b.slug}/login">{b.name}</a>' for b in BANKS) + '</div>'
            return self.reply(page(BANKS[0], "Three banks. One workflow.", body))
        bank, route = self.route()
        if not bank:
            return self.reply(b"Not found", 404)
        if route == "login":
            body = f'''<p class="muted">Sign in to your demonstration account.</p><div class="card">
<form method="post" action="/{bank.slug}/login">
<label for="{bank.user_id}">Customer ID</label><input id="{bank.user_id}" name="username" required autocomplete="off">
<label for="{bank.password_id}">Password</label><input type="password" id="{bank.password_id}" name="password" required>
<button id="{bank.login_id}">Sign in</button></form></div>'''
            return self.reply(page(bank, "Online banking", body))
        if not self.authorized(bank):
            return self.reply(status=303, headers={"Location": f"/{bank.slug}/login"})
        if route == "dashboard":
            body = f'''<p class="muted">Welcome, Demo Finance Team.</p><div class="card"><span class="badge">DEMO ACCOUNT</span>
<p>Business current account · DEMO-0001</p><div class="amount">HKD 11,675.00</div>
<a class="button" id="{bank.statements_id}" href="/{bank.slug}/statements">View e-Statements</a></div>'''
            return self.reply(page(bank, "Account overview", body))
        if route == "statements":
            options = "".join(f'<option value="{p}">{p}</option>' for p in PERIODS)
            body = f'''<p class="muted">Download a monthly statement for your records.</p><div class="card">
<form method="get" action="/{bank.slug}/download"><label for="{bank.period_id}">Statement month</label>
<select id="{bank.period_id}" name="period">{options}</select>
<p class="muted">CSV · HKD · synthetic transactions</p><button id="{bank.download_id}">Download statement</button></form></div>'''
            return self.reply(page(bank, "e-Statements", body))
        if route == "download":
            period = parse_qs(urlparse(self.path).query).get("period", [""])[0]
            if period not in PERIODS:
                return self.reply(b"Unsupported statement month", 400)
            data = statement_csv(bank, period)
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="{bank.slug}_{period}.csv"')
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        self.reply(b"Not found", 404)

    def do_POST(self):
        bank, route = self.route()
        if not bank or route != "login":
            return self.reply(b"Not found", 404)
        length = int(self.headers.get("Content-Length", "0"))
        if length > 4096:
            return self.reply(b"Too large", 413)
        data = parse_qs(self.rfile.read(length).decode())
        if (data.get("username", [""])[0], data.get("password", [""])[0]) != (bank.username, bank.password):
            return self.reply(page(bank, "Sign-in unsuccessful", '<p id="login-error">Incorrect demo credentials.</p>'), 401)
        token = secrets.token_urlsafe(24)
        self.server.sessions[token] = bank.slug
        self.reply(status=303, headers={"Location": f"/{bank.slug}/dashboard",
            "Set-Cookie": f"demo_session={token}; HttpOnly; SameSite=Strict; Path=/"})


def validate_csv(path: Path, bank: Bank, period: str):
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != FIELDS:
            raise ValueError("Downloaded file has an unexpected CSV schema")
        rows = list(reader)
    if len(rows) != 4 or any(r["bank"] != bank.name or not r["date"].startswith(period + "-") for r in rows):
        raise ValueError("Downloaded statement has the wrong bank, month or row count")
    if path.read_bytes() != statement_csv(bank, period):
        raise ValueError("Downloaded statement differs from the expected dummy data")
    return {"rows": len(rows), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run_bank(bank, base_url, period, run_dir, args):
    # Selenium is imported here so --serve and --self-test use only the standard library.
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import Select, WebDriverWait

    directory = run_dir / bank.slug
    directory.mkdir()
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1280,900")
    if args.headless:
        options.add_argument("--headless=new")
    if os.getenv("CHROME_BINARY"):
        options.binary_location = os.environ["CHROME_BINARY"]
    # Only for isolated containers running as root; not enabled on normal desktops.
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        options.add_argument("--no-sandbox")
    options.add_experimental_option("prefs", {"download.default_directory": str(directory),
        "download.prompt_for_download": False, "download.directory_upgrade": True})
    service = Service(executable_path=os.environ["CHROMEDRIVER_PATH"]) if os.getenv("CHROMEDRIVER_PATH") else Service()
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(args.timeout)
        wait = WebDriverWait(driver, args.timeout)

        def click(element_id, label):
            LOG.info("[%s] %s", bank.slug, label)
            wait.until(EC.element_to_be_clickable((By.ID, element_id))).click()
            if args.slow:  # Presentation pacing only; correctness uses explicit waits.
                time.sleep(args.slow)

        driver.get(f"{base_url}/{bank.slug}/login")
        LOG.info("[%s] Open login page", bank.slug)
        prefix = bank.slug.upper()
        username = os.getenv(f"{prefix}_USERNAME", bank.username)
        password = os.getenv(f"{prefix}_PASSWORD", bank.password)
        if args.fail_bank == bank.slug:
            password = "deliberately-wrong-demo-password"
        wait.until(EC.visibility_of_element_located((By.ID, bank.user_id))).send_keys(username)
        driver.find_element(By.ID, bank.password_id).send_keys(password)
        click(bank.login_id, "Sign in")
        wait.until(lambda d: "/dashboard" in d.current_url or d.find_elements(By.ID, "login-error"))
        if driver.find_elements(By.ID, "login-error"):
            raise ValueError("Demo login rejected")
        driver.save_screenshot(str(directory / "01-dashboard.png"))
        click(bank.statements_id, "Open e-Statements")
        Select(wait.until(EC.visibility_of_element_located((By.ID, bank.period_id)))).select_by_value(period)
        LOG.info("[%s] Select month %s", bank.slug, period)
        driver.save_screenshot(str(directory / "02-statement-selection.png"))
        expected = directory / f"{bank.slug}_{period}.csv"
        click(bank.download_id, "Download statement")
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            if expected.is_file() and expected.stat().st_size > 0 and not list(directory.glob("*.crdownload")):
                details = validate_csv(expected, bank, period)
                LOG.info("[%s] Verified %s (%d rows)", bank.slug, expected.name, details["rows"])
                return {"bank": bank.slug, "status": "success", "file": str(expected.relative_to(run_dir)), **details}
            time.sleep(0.2)
        raise TimeoutError("Statement download did not complete")
    except Exception as exc:
        # Short status avoids dumping Selenium traces, environment variables or credentials.
        LOG.error("[%s] Failed: %s; continuing with other banks", bank.slug, type(exc).__name__)
        return {"bank": bank.slug, "status": "failed", "error_type": type(exc).__name__}
    finally:
        if driver:
            driver.quit()


def self_test():
    """HTTP fixture checks, separate from the actual Selenium browser demonstration."""
    import tempfile
    import urllib.request
    import urllib.error
    from http.cookiejar import CookieJar
    from urllib.parse import urlencode
    server = DemoServer(("127.0.0.1", 0))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with tempfile.TemporaryDirectory() as folder:
            for bank in BANKS:
                opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
                assert opener.open(f"{base}/{bank.slug}/download?period=2026-08").url.endswith("/login")
                wrong = urlencode({"username": bank.username, "password": "wrong"}).encode()
                try:
                    opener.open(f"{base}/{bank.slug}/login", wrong)
                    raise AssertionError("Wrong credentials accepted")
                except urllib.error.HTTPError as error:
                    assert error.code == 401
                credentials = urlencode({"username": bank.username, "password": bank.password}).encode()
                assert opener.open(f"{base}/{bank.slug}/login", credentials).url.endswith("/dashboard")
                assert bank.period_id in opener.open(f"{base}/{bank.slug}/statements").read().decode()
                for period in PERIODS:
                    path = Path(folder) / f"{bank.slug}_{period}.csv"
                    path.write_bytes(opener.open(f"{base}/{bank.slug}/download?period={period}").read())
                    validate_csv(path, bank, period)
                try:
                    opener.open(f"{base}/{bank.slug}/download?period=1999-01")
                    raise AssertionError("Unsupported month accepted")
                except urllib.error.HTTPError as error:
                    assert error.code == 400
                print(f"PASS {bank.slug}: login, authentication gate, selectors, 3 statements, invalid month")
    finally:
        server.shutdown()
        server.server_close()


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env", override=False)
    except ImportError:
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="Explore dummy portals manually; no Selenium required")
    parser.add_argument("--self-test", action="store_true", help="Test mock HTTP flow; not a browser test")
    parser.add_argument("--month", default=os.getenv("STATEMENT_MONTH", "2026-08"), choices=PERIODS)
    parser.add_argument("--bank", default="all", choices=["all", *BY_SLUG])
    parser.add_argument("--headless", action="store_true", default=os.getenv("HEADLESS", "false").lower() == "true")
    parser.add_argument("--slow", type=float, default=float(os.getenv("DEMO_SLOW_SECONDS", "0.6")))
    parser.add_argument("--timeout", type=float, default=float(os.getenv("TIMEOUT_SECONDS", "20")))
    parser.add_argument("--port", type=int, default=0, help="0 selects a free local port; use 8765 for manual mode")
    parser.add_argument("--fail-bank", choices=list(BY_SLUG), help="Inject a dummy login failure to show isolation")
    args = parser.parse_args()
    if args.timeout <= 0 or args.slow < 0:
        parser.error("timeout must be positive; slow must be nonnegative")
    if args.self_test:
        self_test()
        return 0
    server = DemoServer(("127.0.0.1", args.port))
    base = f"http://127.0.0.1:{server.server_port}"
    if args.serve:
        print(f"Demo portals: {base} (Ctrl+C to stop)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0
    threading.Thread(target=server.serve_forever, daemon=True).start()
    out = Path(os.getenv("OUTPUT_DIR", "output"))
    if not out.is_absolute():
        out = ROOT / out
    run_dir = out.resolve() / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    run_dir.mkdir(parents=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(run_dir / "run.log", encoding="utf-8")])
    try:
        LOG.info("Starting fictional-bank demonstration for %s", args.month)
        results = [run_bank(b, base, args.month, run_dir, args) for b in BANKS if args.bank in ("all", b.slug)]
        report = {"demo": True, "period": args.month, "results": results}
        (run_dir / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        LOG.info("Complete: %d/%d successful. Output: %s", sum(r["status"] == "success" for r in results), len(results), run_dir)
        return 0 if all(r["status"] == "success" for r in results) else 1
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
