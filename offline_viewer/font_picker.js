/* ==========================================================================
   OfflineFeed — Offline Viewer Font Picker   (NEW FILE)
   --------------------------------------------------------------------------
   Independent web-UI font system. It is COMPLETELY separate from the PySide6
   desktop app's Font Family picker:
     * fetches the installed system fonts from  GET /api/system/fonts
     * lets the user pick a UI/reader font from a searchable list
     * applies it by overriding the CSS custom properties the viewer already
       uses (--font-stack-graphik) plus a new --reader-font-family
     * persists the choice in localStorage and restores it on load

   Drop-in: it self-injects its own button + panel with all styles inlined, so
   it does NOT depend on the existing markup or stylesheet. Changing the font
   here never touches the desktop app, and vice-versa.
   ========================================================================== */
(function () {
  "use strict";

  var STORAGE_KEY = "offlinefeed-viewer-font";
  // Sane web-safe fallbacks appended after the chosen family so text never
  // disappears if a family is missing.
  var WEB_SAFE_FALLBACKS = "system-ui, 'Segoe UI', Roboto, Arial, sans-serif";
  var FALLBACK_FONTS = [
    "Arial", "Calibri", "Consolas", "Courier New", "Georgia",
    "Roboto", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"
  ];

  // Build a CSS font-family value. The chosen family is named first (the
  // browser resolves it from the locally installed system fonts — i.e.
  // local("Family")) and we always append web-safe fallbacks.
  function buildStack(family) {
    if (!family) return WEB_SAFE_FALLBACKS;
    return "'" + String(family).replace(/'/g, "") + "', " + WEB_SAFE_FALLBACKS;
  }

  function applyFont(family) {
    var stack = buildStack(family);
    var root = document.documentElement;
    // Item 1: the offline reader font is INDEPENDENT from the chat/UI font, so
    // only override the dedicated reader variable here. We deliberately do NOT
    // touch --font-stack-graphik (the chat/UI font), so changing the reader
    // font never alters the chat font and vice-versa.
    root.style.setProperty("--reader-font-family", stack);
  }

  function savedFont() {
    try { return localStorage.getItem(STORAGE_KEY) || ""; } catch (e) { return ""; }
  }
  function persistFont(family) {
    try {
      if (family) localStorage.setItem(STORAGE_KEY, family);
      else localStorage.removeItem(STORAGE_KEY);
    } catch (e) { /* ignore storage errors */ }
  }

  // Restore the saved choice immediately so there is no font flash on load.
  applyFont(savedFont());

  function fetchFonts() {
    return fetch("/api/system/fonts")
      .then(function (r) { return r.ok ? r.json() : { fonts: FALLBACK_FONTS }; })
      .then(function (d) {
        return (d && d.fonts && d.fonts.length) ? d.fonts : FALLBACK_FONTS;
      })
      .catch(function () { return FALLBACK_FONTS; });
  }

  function el(tag, css, props) {
    var n = document.createElement(tag);
    if (css) n.style.cssText = css;
    if (props) Object.keys(props).forEach(function (k) { n[k] = props[k]; });
    return n;
  }

  function buildUI(fonts) {
    var current = savedFont();

    // Floating toggle button (bottom-right).
    var btn = el("button",
      "position:fixed;right:18px;bottom:18px;z-index:99999;width:44px;height:44px;" +
      "border-radius:50%;border:none;cursor:pointer;background:#2481cc;color:#fff;" +
      "box-shadow:0 4px 14px rgba(0,0,0,.35);font-size:18px;font-weight:700;",
      { title: "Reader font", textContent: "A" });

    // Panel.
    var panel = el("div",
      "position:fixed;right:18px;bottom:72px;z-index:99999;width:260px;max-height:60vh;" +
      "display:none;flex-direction:column;background:#17212b;color:#fff;" +
      "border:1px solid #101921;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.45);" +
      "overflow:hidden;font-family:" + WEB_SAFE_FALLBACKS + ";");

    var header = el("div",
      "padding:12px 14px;font-weight:700;font-size:14px;border-bottom:1px solid #101921;",
      { textContent: "Reader Font" });

    var search = el("input",
      "margin:10px;padding:8px 10px;border-radius:8px;border:1px solid #101921;" +
      "background:#0e1621;color:#fff;outline:none;",
      { type: "text", placeholder: "Search fonts\u2026" });

    var list = el("div", "overflow:auto;padding:0 6px 6px;flex:1 1 auto;");

    var reset = el("button",
      "margin:6px 10px 12px;padding:8px;border-radius:8px;border:1px solid #101921;" +
      "background:#202b38;color:#fff;cursor:pointer;",
      { textContent: "Reset to default" });

    function renderList(filter) {
      list.innerHTML = "";
      var q = (filter || "").toLowerCase();
      fonts.forEach(function (fam) {
        if (q && fam.toLowerCase().indexOf(q) === -1) return;
        var row = el("div",
          "padding:8px 10px;border-radius:8px;cursor:pointer;font-size:15px;" +
          (fam === current ? "background:#202b38;" : "") +
          "font-family:" + buildStack(fam) + ";",
          { textContent: fam });
        row.addEventListener("mouseenter", function () { row.style.background = "#202b38"; });
        row.addEventListener("mouseleave", function () {
          row.style.background = (fam === current ? "#202b38" : "transparent");
        });
        row.addEventListener("click", function () {
          current = fam;
          applyFont(fam);     // live preview / apply
          persistFont(fam);   // remember across sessions
          renderList(search.value);
        });
        list.appendChild(row);
      });
    }

    search.addEventListener("input", function () { renderList(search.value); });
    reset.addEventListener("click", function () {
      current = "";
      persistFont("");
      applyFont("");          // back to the stylesheet default stack
      renderList(search.value);
    });
    btn.addEventListener("click", function () {
      var open = (panel.style.display === "none" || !panel.style.display);
      panel.style.display = open ? "flex" : "none";
      if (open) search.focus();
    });

    panel.appendChild(header);
    panel.appendChild(search);
    panel.appendChild(list);
    panel.appendChild(reset);
    document.body.appendChild(panel);
    document.body.appendChild(btn);
    renderList("");
  }

  function init() { fetchFonts().then(buildUI); }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
