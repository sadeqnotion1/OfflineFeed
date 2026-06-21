# Path B - twscrape RSS shim for OfflineFeed

A tiny local HTTP service that fetches **real reverse-chronological** tweets with
[`twscrape`](https://github.com/vladkens/twscrape) and serves them as an RSS feed
at `http://127.0.0.1:8081/<handle>/rss`.

**Why this needs no app change:** OfflineFeed's resolver already requests
`{host}/{handle}/rss` from each host in `OFFLINEFEED_NITTER_HOSTS` and rewrites
permalinks to `https://x.com/<path>`. This shim speaks exactly that shape, so to
OfflineFeed it's just "a Nitter host" living on the default `127.0.0.1:8081`.

> Do NOT use the Path A ZIP (docker-compose / nitter.conf / sessions.jsonl) for
> this - none of it applies here. This package replaces it.

---

## Files
- `run_twscrape_gui.bat` - **double-click this (Windows)** to install twscrape and
  open the control-panel GUI. Easiest path.
- `twscrape_gui.py` - the GUI itself (Tkinter; ships with Python, no extra deps).
- `start_shim_only.bat` - runs just the RSS server (no GUI), e.g. in background.
- `twscrape_rss_shim.py` - the local RSS server.
- `cookie_utils.py` - cookie-file parser used by the GUI.
- `requirements.txt` - just `twscrape`.
- `_selftest_render.py` / `_selftest_cookies.py` - offline checks (no network).

---

## Easiest setup: the GUI (Windows)

1. Make sure **Python 3.10+** is installed (during install, tick
   "Add python.exe to PATH").
2. **Double-click `run_twscrape_gui.bat`.** It installs twscrape the first time,
   then opens the control panel.
3. In the window:
   - **Section 1 - Add account:** either paste your `auth_token` and `ct0`, or
     click **"Import cookies file (Netscape / JSON)"** and pick your exported
     cookies file - it fills both boxes for you. Then click **Add / update
     account**.
   - **Section 2 - Run server:** click **Start server** (default port 8081).
   - **Section 3 - Test:** type a handle (e.g. `nasa`) and click **Open feed in
     browser** - you should see RSS with recent tweets.
4. Leave the server running and start OfflineFeed (env var already defaults to
   `http://127.0.0.1:8081`). Refresh and check System Logs.

> Is a **Netscape `cookies.txt`** OK? **Yes.** That's the format the popular
> "Get cookies.txt LOCALLY" extension exports, and the Import button reads it
> directly. JSON exports (Cookie-Editor) and a raw `auth_token=...; ct0=...`
> string work too.

---

## Manual / command-line setup (optional)

## Requirements
- Python 3.10+
- One X/Twitter account you can log into **in a normal browser** (see note below).

---

## About the "phone number" wall

When you try to register a brand-new account, X often demands a phone number.
That requirement is on **X's signup side** - no scraper or code can bypass it.
The fix is to **not register/login programmatically at all**. Instead, log in
once in a real browser and hand twscrape the resulting **cookies**
(`auth_token` + `ct0`). This is twscrape's most stable method and avoids the
entire signup/login/phone challenge.

You do **not** need a fresh burner. Any account you can sign into in a browser
works - including:
- An X account you already have (a secondary/non-primary one is ideal).
- A new account created via **"Sign up with Google"** in the X mobile app, which
  often skips the phone step.
- A new account created in the **mobile app over normal cellular/Wi-Fi** (not a
  VPN/datacenter IP), where the phone challenge is less likely to trigger.

> Note: X frequently rejects VoIP numbers (Google Voice, TextNow, etc.). If you
> must verify, a real SIM is most reliable; you can sometimes add + verify a
> number and then remove it afterward.

---

### Setup (cookie method - recommended)

1. **Install:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get your cookies** from a browser where you're logged into X:
   - Open `x.com` while logged in.
   - Open DevTools (F12) -> **Application** (Chrome) or **Storage** (Firefox)
     -> **Cookies** -> `https://x.com`.
   - Copy the **`auth_token`** value and the **`ct0`** value.

3. **Add the account by cookie** (creates `accounts.db`):
   ```bash
   twscrape add_cookie my_account "auth_token=THE_AUTH_TOKEN; ct0=THE_CT0"
   twscrape accounts            # should show the account as active
   ```
   Cookie accounts that include `ct0` are **activated immediately** - there is
   NO `login_accounts` step, no email code, and no phone prompt.

4. **Run the shim** (from the same folder as `accounts.db`):
   ```bash
   python twscrape_rss_shim.py
   ```
   It listens on `127.0.0.1:8081` by default. Override via env vars if needed:
   `TWSCRAPE_SHIM_PORT`, `TWSCRAPE_SHIM_HOST`, `TWSCRAPE_SHIM_LIMIT`,
   `TWSCRAPE_ACCOUNTS_DB`.

5. **Verify it directly:**
   ```bash
   curl http://127.0.0.1:8081/nasa/rss
   ```
   You should get RSS with newest-first `<item>`s and real `pubDate`s.

6. **Point OfflineFeed at it** (already the default after the resolver fix):
   ```bash
   # Windows PowerShell (persistent):
   setx OFFLINEFEED_NITTER_HOSTS "http://127.0.0.1:8081"
   # mac/Linux:
   export OFFLINEFEED_NITTER_HOSTS="http://127.0.0.1:8081"
   ```
   Start the app, click **refresh**, open **System Logs**. You should see:
   ```
   [Twitter] @nasa -> http://127.0.0.1:8081: OK (N tweets)
   ```
   Syndication is never reached, so the stale/curated-feed problem is gone.

### Optional: more accounts for rotation
Add a second/third account the same way (`twscrape add_cookie acct2 "..."`).
twscrape rotates across them and backs off on rate limits, which helps when you
have many sources.

### Alternative: password login (less stable, can hit the phone wall)
```bash
twscrape add_accounts accounts.txt username:password:email:email_password
twscrape login_accounts
```
This logs in via the email verification code and is exactly the flow that can
trigger phone/identity challenges - prefer the cookie method above.

---

## Notes & tuning
- **Freshness:** twscrape returns the live `UserTweets` timeline, so feeds are
  current. The shim re-fetches on each request; OfflineFeed only calls it on
  refresh, so load is light.
- **Cookie lifetime:** `auth_token` stays valid for weeks-to-months. When it
  expires, twscrape will error - just repeat step 2-3 with a fresh cookie.
- **Per-feed size:** `TWSCRAPE_SHIM_LIMIT` (default 40).
- **Keep it local:** the shim binds to `127.0.0.1` only. Don't expose it.
- **Run as a background service** (optional): a Windows Task / NSSM service, or
  `nohup python twscrape_rss_shim.py &` on mac/Linux.

## Self-test (offline, already run for you)
```bash
python _selftest_render.py
```
Validates that the RSS output is well-formed and carries the fields the app's
parser needs (title, link, pubDate, guid). It does NOT exercise twscrape - that
step needs your cookie + network, which only you can run.
