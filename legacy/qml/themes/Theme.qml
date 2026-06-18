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
    property string persianFontFamily: "Vazirmatn"
    // user-selectable accent override (empty = use the palette's accent)
    property string accentOverride: ""
    // chat wallpaper mode: "pattern", "solid", "none"
    property string wallpaperMode: "pattern"

    // ---------------------------------------------------------------------
    //  Palettes — exact Telegram Desktop tokens
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

    // Convenience accessors used across components
    readonly property color bg:            p.bg
    readonly property color panel:         p.panel
    readonly property color panelAlt:      p.panelAlt
    readonly property color hover:         p.hover
    readonly property color selection:     p.selection
    readonly property color accent:        accentOverride !== "" ? accentOverride : p.accent
    readonly property color accentText:    p.accentText
    readonly property color inBubble:      p.inBubble
    readonly property color outBubble:     p.outBubble
    readonly property color text:          p.text
    readonly property color textSecondary: p.secondary
    readonly property color divider:       p.divider
    readonly property color badge:         p.badge
    readonly property color badgeMuted:    p.badgeMuted
    readonly property color tick:          p.tick
    readonly property color link:          p.link
    readonly property color wallpaper:     p.wallpaper

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
