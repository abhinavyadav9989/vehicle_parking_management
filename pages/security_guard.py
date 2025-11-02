# Security guard pages
from tkinter import ttk

# ecurity Guard Dashboard Page
def render(parent, user=None, on_logout=None):
    fm = ttk.Frame(parent, padding=40)
    fm.pack(fill="both", expand=True)
    ttk.Label(fm, text="Security Guard Dashboard", font=("Segoe UI Semibold", 22)).pack(pady=(0, 16))
    if user and user.get("full_name"):
        ttk.Label(fm, text=f"Welcome, {user['full_name']}!", font=("Segoe UI", 12)).pack(pady=(0, 12))

    ttk.Label(fm, text="Gate operations tools will appear here soon.", font=("Segoe UI", 11)).pack(pady=(0, 24))

    if on_logout is not None:
        ttk.Button(fm, text="Logout", command=on_logout).pack()
    return fm

