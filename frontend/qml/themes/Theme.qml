pragma Singleton
import QtQuick

// Central design-token singleton. Holds the exact Telegram Desktop color
// palette for every variant, plus shared metrics, fonts and animation timings.
QtObject {
    id: theme

    // ----- Active selections (driven by the Python bridge / SettingsPage) -----
    // variant: "night" (Tinted dark default), "day", "classic", "tinted"
    property string variant: "night"
    property bool isDark: variant === "night" || variant === "classic" || variant === "tinted"
    property bool rtl: false
    property string fontFamily: "Roboto"
    // Item 1: offline-reader font, independent from the chat/UI fontFamily.
    property string readerFontFamily: "Roboto"
    property string persianFontFamily: "Vazirmatn"
    // Ultimate safe default used by the Font Family picker when a previously
    // saved font is no longer installed on this machine.
    property string fallbackFontFamily: "Roboto"
    // user-selectable accent override (empty = use the palette's accent)
    property string accentOverride: ""
    // chat wallpaper mode: "pattern", "solid", "none", "image"
    property string wallpaperMode: "pattern"
    // Item 8: file URI of a user-chosen wallpaper image (used when mode=="image")
    property string wallpaperImage: ""

    // ---------------------------------------------------------------------
    //  Palettes — exact Telegram Desktop tokens
    //  NOTE: the per-palette "selection", "badge", "tick" and "link" entries
    //  below are kept only as documentation / reference of Telegram's stock
    //  values. They are NO LONGER read directly by the UI — the accent-driven
    //  accessors further down derive those tokens from the single canonical
    //  `accent` so a custom accent recolors the whole app. (See ACCENT note.)
    // ---------------------------------------------------------------------
    readonly property var palettes: ({
        "night": {
            "bg":            "#17212b",
            "panel":         "#232e3c",
            "panelAlt":      "#1d2733",
            "hover":         "#202b38",
            "selection":     "#2b5278",
            "accent":        "#5288c1",
            "accentText":    "#ffffff",
            "inBubble":      "#182533",
            "outBubble":     "#2b5278",
            "text":          "#ffffff",
            "secondary":     "#7f91a4",
            "divider":       "#101921",
            "badge":         "#5288c1",
            "badgeMuted":    "#6c7883",
            "tick":          "#5fb0e5",
            "link":          "#62a0d4",
            "wallpaper":     "#0e1621"
        },
        "classic": {
            "bg":            "#18222d",
            "panel":         "#222e3a",
            "panelAlt":      "#1b2631",
            "hover":         "#1f2a35",
            "selection":     "#2b5278",
            "accent":        "#56a3eb",
            "accentText":    "#ffffff",
            "inBubble":      "#182533",
            "outBubble":     "#2b5278",
            "text":          "#ffffff",
            "secondary":     "#7f91a4",
            "divider":       "#0f1820",
            "badge":         "#56a3eb",
            "badgeMuted":    "#6c7883",
            "tick":          "#5fb0e5",
            "link":          "#62a0d4",
            "wallpaper":     "#0e1621"
        },
        "tinted": {
            "bg":            "#1a1a2e",
            "panel":         "#24243e",
            "panelAlt":      "#1f1f38",
            "hover":         "#262642",
            "selection":     "#3e4b7a",
            "accent":        "#7a8cff",
            "accentText":    "#ffffff",
            "inBubble":      "#1e1e3a",
            "outBubble":     "#3e4b7a",
            "text":          "#ffffff",
            "secondary":     "#8a8aa8",
            "divider":       "#121225",
            "badge":         "#7a8cff",
            "badgeMuted":    "#6c6c88",
            "tick":          "#9fb0ff",
            "link":          "#9aa8ff",
            "wallpaper":     "#12122a"
        },
        "day": {
            "bg":            "#ffffff",
            "panel":         "#ffffff",
            "panelAlt":      "#f4f4f5",
            "hover":         "#f1f1f2",
            "selection":     "#e9f3ff",
            "accent":        "#3390ec",
            "accentText":    "#ffffff",
            "inBubble":      "#ffffff",
            "outBubble":     "#effdde",
            "text":          "#000000",
            "secondary":     "#707579",
            "divider":       "#e6e6e8",
            "badge":         "#3390ec",
            "badgeMuted":    "#a8b0b8",
            "tick":          "#4fae4e",
            "link":          "#168acd",
            "wallpaper":     "#dbe6d9"
        }
    })

    readonly property var p: palettes[variant] ? palettes[variant] : palettes["night"]

    // =====================================================================
    //  ★ CANONICAL ACCENT — SINGLE SOURCE OF TRUTH FOR THE ENTIRE QML UI ★
    //  -------------------------------------------------------------------
    //  `accent` is the ONE accent value for the whole app. Every accent-
    //  driven token below (accentText, selection, badge, tick, link and the
    //  accent* variants) is DERIVED from it, so changing the accent — either
    //  by switching theme variant OR by picking a custom `accentOverride` in
    //  Settings — recolors the UI coherently everywhere.
    //
    //  GUARD (do not regress): never hard-code an accent-equivalent hex in a
    //  component. Bind to Theme.accent / Theme.accentText / Theme.selection /
    //  Theme.badge / Theme.tick / Theme.link / Theme.accentHover /
    //  Theme.accentPressed / Theme.accentFill / Theme.accentBorder, or add a
    //  new derived token HERE so it stays on the single accent pipeline.
    // =====================================================================
    readonly property color accent: accentOverride !== "" ? accentOverride : p.accent

    // Contrast-safe foreground for content placed ON the accent surface.
    // Picks dark ink on light accents and white on dark accents so accent
    // buttons/badges keep readable text for ANY accent value (WCAG-aware).
    readonly property color accentText: _readableOn(accent)

    // Derived accent variants — use these instead of new standalone hexes.
    readonly property color accentHover:   Qt.lighter(accent, 1.12)
    readonly property color accentPressed: Qt.darker(accent, 1.12)
    readonly property color accentFill:    Qt.rgba(accent.r, accent.g, accent.b, 0.15) // translucent fill
    readonly property color accentBorder:  Qt.rgba(accent.r, accent.g, accent.b, 0.45) // focus/border tint

    // Accent-derived semantic tokens (previously static per-palette hexes).
    // selection blends the accent toward the background so it reads as a
    // muted accent tint in both dark and light modes.
    readonly property color selection: _mix(accent, bg, isDark ? 0.62 : 0.86)
    readonly property color badge:     accent
    readonly property color tick:      isDark ? Qt.lighter(accent, 1.25) : accent
    readonly property color link:      isDark ? Qt.lighter(accent, 1.12) : Qt.darker(accent, 1.06)

    // ----- Neutral / non-accent tokens (intentionally palette-driven) -----
    readonly property color bg:            p.bg
    readonly property color panel:         p.panel
    readonly property color panelAlt:      p.panelAlt
    readonly property color hover:         p.hover
    readonly property color inBubble:      p.inBubble
    readonly property color outBubble:     p.outBubble
    readonly property color text:          p.text
    readonly property color textSecondary: p.secondary
    readonly property color divider:       p.divider
    readonly property color badgeMuted:    p.badgeMuted
    readonly property color wallpaper:     p.wallpaper

    // ----- Accent helpers (the single accent pipeline) -----
    // Linear blend of two colors. t=0 -> c1, t=1 -> c2. Returns opaque color.
    function _mix(c1, c2, t) {
        return Qt.rgba(c1.r + (c2.r - c1.r) * t,
                       c1.g + (c2.g - c1.g) * t,
                       c1.b + (c2.b - c1.b) * t,
                       1.0)
    }
    // Relative luminance (sRGB-ish, good enough for picking ink color).
    function _luminance(c) {
        return 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b
    }
    // Contrast-safe ink for text/icons drawn on top of color `c`.
    function _readableOn(c) {
        return _luminance(c) > 0.6 ? "#101010" : "#ffffff"
    }

    // ----- Metrics -----
    readonly property int railWidth: 72
    readonly property int chatListWidth: 320
    readonly property int infoPanelWidth: 340
    readonly property int titleBarHeight: 44
    readonly property int headerHeight: 56
    readonly property int bubbleRadius: 13
    readonly property int avatarSize: 46
    readonly property int rowHeight: 70

    // ----- Animation -----
    readonly property int anim: 180
    readonly property int animFast: 140
    readonly property int easing: Easing.OutCubic

    // ----- Avatar gradients (Telegram's per-peer color set) -----
    // NOTE: these are intentionally NOT accent-driven. Telegram colors each
    // peer avatar from a fixed multi-hue set for visual distinction.
    readonly property var avatarGradients: [
        ["#ff885e", "#ff516a"], // red
        ["#ffcd6a", "#ffa85c"], // orange
        ["#a0de7e", "#54cb68"], // green
        ["#82b1ff", "#665fff"], // blue/violet
        ["#72d5fd", "#2a9ef1"], // cyan
        ["#e0a2f3", "#d669ed"], // purple
        ["#ffa3a3", "#ff5b9b"]  // pink
    ]

    function gradientFor(key) {
        var h = 0;
        var s = key ? key : "";
        for (var i = 0; i < s.length; i++)
            h = (s.charCodeAt(i) + ((h << 5) - h)) | 0;
        var idx = Math.abs(h) % avatarGradients.length;
        return avatarGradients[idx];
    }
}
