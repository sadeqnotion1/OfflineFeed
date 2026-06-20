pragma Singleton
import QtQuick

// Central design-token singleton. Holds the exact Telegram Desktop color
// palette for every variant, plus shared metrics, fonts and animation timings.
//
// ─────────────────────────────────────────────────────────────────────────
//  RED-ACCENT RETINT (this revision)
//  The neutral DARK surfaces used to be read straight from the stock blue
//  `night` palette, so a red accent looked bolted-on. They are now DERIVED by
//  tinting a hue-free grayscale anchor toward `accent` via tint(), and
//  selection/hover are expressed as accent-at-low-alpha. Change the single
//  `accentOverride` hex below and the ENTIRE dark UI re-tints coherently.
// ─────────────────────────────────────────────────────────────────────────
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
    // ★ SINGLE SOURCE OF TRUTH ★ — user-selectable accent override.
    //   Empty string ('') falls back to the palette's stock accent.
    //   Set to one hex here (or from Settings) and the whole UI re-tints:
    //   accent, selection, hover, badge, tick, link, outBubble AND every
    //   neutral surface (bg/panel/panelAlt/inBubble/divider/wallpaper/
    //   textSecondary) are all derived from it.
    property string accentOverride: "#e0534f"   // Telegram-red (assumed; change me)
    // chat wallpaper mode: "pattern", "solid", "none", "image"
    property string wallpaperMode: "pattern"
    // Item 8: file URI of a user-chosen wallpaper image (used when mode=="image")
    property string wallpaperImage: ""

    // ----- Post media layout (image legibility scrim) -----
    // ADDITIVE (06_image_overlay_scrim): controls how a post's title + meta are
    // laid out relative to its image.
    //   "below"   -> caption sits in the bubble UNDER the image (ORIGINAL
    //                behavior — this is the safe, non-breaking default).
    //   "overlay" -> title + meta are drawn ON the image, lifted above a
    //                bottom gradient scrim so they stay legible on bright
    //                images (Telegram-style). See MessageBubble.qml.
    // Flip this ONE value to switch the whole app, or set `overlayMode` on an
    // individual MessageBubble. Default stays "below" so existing UI is intact.
    property string postOverlayMode: "overlay"

    // ---------------------------------------------------------------------
    //  Palettes — exact Telegram Desktop tokens
    //  NOTE: the per-palette "selection", "badge", "tick" and "link" entries
    //  below are kept only as documentation / reference of Telegram's stock
    //  values. They are NO LONGER read directly by the UI — the accent-driven
    //  accessors further down derive those tokens from the single canonical
    //  `accent` so a custom accent recolors the whole app. (See ACCENT note.)
    //  In DARK variants the NEUTRAL surfaces are likewise no longer read from
    //  here; they are derived from `darkNeutral` + `accent` (see below). The
    //  light "day" variant still reads its neutrals straight from this table.
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

    // ---------------------------------------------------------------------
    //  DARK neutral anchors — a HUE-FREE grayscale lightness ladder.
    //  Because these carry no hue, tinting them toward a warm accent yields
    //  warm near-neutrals (never a bluish/purple cast — there is no competing
    //  blue base). The tint* amounts are intentionally subtle (comms-style,
    //  not neon). Used only for isDark variants.
    // ---------------------------------------------------------------------
    readonly property var darkNeutral: ({
        "bg":        "#161616",
        "panelAlt":  "#1c1c1c",
        "panel":     "#242424",
        "inBubble":  "#1e1e1e",
        "divider":   "#0f0f0f",
        "wallpaper": "#0d0d0d",
        "secondary": "#8a8a8a"
    })
    readonly property real tintBg:        0.08
    readonly property real tintPanel:     0.10
    readonly property real tintPanelAlt:  0.09
    readonly property real tintInBubble:  0.08
    readonly property real tintDivider:   0.10
    readonly property real tintWallpaper: 0.07
    readonly property real tintSecondary: 0.10

    // =====================================================================
    //  ★ CANONICAL ACCENT — SINGLE SOURCE OF TRUTH FOR THE ENTIRE QML UI ★
    //  -------------------------------------------------------------------
    //  `accent` is the ONE accent value for the whole app. Every accent-
    //  driven token below (accentText, selection, hover, badge, tick, link,
    //  outBubble and the accent* variants) AND every dark neutral surface is
    //  DERIVED from it, so changing the accent — either by switching theme
    //  variant OR by picking a custom `accentOverride` in Settings — recolors
    //  the UI coherently everywhere.
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

    // List-row state washes — subtle accent tints layered over the panel so the
    // active/hover row reads as a soft accent wash instead of a solid band.
    // Both are accent-derived (selection ~15% alpha, hover ~8% alpha), so a
    // custom accent recolors them automatically (stays on the accent pipeline).
    readonly property color selectionFill: Qt.rgba(accent.r, accent.g, accent.b, 0.15)
    readonly property color hoverFill:     Qt.rgba(accent.r, accent.g, accent.b, 0.08)

    // Accent-derived semantic tokens (previously static per-palette hexes).
    readonly property color badge:     accent
    readonly property color tick:      isDark ? Qt.lighter(accent, 1.25) : accent
    readonly property color link:      isDark ? Qt.lighter(accent, 1.12) : Qt.darker(accent, 1.06)

    // ----- Neutral / near-neutral tokens -----
    //  DARK variants: derived by tinting the hue-free `darkNeutral` anchors
    //  toward `accent`, so a warm accent => warm surfaces. The light "day"
    //  variant keeps its stock palette so the bright theme stays intact.
    //  Token NAMES are unchanged so every component keeps binding correctly.
    readonly property color bg:            isDark ? tint(darkNeutral.bg,        accent, tintBg)        : p.bg
    readonly property color panel:         isDark ? tint(darkNeutral.panel,     accent, tintPanel)     : p.panel
    readonly property color panelAlt:      isDark ? tint(darkNeutral.panelAlt,  accent, tintPanelAlt)  : p.panelAlt
    readonly property color inBubble:      isDark ? tint(darkNeutral.inBubble,  accent, tintInBubble)  : p.inBubble
    // Outgoing bubble reads as a muted accent surface (Telegram-style).
    readonly property color outBubble:     _mix(accent, bg, isDark ? 0.55 : 0.80)
    readonly property color text:          p.text
    readonly property color textSecondary: isDark ? tint(darkNeutral.secondary, accent, tintSecondary) : p.secondary
    readonly property color divider:       isDark ? tint(darkNeutral.divider,   accent, tintDivider)   : p.divider
    readonly property color badgeMuted:    p.badgeMuted
    readonly property color wallpaper:     isDark ? tint(darkNeutral.wallpaper, accent, tintWallpaper) : p.wallpaper

    // ----- Surface elevation tokens (plane separation for the 3-pane shell) -----
    readonly property color railBg:    panel       // folder rail (top chrome)
    readonly property color listBg:    panelAlt     // chat list (mid plane)
    readonly property color contentBg: bg           // chat view (base plane)
    readonly property color hairline:  isDark ? Qt.rgba(1, 1, 1, 0.06)
                                              : Qt.rgba(0, 0, 0, 0.08)

    // selection & hover: accent at LOW ALPHA instead of hard-coded blue.
    // Drawn over `bg`, these read as a subtle accent wash that matches the
    // accent for ANY accent value (selection ~15%, hover ~8% in dark).
    readonly property color selection: Qt.rgba(accent.r, accent.g, accent.b, isDark ? 0.15 : 0.12)
    readonly property color hover:     Qt.rgba(accent.r, accent.g, accent.b, isDark ? 0.08 : 0.06)

    // ----- Media overlay tokens (image legibility scrim) -----
    // ADDITIVE (06_image_overlay_scrim). Text drawn ON media is ALWAYS light,
    // independent of the light/dark variant, because it sits over a dark scrim
    // (never the theme background). `scrim`/`scrimMid` are the gradient stops
    // used by the bottom-anchored scrim in MessageBubble.qml; keeping them here
    // means a single place tunes media-overlay legibility app-wide.
    readonly property color onMedia:      "#ffffff"                  // overlaid title (max contrast)
    readonly property color onMediaMuted: Qt.rgba(1, 1, 1, 0.72)    // overlaid meta (muted but legible)
    readonly property color scrim:        Qt.rgba(0, 0, 0, 0.78)    // strongest stop, at the very bottom
    readonly property color scrimMid:     Qt.rgba(0, 0, 0, 0.55)    // mid stop, fades up to transparent

    // ----- Accent / blend helpers (the single accent pipeline) -----
    // tint(base, accent, amount): linear blend of `base` toward `accent`.
    //   amount=0 -> base, amount=1 -> accent. Returns an OPAQUE color.
    //   This is the reusable warm-neutral derivation helper.
    function tint(base, accent, amount) {
        return Qt.rgba(base.r + (accent.r - base.r) * amount,
                       base.g + (accent.g - base.g) * amount,
                       base.b + (accent.b - base.b) * amount,
                       1.0)
    }
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
    readonly property int bubbleRadius: radius.lg

    // ----- Corner radius scale (single source of truth) -----
    // Bind components to these tokens instead of hard-coding literal radius
    // numbers, so corner rounding stays consistent across cards, inputs,
    // chips, badges and avatars. (Sizes are unchanged - only corner radii.)
    //   sm   -> small chips / tags
    //   md   -> inputs / search fields
    //   lg   -> cards / message bubbles
    //   pill -> fully rounded (badges, avatars, pill buttons, toasts)
    // `pill` is a large constant; Qt clamps radius to min(w,h)/2, so it
    // yields a perfect pill for any height and a circle for square items.
    readonly property var radius: ({ "sm": 8, "md": 12, "lg": 18, "pill": 9999 })
    readonly property int avatarSize: 46
    readonly property int rowHeight: 70

    // ----- Spacing scale (09_spacing_density) -----
    // ★ SINGLE SOURCE OF TRUTH for margins & gaps ★. One 4px-based ladder used
    // app-wide so paddings/gaps line up on a consistent grid. Bind components
    // to these tokens instead of hard-coding literal margins/spacings.
    //   xs -> 4    tight inner gaps (stacked text lines)
    //   sm -> 8    small paddings / inline gaps (icon <-> text)
    //   md -> 12   standard row padding & avatar <-> text gap
    //   lg -> 16   section padding
    //   xl -> 20   large padding
    readonly property var space: ({ "xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 20 })

    // ----- List-row density (Telegram Desktop dialog-row spec) -----
    // Fixed geometry so every channel row is the same height and the avatar /
    // paddings / gaps all sit on the spacing grid above. rowHeight stays 70
    // (within the 64-72 Telegram range); the list-row avatar is its OWN token
    // (54) so other surfaces still using avatarSize (46) are left untouched.
    readonly property int rowAvatarSize: 54            // list-row avatar
    readonly property int rowPadding:    space.md       // leading / trailing inset = 12
    readonly property int rowGap:        space.md       // avatar <-> text gap      = 12
    readonly property int rowLineGap:    space.xs       // name <-> preview (vertical) = 4
    readonly property int rowInlineGap:  space.sm       // text <-> trailing meta (icons/time/badge) = 8
    // Text-block left edge — used by the row divider so it starts under the text.
    readonly property int rowTextInset:  rowPadding + rowAvatarSize + rowGap   // = 78

    // ----- Search header height (09_spacing_density) -----
    // Match the chat-list search header to the chat header so both top bars
    // align on the same scale (Telegram-style). Was a literal 54.
    readonly property int searchBarHeight: headerHeight   // = 56

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

    // ----- System-entry icon-avatar gradients -----
    // Dedicated, STABLE gradients for the special system entries so they render
    // as a purposeful TINTED gradient + glyph (see Avatar.qml) instead of a
    // flat single-color circle or a random hash color. Keyed by the avatarPath
    // sentinel Avatar.qml uses. Intentionally fixed (NOT accent-driven and NOT
    // hash-derived) so these rows look identical on every launch.
    readonly property var systemAvatarGradients: ({
        "bookmark": ["#4f8ff7", "#2a5fd0"],  // Saved Messages    - Telegram blue
        "archive":  ["#9aa7b6", "#5d6b7d"],  // Archived Messages - muted slate
        "logs":     ["#4db6ac", "#2a8f86"],  // System & App Logs - teal
        "trash":    ["#ff7a6b", "#e0534f"]   // Bin               - soft red
    })

    // True when `key` denotes a system icon-avatar (not a per-peer gradient).
    function isSystemAvatar(key) {
        return key === "bookmark" || key === "archive"
            || key === "logs" || key === "trash";
    }

    // Deterministic gradient for an icon-avatar key. Falls back to the regular
    // per-peer gradient set if an unknown key is passed (defensive - never
    // returns undefined, so the disc always has a valid 2-stop gradient).
    function iconGradientFor(key) {
        return systemAvatarGradients[key] ? systemAvatarGradients[key]
                                          : gradientFor(key);
    }
}
