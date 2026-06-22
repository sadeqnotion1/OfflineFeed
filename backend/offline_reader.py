"""
offline_reader.py -- OfflineFeed server-rendered "offline reader" page (drop-in).

WHY THIS EXISTS
---------------
The desktop app's "open in offline viewer" action (bridge.openInOfflineViewer)
opens the system browser at:

    http://127.0.0.1:8080/?reader=<article-url>&title=<title>

Previously gui_server.py had NO handler for that deep link, so the request fell
through to the static file server and the browser showed a raw
"Directory listing for /?reader=..." -- a broken, cropped-looking page
(exactly the bug in the screenshot).

This module renders a complete, self-contained, responsive HTML reader page from
the article blocks the backend ALREADY extracts (get_article_content_blocks),
so an opened post renders fully and uncropped -- using only real data.

DESIGN (per the project Delivery Standard, section 6 "UI/UX"):
  * Palette: OLED ink #0A0A14, violet #8B5CF6, cyan #06B6D4, green #22C55E.
  * Type:    Outfit (display) / Inter (body) / JetBrains Mono (mono), each with
             system fallbacks. NOTE: this is an OFFLINE reader, so we do NOT
             pull fonts from a CDN -- we use the families if the OS has them and
             fall back gracefully otherwise (zero new dependencies, no network).
  * Motion:  subtle fade/rise on load, gated behind prefers-reduced-motion.
  * A11y:    visible :focus-visible rings, cursor:pointer on clickables,
             >=4.5:1 contrast, responsive at 1440 / 1024 / 768 / 375.
  * Icons:   thin-line inline SVG only (no emoji as icons).

Pure standard library. Never raises: callers always get a valid HTML string.
"""

import html as _html

# Thin-line (1.6px) external-link icon -- SVG, not an emoji/glyph.
_EXTERNAL_SVG = (
    '<svg class="ico" viewBox="0 0 24 24" width="16" height="16" fill="none" '
    'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<path d="M14 5h5v5"></path><path d="M19 5l-8 8"></path>'
    '<path d="M18 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4"></path>'
    "</svg>"
)


def _esc(s):
    try:
        return _html.escape(str(s or ""), quote=True)
    except Exception:
        return ""


def _blocks_to_html(blocks):
    parts = []
    for b in (blocks or []):
        if not isinstance(b, dict):
            continue
        btype = b.get("type")
        content = (b.get("content") or "").strip()
        if not content:
            continue
        if btype == "p":
            parts.append("<p>" + _esc(content) + "</p>")
        elif btype == "h":
            level = b.get("level", 2)
            try:
                level = int(level)
            except Exception:
                level = 2
            level = min(max(level, 2), 4)
            parts.append("<h%d>%s</h%d>" % (level, _esc(content), level))
        elif btype == "quote":
            parts.append("<blockquote>" + _esc(content) + "</blockquote>")
        elif btype == "img":
            # content may be a local cached path (assets/...) or a remote URL.
            parts.append(
                '<figure><img loading="lazy" src="%s" alt=""></figure>'
                % _esc(content)
            )
    return "\n".join(parts)


_CSS = """
  :root {
    color-scheme: dark;
    --ink: #0A0A14;
    --ink-2: #12121F;
    --text: #ECECF2;
    --muted: #A6A6B6;          /* >=4.5:1 on --ink */
    --violet: #8B5CF6;
    --cyan: #06B6D4;
    --green: #22C55E;
    --hairline: rgba(255,255,255,0.08);
    --display: "Outfit", "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
    --body: "Inter", "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
    --mono: "JetBrains Mono", "Fira Code", "Cascadia Mono", Consolas, monospace;
  }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; }
  body {
    margin: 0;
    background: var(--ink);
    color: var(--text);
    font-family: var(--body);
    line-height: 1.65;
    -webkit-font-smoothing: antialiased;
  }
  .wrap { max-width: 720px; margin: 0 auto; padding: 48px 24px 96px; }
  header.head {
    margin: 0 0 28px; padding: 0 0 20px;
    border-bottom: 1px solid var(--hairline);
  }
  h1.title {
    font-family: var(--display);
    font-size: 30px; line-height: 1.22; font-weight: 700;
    letter-spacing: -0.01em; margin: 0 0 10px;
  }
  .src { font-size: 13px; color: var(--muted); margin: 0; word-break: break-word; }
  .src a { color: var(--cyan); text-decoration: none; }
  .src a:hover { text-decoration: underline; }
  article p { font-size: 17px; margin: 0 0 18px; }
  article h2, article h3, article h4 {
    font-family: var(--display); font-weight: 600; line-height: 1.3; margin: 30px 0 10px;
  }
  article h2 { font-size: 22px; }
  article h3 { font-size: 19px; }
  blockquote {
    margin: 20px 0; padding: 10px 18px;
    border-left: 3px solid var(--violet); color: #D2D2DC;
    background: rgba(139,92,246,0.10); border-radius: 8px;
  }
  figure { margin: 22px 0; }
  img { max-width: 100%; height: auto; display: block; border-radius: 14px; }
  .empty {
    color: var(--muted); font-size: 16px; padding: 18px 20px;
    background: var(--ink-2); border: 1px solid var(--hairline); border-radius: 12px;
  }
  .actions { margin-top: 28px; }
  .open {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 12px 18px; cursor: pointer;
    background: linear-gradient(135deg, var(--violet), var(--cyan));
    color: #fff; border-radius: 12px; text-decoration: none;
    font-weight: 600; font-size: 15px;
    transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease;
  }
  .open:hover { transform: translateY(-1px); filter: brightness(1.05);
    box-shadow: 0 8px 24px rgba(139,92,246,0.30); }
  .open .ico { display: block; }
  a:focus-visible, .open:focus-visible {
    outline: 2px solid var(--cyan); outline-offset: 3px; border-radius: 6px;
  }
  /* Tasteful entrance, disabled when the user prefers reduced motion. */
  @media (prefers-reduced-motion: no-preference) {
    .wrap { animation: rise 420ms cubic-bezier(0.22, 1, 0.36, 1) both; }
    @keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
  }
  /* Responsive: 1440 / 1024 / 768 / 375. */
  @media (max-width: 1024px) { .wrap { max-width: 680px; } }
  @media (max-width: 768px)  { .wrap { padding: 36px 20px 80px; } h1.title { font-size: 26px; } article p { font-size: 16px; } }
  @media (max-width: 375px)  { .wrap { padding: 28px 16px 64px; } h1.title { font-size: 23px; } }
"""


def render_reader_html(url, title="", blocks=None):
    """Return a full HTML document string for the offline reader page."""
    title = title or "Offline Reader"
    body_html = _blocks_to_html(blocks)
    if not body_html:
        # Defensive empty state -- never show a blank/broken page.
        body_html = (
            '<p class="empty">This post could not be extracted for offline '
            'reading (some sources, like X/Twitter, block server-side '
            'extraction). You can still open the original below.</p>'
        )
    safe_url = _esc(url)
    safe_title = _esc(title)
    return (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>' + safe_title + '</title>\n'
        '<style>' + _CSS + '</style>\n'
        '</head>\n'
        '<body>\n'
        '  <main class="wrap">\n'
        '    <header class="head">\n'
        '      <h1 class="title">' + safe_title + '</h1>\n'
        '      <p class="src"><a href="' + safe_url + '" target="_blank" rel="noopener">' + safe_url + '</a></p>\n'
        '    </header>\n'
        '    <article>\n' + body_html + '\n    </article>\n'
        '    <p class="actions"><a class="open" href="' + safe_url + '" target="_blank" rel="noopener">'
        + _EXTERNAL_SVG + '<span>Open original</span></a></p>\n'
        '  </main>\n'
        '</body>\n'
        '</html>'
    )
