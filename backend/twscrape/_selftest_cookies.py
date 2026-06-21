#!/usr/bin/env python3
# Offline test for the cookie parser. No Tkinter/network needed.
import cookie_utils as g

# 1) Netscape cookies.txt format (tab-separated, 7 columns)
netscape = "\n".join([
    "# Netscape HTTP Cookie File",
    "\t".join([".x.com", "TRUE", "/", "TRUE", "9999999999", "auth_token", "AAAA1111"]),
    "\t".join([".x.com", "TRUE", "/", "TRUE", "9999999999", "ct0", "BBBB2222"]),
    "\t".join([".x.com", "TRUE", "/", "TRUE", "9999999999", "guest_id", "ignore"]),
])
a, c = g.extract_tokens_from_cookies_text(netscape)
assert (a, c) == ("AAAA1111", "BBBB2222"), (a, c)

# 2) JSON array export (Cookie-Editor style)
json_arr = '[{"name":"ct0","value":"CT0VAL"},{"name":"auth_token","value":"AUTHVAL"}]'
a, c = g.extract_tokens_from_cookies_text(json_arr)
assert (a, c) == ("AUTHVAL", "CT0VAL"), (a, c)

# 3) Raw cookie string
raw = "auth_token=RAWAUTH; ct0=RAWCT0; lang=en"
a, c = g.extract_tokens_from_cookies_text(raw)
assert (a, c) == ("RAWAUTH", "RAWCT0"), (a, c)

# 4) Empty / junk
assert g.extract_tokens_from_cookies_text("") == ("", "")

print("PASS: cookie parser handles Netscape, JSON, and raw-string formats.")
