"""Campus management / admin dashboard placeholder UI."""

from tkinter import ttk


def render(parent, user=None, on_logout=None):
    """Render the campus management dashboard page."""
    frame = ttk.Frame(parent, padding=40)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame,
        text="Campus Management Dashboard",
        font=("Segoe UI Semibold", 22),
    ).pack(pady=(0, 16))

    if user and user.get("full_name"):
        ttk.Label(
            frame,
            text=f"Welcome, {user['full_name']}!",
            font=("Segoe UI", 12),
        ).pack(pady=(0, 12))

    ttk.Label(
        frame,
        text="Administrative tools will be added soon.",
        font=("Segoe UI", 11),
    ).pack(pady=(0, 24))

    if on_logout is not None:
        ttk.Button(
            frame,
            text="Logout",
            command=on_logout,
        ).pack()

    return frame

