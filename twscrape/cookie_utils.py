#!/usr/bin/env python3
"""Cookie parsing helper shared by the GUI and its tests (no Tkinter import)."""
import json
import re


def extract_tokens_from_cookies_text(text):
    """Pull (auth_token, ct0) out of any common cookie export.

    Supports: Netscape cookies.txt (tab-separated, 7 cols), JSON arrays of
    {name, value}, JSON dict {name: value}, and raw 'auth_token=..; ct0=..'.
    """
    auth, ct0 = "", ""
    text = (text or "").strip()
    if not text:
        return auth, ct0

    # 1) JSON forms
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "name" not in data:
            auth = data.get("auth_token", auth) or auth
            ct0 = data.get("ct0", ct0) or ct0
        elif isinstance(data, dict):
            data = [data]
        if isinstance(data, list):
            for c in data:
                if not isinstance(c, dict):
                    continue
                name, value = c.get("name"), c.get("value", "")
                if name == "auth_token":
                    auth = value
                elif name == "ct0":
                    ct0 = value
        if auth or ct0:
            return auth, ct0
    except (ValueError, TypeError):
        pass

    # 2) Netscape cookies.txt (domain, flag, path, secure, expiry, name, value)
    for line in text.splitlines():
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) >= 7:
            name, value = fields[5], fields[6]
            if name == "auth_token":
                auth = value
            elif name == "ct0":
                ct0 = value
    if auth or ct0:
        return auth, ct0

    # 3) Raw cookie string fallback
    m = re.search(r"auth_token=([^;\s]+)", text)
    if m:
        auth = m.group(1)
    m = re.search(r"ct0=([^;\s]+)", text)
    if m:
        ct0 = m.group(1)
    return auth, ct0
