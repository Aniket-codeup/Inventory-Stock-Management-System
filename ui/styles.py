import tkinter as tk
from tkinter import ttk

# Color Palette
COLOR_SIDEBAR_BG = "#0f172a"      # Deep slate / Navy 900
COLOR_SIDEBAR_HEADER = "#1e293b"  # Slate 800
COLOR_SIDEBAR_HOVER = "#334155"   # Slate 700
COLOR_SIDEBAR_ACTIVE = "#2563eb"  # Vibrant Royal Blue
COLOR_SIDEBAR_TEXT = "#e2e8f0"    # Light slate

COLOR_BG = "#f8fafc"              # Crisp slate 50
COLOR_CARD_BG = "#ffffff"         # Clean white
COLOR_BORDER = "#e2e8f0"          # Light border
COLOR_TEXT_PRIMARY = "#0f172a"    # Dark slate 900
COLOR_TEXT_SECONDARY = "#64748b"  # Slate 500

# Status & Accent Colors
COLOR_PRIMARY = "#2563eb"         # Blue 600
COLOR_SUCCESS = "#10b981"         # Emerald 500 (In Stock)
COLOR_WARNING = "#f59e0b"         # Amber 500 (Low Stock)
COLOR_DANGER = "#ef4444"          # Rose 500 (Out of Stock)
COLOR_PURPLE = "#8b5cf6"          # Purple 500

# Modern Fonts
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SUBTITLE = ("Segoe UI", 12, "bold")
FONT_HEADING = ("Segoe UI", 11, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_STAT_NUM = ("Segoe UI", 18, "bold")

def setup_modern_styles(root: tk.Tk):
    """Configure modern ttk styles for the entire desktop application."""
    style = ttk.Style(root)
    # Use 'clam' or 'alt' as base engine if available for full color control
    available_themes = style.theme_names()
    if "clam" in available_themes:
        style.theme_use("clam")

    # General Frames
    style.configure("TFrame", background=COLOR_BG)
    style.configure("Card.TFrame", background=COLOR_CARD_BG, relief="solid", borderwidth=1)
    style.configure("Sidebar.TFrame", background=COLOR_SIDEBAR_BG)
    style.configure("SidebarHeader.TFrame", background=COLOR_SIDEBAR_HEADER)

    # General Labels
    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT_PRIMARY, font=FONT_BODY)
    style.configure("Card.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_PRIMARY, font=FONT_BODY)
    style.configure("CardTitle.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_SECONDARY, font=FONT_HEADING)
    style.configure("CardStat.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_PRIMARY, font=FONT_STAT_NUM)
    style.configure("HeaderTitle.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_PRIMARY, font=FONT_TITLE)
    style.configure("HeaderSub.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_SECONDARY, font=FONT_SMALL)

    # Sidebar Buttons
    style.configure(
        "Sidebar.TButton",
        background=COLOR_SIDEBAR_BG,
        foreground=COLOR_SIDEBAR_TEXT,
        font=FONT_HEADING,
        borderwidth=0,
        focuscolor=COLOR_SIDEBAR_ACTIVE,
        anchor="w",
        padding=(16, 10)
    )
    style.map(
        "Sidebar.TButton",
        background=[("active", COLOR_SIDEBAR_HOVER), ("pressed", COLOR_SIDEBAR_ACTIVE)],
        foreground=[("active", "#ffffff")]
    )

    style.configure(
        "SidebarActive.TButton",
        background=COLOR_SIDEBAR_ACTIVE,
        foreground="#ffffff",
        font=FONT_HEADING,
        borderwidth=0,
        anchor="w",
        padding=(16, 10)
    )

    # Primary Action Buttons
    style.configure(
        "Primary.TButton",
        background=COLOR_PRIMARY,
        foreground="#ffffff",
        font=FONT_BODY_BOLD,
        borderwidth=0,
        padding=(12, 6)
    )
    style.map(
        "Primary.TButton",
        background=[("active", "#1d4ed8"), ("pressed", "#1e40af")]
    )

    # Success Buttons
    style.configure(
        "Success.TButton",
        background=COLOR_SUCCESS,
        foreground="#ffffff",
        font=FONT_BODY_BOLD,
        borderwidth=0,
        padding=(12, 6)
    )
    style.map(
        "Success.TButton",
        background=[("active", "#059669")]
    )

    # Danger Buttons
    style.configure(
        "Danger.TButton",
        background=COLOR_DANGER,
        foreground="#ffffff",
        font=FONT_BODY_BOLD,
        borderwidth=0,
        padding=(12, 6)
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#dc2626")]
    )

    # Secondary Buttons
    style.configure(
        "Secondary.TButton",
        background="#e2e8f0",
        foreground=COLOR_TEXT_PRIMARY,
        font=FONT_BODY,
        borderwidth=0,
        padding=(10, 6)
    )
    style.map(
        "Secondary.TButton",
        background=[("active", "#cbd5e1")]
    )

    # Modern Treeview Styling
    style.configure(
        "Treeview",
        background="#ffffff",
        foreground=COLOR_TEXT_PRIMARY,
        rowheight=28,
        fieldbackground="#ffffff",
        font=FONT_BODY,
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        background="#f1f5f9",
        foreground=COLOR_TEXT_PRIMARY,
        font=FONT_HEADING,
        relief="flat",
        padding=(6, 6)
    )
    style.map(
        "Treeview",
        background=[("selected", "#dbeafe")],
        foreground=[("selected", "#1e3a8a")]
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#e2e8f0")]
    )

    # Notebook Tabs
    style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
    style.configure("TNotebook.Tab", background="#e2e8f0", foreground=COLOR_TEXT_PRIMARY, padding=(14, 6), font=FONT_HEADING)
    style.map("TNotebook.Tab", background=[("selected", COLOR_CARD_BG)], foreground=[("selected", COLOR_PRIMARY)])

    # Entry and Combobox
    style.configure("TEntry", fieldbackground="#ffffff", padding=5)
    style.configure("TCombobox", fieldbackground="#ffffff", padding=4)

def configure_treeview_tags(tree: ttk.Treeview):
    """Configure row background colors and badge highlights for stock status."""
    tree.tag_configure("evenrow", background="#ffffff")
    tree.tag_configure("oddrow", background="#f8fafc")
    tree.tag_configure("status_in_stock", foreground="#047857", font=FONT_BODY_BOLD)       # Emerald green
    tree.tag_configure("status_low_stock", foreground="#b45309", font=FONT_BODY_BOLD)      # Amber orange
    tree.tag_configure("status_out_of_stock", foreground="#b91c1c", font=FONT_BODY_BOLD)   # Rose red
