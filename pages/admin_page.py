import tkinter as tk
from tkinter import ttk, messagebox
from services.admin_service import AdminService

_admin = AdminService()


def render(parent, on_logout, current_user=None):
    wrapper = ttk.Frame(parent)
    wrapper.grid(row=0, column=0)

    # Topbar
    bar = ttk.Frame(wrapper)
    bar.grid(row=0, column=0, sticky="ew")
    bar.grid_columnconfigure(0, weight=1)
    title = ttk.Label(bar, text="Campus Management Dashboard")
    title.configure(font=("Segoe UI Semibold", 13))
    title.grid(row=0, column=0, sticky="w")
    ttk.Button(bar, text="Logout", command=on_logout).grid(row=0, column=1, sticky="e")

    # Tabs
    tabs_card = ttk.Frame(wrapper)
    tabs_card.grid(row=1, column=0, padx=24, pady=12, sticky="n")
    nb = ttk.Notebook(tabs_card)
    nb.grid(row=0, column=0)

    dash_tab = ttk.Frame(nb)
    verify_tab = ttk.Frame(nb)
    flags_tab = ttk.Frame(nb)

    nb.add(dash_tab, text="Dashboard")
    nb.add(verify_tab, text="Verification")
    nb.add(flags_tab, text="Flags")

    # Dashboard KPIs
    kpi_row = ttk.Frame(dash_tab)
    kpi_row.grid(row=0, column=0, pady=(0, 12))
    def chip(lbl, val):
        f = ttk.Labelframe(kpi_row, text=lbl, style="Glass.TLabelframe")
        ttk.Label(f, text=str(val)).grid(row=0, column=0, padx=8, pady=8)
        return f
    chips = [
        ("Users", _admin.count_users()),
        ("Guards", _admin.count_guards()),
        ("Vehicles", _admin.count_vehicles()),
        ("Open Flags", _admin.count_open_flags()),
    ]
    for idx, (lbl, val) in enumerate(chips):
        chip(lbl, val).grid(row=0, column=idx, padx=6)

    # Verification queue
    rows = _admin.list_pending_verifications()
    ttk.Label(verify_tab, text=f"Pending: {len(rows)}").grid(row=0, column=0, padx=8, pady=8, sticky="w")
    for i, r in enumerate(rows, start=1):
        row_f = ttk.Frame(verify_tab)
        row_f.grid(row=i, column=0, sticky="w", pady=4)
        ttk.Label(row_f, text=f"{r['full_name']} ({r['email']})").grid(row=0, column=0, padx=8)
        def _approve(r=r):
            try:
                _admin.set_verification_status(r['id'], reviewer_id=(current_user or {}).get('id') or 0, status='approved')
                messagebox.showinfo("Verify", "Approved.")
            except Exception as e:
                messagebox.showerror("Verify", str(e))
        def _reject(r=r):
            try:
                _admin.set_verification_status(r['id'], reviewer_id=(current_user or {}).get('id') or 0, status='rejected')
                messagebox.showinfo("Verify", "Rejected.")
            except Exception as e:
                messagebox.showerror("Verify", str(e))
        ttk.Button(row_f, text="Approve", style="Role.TButton", command=_approve).grid(row=0, column=1, padx=6)
        ttk.Button(row_f, text="Reject", style="Role.TButton", command=_reject).grid(row=0, column=2, padx=6)

    # Flags
    flags = _admin.list_open_flags()
    ttk.Label(flags_tab, text=f"Open Flags: {len(flags)}").grid(row=0, column=0, padx=8, pady=8, sticky="w")
    for i, f in enumerate(flags, start=1):
        row_f = ttk.Frame(flags_tab)
        row_f.grid(row=i, column=0, sticky="w", pady=4)
        ttk.Label(row_f, text=f"#{f['id']} - {f['reason']} by {f['raised_by']} at {f['created_at']}").grid(row=0, column=0, padx=8)
        note_var = tk.StringVar(value="")
        ttk.Entry(row_f, textvariable=note_var, width=30).grid(row=0, column=1, padx=6)
        def _close(f=f, note_var=note_var):
            try:
                _admin.close_flag(f['id'], admin_user_id=(current_user or {}).get('id') or 0, note=note_var.get() or None)
                messagebox.showinfo("Flag", "Closed.")
            except Exception as e:
                messagebox.showerror("Flag", str(e))
        ttk.Button(row_f, text="Close", style="Role.TButton", command=_close).grid(row=0, column=2, padx=6)

    return wrapper


