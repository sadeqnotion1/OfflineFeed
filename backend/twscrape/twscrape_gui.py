#!/usr/bin/env python3
"""
twscrape_gui.py  --  point-and-click control panel for the OfflineFeed Path B shim.

It lets you, with no command line:
  1. Import your X cookies (Netscape cookies.txt, JSON export, or a raw
     "auth_token=...; ct0=..." string) and register the account with twscrape.
  2. Start / stop the local RSS shim (twscrape_rss_shim.py).
  3. Test a handle (opens http://127.0.0.1:<port>/<handle>/rss in your browser).

No extra deps: Tkinter ships with standard Python. Needs `twscrape` installed
(see requirements.txt) and twscrape_rss_shim.py next to this file.
"""
import asyncio
import json
import os
import re
import subprocess
import sys
import threading
import webbrowser

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from cookie_utils import extract_tokens_from_cookies_text

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "accounts.db")
SHIM_PATH = os.path.join(HERE, "twscrape_rss_shim.py")


class App:
    def __init__(self, root):
        self.root = root
        self.proc = None
        root.title("OfflineFeed - twscrape control panel")
        root.geometry("720x600")

        pad = {"padx": 8, "pady": 4}

        # --- Section 1: account ---------------------------------------------
        acc = ttk.LabelFrame(root, text="1. Add X account by cookie")
        acc.pack(fill="x", **pad)

        ttk.Label(acc, text="Account name:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.name_var = tk.StringVar(value="my_account")
        ttk.Entry(acc, textvariable=self.name_var, width=24).grid(row=0, column=1, sticky="w")

        ttk.Label(acc, text="auth_token:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.auth_var = tk.StringVar()
        ttk.Entry(acc, textvariable=self.auth_var, width=64).grid(row=1, column=1, columnspan=2, sticky="we")

        ttk.Label(acc, text="ct0:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.ct0_var = tk.StringVar()
        ttk.Entry(acc, textvariable=self.ct0_var, width=64).grid(row=2, column=1, columnspan=2, sticky="we")

        btns = ttk.Frame(acc)
        btns.grid(row=3, column=0, columnspan=3, sticky="w", padx=6, pady=6)
        ttk.Button(btns, text="Import cookies file (Netscape / JSON)\u2026",
                   command=self.import_cookies).pack(side="left", padx=4)
        ttk.Button(btns, text="Add / update account",
                   command=self.add_account).pack(side="left", padx=4)
        ttk.Button(btns, text="Check accounts",
                   command=self.check_accounts).pack(side="left", padx=4)
        acc.columnconfigure(1, weight=1)

        # --- Section 2: server ----------------------------------------------
        srv = ttk.LabelFrame(root, text="2. Run the local RSS shim")
        srv.pack(fill="x", **pad)
        ttk.Label(srv, text="Port:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.port_var = tk.StringVar(value="8081")
        ttk.Entry(srv, textvariable=self.port_var, width=8).grid(row=0, column=1, sticky="w")
        ttk.Label(srv, text="Tweets per feed:").grid(row=0, column=2, sticky="e", padx=6)
        self.limit_var = tk.StringVar(value="40")
        ttk.Entry(srv, textvariable=self.limit_var, width=8).grid(row=0, column=3, sticky="w")
        self.start_btn = ttk.Button(srv, text="Start server", command=self.start_server)
        self.start_btn.grid(row=0, column=4, padx=6)
        self.stop_btn = ttk.Button(srv, text="Stop server", command=self.stop_server, state="disabled")
        self.stop_btn.grid(row=0, column=5, padx=6)
        self.status_var = tk.StringVar(value="Server: stopped")
        ttk.Label(srv, textvariable=self.status_var, foreground="#a00").grid(
            row=1, column=0, columnspan=6, sticky="w", padx=6)

        # --- Section 3: test ------------------------------------------------
        tst = ttk.LabelFrame(root, text="3. Test a handle")
        tst.pack(fill="x", **pad)
        ttk.Label(tst, text="@").grid(row=0, column=0, sticky="e", padx=(6, 0))
        self.handle_var = tk.StringVar(value="nasa")
        ttk.Entry(tst, textvariable=self.handle_var, width=24).grid(row=0, column=1, sticky="w")
        ttk.Button(tst, text="Open feed in browser", command=self.open_feed).grid(row=0, column=2, padx=6)

        # --- Log ------------------------------------------------------------
        logf = ttk.LabelFrame(root, text="Log")
        logf.pack(fill="both", expand=True, **pad)
        self.log = scrolledtext.ScrolledText(logf, height=14, wrap="word")
        self.log.pack(fill="both", expand=True, padx=4, pady=4)
        self._log("Ready. Tip: paste auth_token + ct0, or use 'Import cookies file'.")
        self._log("DB: " + DB_PATH)

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    # -- logging helpers (thread-safe) --------------------------------------
    def _log(self, msg):
        self.root.after(0, lambda: self._append(msg))

    def _append(self, msg):
        self.log.insert("end", str(msg) + "\n")
        self.log.see("end")

    # -- section 1 ----------------------------------------------------------
    def import_cookies(self):
        path = filedialog.askopenfilename(
            title="Select cookies file",
            filetypes=[("Cookies", "*.txt *.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError as e:
            messagebox.showerror("Import failed", str(e))
            return
        auth, ct0 = extract_tokens_from_cookies_text(text)
        if auth:
            self.auth_var.set(auth)
        if ct0:
            self.ct0_var.set(ct0)
        if auth and ct0:
            self._log("Imported auth_token and ct0 from: " + os.path.basename(path))
        else:
            missing = ", ".join([n for n, v in (("auth_token", auth), ("ct0", ct0)) if not v])
            self._log("WARNING: could not find " + missing + " in that file.")
            messagebox.showwarning(
                "Missing cookies",
                "Could not find: " + missing + "\nMake sure you exported cookies "
                "while logged into x.com.",
            )

    def add_account(self):
        name = self.name_var.get().strip() or "my_account"
        auth = self.auth_var.get().strip()
        ct0 = self.ct0_var.get().strip()
        if not auth or not ct0:
            messagebox.showwarning("Missing values", "Both auth_token and ct0 are required.")
            return
        self._log("Adding account '" + name + "' by cookie\u2026")
        threading.Thread(target=self._add_worker, args=(name, auth, ct0), daemon=True).start()

    def _add_worker(self, name, auth, ct0):
        async def go():
            from twscrape import API
            api = API(DB_PATH)
            cookies = "auth_token=" + auth + "; ct0=" + ct0
            await api.pool.add_account(
                name, "twscrape", name + "@example.com", "twscrape", cookies=cookies
            )
        try:
            asyncio.run(go())
            self._log("OK: account '" + name + "' added/updated (activated via ct0).")
            self._log("Now click 'Start server', then 'Open feed in browser' to test.")
        except Exception as e:  # noqa: BLE001 - surface any twscrape error to the user
            self._log("ERROR adding account: " + str(e))

    def check_accounts(self):
        self._log("Checking accounts\u2026")
        threading.Thread(target=self._check_worker, daemon=True).start()

    def _check_worker(self):
        try:
            out = subprocess.run(
                [sys.executable, "-m", "twscrape", "accounts"],
                cwd=HERE, capture_output=True, text=True, timeout=60,
            )
            text = (out.stdout or "") + (out.stderr or "")
            self._log(text.strip() or "(no output)")
        except Exception as e:  # noqa: BLE001
            self._log("Could not list accounts via CLI: " + str(e))

    # -- section 2 ----------------------------------------------------------
    def start_server(self):
        if self.proc and self.proc.poll() is None:
            self._log("Server already running.")
            return
        if not os.path.exists(SHIM_PATH):
            messagebox.showerror("Missing file", "twscrape_rss_shim.py not found next to this app.")
            return
        env = os.environ.copy()
        env["TWSCRAPE_SHIM_PORT"] = self.port_var.get().strip() or "8081"
        env["TWSCRAPE_SHIM_LIMIT"] = self.limit_var.get().strip() or "40"
        env["TWSCRAPE_ACCOUNTS_DB"] = DB_PATH
        try:
            self.proc = subprocess.Popen(
                [sys.executable, SHIM_PATH], cwd=HERE, env=env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Start failed", str(e))
            return
        self.status_var.set("Server: running on port " + (self.port_var.get().strip() or "8081"))
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self._pump, daemon=True).start()

    def _pump(self):
        for line in self.proc.stdout:
            self._log(line.rstrip())
        self._log("[server stopped]")
        self.root.after(0, self._reset_server_buttons)

    def _reset_server_buttons(self):
        self.status_var.set("Server: stopped")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def stop_server(self):
        if self.proc and self.proc.poll() is None:
            self._log("[stopping server\u2026]")
            self.proc.terminate()

    # -- section 3 ----------------------------------------------------------
    def open_feed(self):
        port = self.port_var.get().strip() or "8081"
        handle = self.handle_var.get().strip().lstrip("@") or "nasa"
        url = "http://127.0.0.1:" + port + "/" + handle + "/rss"
        self._log("Opening " + url)
        webbrowser.open(url)

    def on_close(self):
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
        finally:
            self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
