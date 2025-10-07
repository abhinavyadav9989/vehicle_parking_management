
# ui/theme_light.py (professional polish)
import tkinter as tk
from tkinter import ttk

PALETTE = {
    "bg": "#F7FAFF",
    "panel": "#FFFFFF",
    "muted": "#64748B",
    "text": "#0F172A",
    "border": "#E7EEF8",
    "primary": "#2563EB",
    "primary-ghost": "#EFF6FF",
    "success": "#16A34A",
    "warn": "#F59E0B",
    "danger": "#EF4444",
}

def setup_style(root: tk.Misc):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=PALETTE["bg"])

    base_font = ("Segoe UI", 10)
    style.configure(".", background=PALETTE["bg"], foreground=PALETTE["text"], font=base_font)
    style.configure("TFrame", background=PALETTE["bg"])
    style.configure("TLabel", background=PALETTE["bg"], foreground=PALETTE["text"])

    # Panels & Labels
    style.configure("Panel.TFrame", background=PALETTE["panel"])
    style.configure("Panel.TLabel", background=PALETTE["panel"], foreground=PALETTE["text"])
    style.configure("Muted.TLabel", background=PALETTE["panel"], foreground=PALETTE["muted"])

    # Sidebar
    style.configure("Sidebar.TFrame", background=PALETTE["bg"])
    style.configure("SidebarHeading.TLabel", background=PALETTE["bg"], foreground=PALETTE["muted"], font=("Segoe UI Semibold", 10))

    # Navigation
    style.configure("Nav.TButton", background=PALETTE["bg"], foreground=PALETTE["text"],
                    anchor="w", relief="flat", padding=(14,10))
    style.map("Nav.TButton",
              background=[("active", PALETTE["primary-ghost"])],
              relief=[("pressed", "flat")])

    style.configure("NavSelected.TButton", background=PALETTE["primary-ghost"], foreground=PALETTE["text"],
                    anchor="w", relief="flat", padding=(14,10))
    style.map("NavSelected.TButton", background=[("active", PALETTE["primary-ghost"])])

    # Buttons
    style.configure("Primary.TButton", background=PALETTE["primary"], foreground="#FFFFFF",
                    padding=(14,8), relief="flat")
    style.map("Primary.TButton",
              background=[("active", "#1D4ED8")],
              relief=[("pressed", "flat")])

    # Cards
    style.configure("Card.TFrame", background=PALETTE["panel"], relief="flat",
                    borderwidth=1, highlightthickness=1, highlightbackground=PALETTE["border"])
    style.configure("KPI.TFrame", background=PALETTE["panel"], relief="flat",
                    borderwidth=1, highlightthickness=1, highlightbackground=PALETTE["border"])

    # Headings
    style.configure("H1.TLabel", font=("Segoe UI Semibold", 22), foreground=PALETTE["text"], background=PALETTE["panel"])
    style.configure("H2.TLabel", font=("Segoe UI Semibold", 12), foreground=PALETTE["text"], background=PALETTE["panel"])
    style.configure("Subdued.TLabel", font=("Segoe UI", 10), foreground=PALETTE["muted"], background=PALETTE["panel"])

    # Pills / list rows
    style.configure("Pill.TFrame", background="#F1F5F9", relief="flat", borderwidth=0)
    style.configure("Pill.TLabel", background="#F1F5F9", foreground=PALETTE["text"])

    # Divider line
    style.configure("Divider.TFrame", background=PALETTE["border"])
