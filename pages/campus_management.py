# Campus Management Dashboard
from tkinter import ttk

# Rendering the campus management dashboard
def render(parent, user=None, on_logout=None):
    fm = ttk.Frame(parent, padding=40)
    fm.pack(fill="both", expand=True)
    ttk.Label(fm, text="Campus Management Dashboard", font=("Segoe UI Semibold", 22)).pack(pady=(0, 16))
    
    if user and user.get("full_name"):
        ttk.Label(fm, text=f"Welcome, {user['full_name']}!", font=("Segoe UI", 12)).pack(pady=(0, 12))
    ttk.Label(fm, text="Administrative tools will be added soon.", font=("Segoe UI", 11)).pack(pady=(0, 24))

    if on_logout is not None:
        ttk.Button(fm, text="Logout", command=on_logout).pack()
    return fm


