
import tkinter as tk
from tkinter import ttk, messagebox
from services.member_service import MemberService
from ui.theme_light import setup_style
from ui.widgets import card, kpi_card, pill_row

_member = MemberService()

def render(parent, on_logout, current_user=None):
    for w in parent.winfo_children():
        w.destroy()

    setup_style(parent)

    root = ttk.Frame(parent, style="TFrame")
    root.grid(row=0, column=0, sticky="nsew")
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)

    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)

    uid = (current_user or {}).get("id") or 0
    name = (current_user or {}).get("full_name", "Student")

    # Sidebar
    sidebar = ttk.Frame(root, style="Sidebar.TFrame")
    sidebar.grid(row=0, column=0, sticky="nsw", padx=(8, 0), pady=8)
    sidebar.configure(width=230)
    sidebar.grid_propagate(False)

    ttk.Label(sidebar, text="Campus Parking", style="SidebarHeading.TLabel").grid(row=0, column=0, sticky="w", padx=16, pady=(8, 14))

    nav_state = {"active": "dashboard"}
    nav_buttons = {}

    def nav_btn(text, key, row, icon=""):
        def _click():
            set_active(key)
        style = "NavSelected.TButton" if nav_state["active"] == key else "Nav.TButton"
        b = ttk.Button(sidebar, text=(f"{icon}  {text}" if icon else text), style=style, command=_click)
        b.grid(row=row, column=0, sticky="ew", padx=8, pady=4)
        nav_buttons[key] = b

    nav_btn("Dashboard", "dashboard", 1, icon="🗂")
    nav_btn("My Slot",   "slot",      2, icon="🚘")
    nav_btn("Profile",   "profile",   3, icon="🧑‍🎓")

    spacer = ttk.Frame(sidebar, style="Sidebar.TFrame")
    spacer.grid(row=9, column=0, sticky="nsew")
    sidebar.grid_rowconfigure(9, weight=1)
    ttk.Separator(sidebar, orient="horizontal").grid(row=10, column=0, sticky="ew", padx=8, pady=(8, 6))
    ttk.Button(sidebar, text="Logout", style="Nav.TButton", command=on_logout).grid(row=11, column=0, sticky="ew", padx=8, pady=(0, 8))

    # Main panel
    main_panel = ttk.Frame(root, style="Panel.TFrame")
    main_panel.grid(row=0, column=1, sticky="nsew", padx=16, pady=12)
    main_panel.grid_columnconfigure(0, weight=1)

    content = ttk.Frame(main_panel, style="Panel.TFrame")
    content.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
    content.grid_columnconfigure(0, weight=1)

    # Views
    view_dashboard = ttk.Frame(content, style="Panel.TFrame")
    view_slot      = ttk.Frame(content, style="Panel.TFrame")
    view_profile   = ttk.Frame(content, style="Panel.TFrame")
    for v in (view_dashboard, view_slot, view_profile):
        v.grid(row=0, column=0, sticky="nsew")
        v.grid_remove()

    # ===== DASHBOARD
    header = ttk.Label(view_dashboard, text=f"Welcome, {name}", style="H1.TLabel")
    header.grid(row=0, column=0, sticky="w")
    ttk.Label(view_dashboard, text="Manage your parking and profile", style="Subdued.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 16))

    kpis = ttk.Frame(view_dashboard, style="Panel.TFrame")
    kpis.grid(row=2, column=0, sticky="ew", pady=(0, 18))
    for i in range(3): kpis.grid_columnconfigure(i, weight=1)

    k0, lbl_reg_count = kpi_card(kpis, "🚗", "Registered Vehicles");   k0.grid(row=0, column=0, sticky="ew", padx=(0,14))
    k1, lbl_ver       = kpi_card(kpis, "✅", "Verification Status");   k1.grid(row=0, column=1, sticky="ew", padx=(0,14))
    k2, lbl_state     = kpi_card(kpis, "🕒", "Current Status");        k2.grid(row=0, column=2, sticky="ew")

    cp = card(view_dashboard, columns=2); cp.grid(row=3, column=0, sticky="ew")
    ttk.Label(cp.inner, text="Current Parking", style="H2.TLabel").grid(row=0, column=0, sticky="w", pady=(0,10), columnspan=2)
    ttk.Label(cp.inner, text="Slot Number", style="Subdued.TLabel").grid(row=1, column=0, sticky="w", padx=(0,24))
    lbl_slot = ttk.Label(cp.inner, text="—", style="Panel.TLabel"); lbl_slot.grid(row=2, column=0, sticky="w", padx=(0,24))
    ttk.Label(cp.inner, text="Vehicle", style="Subdued.TLabel").grid(row=1, column=1, sticky="w", padx=(0,24))
    lbl_vehicle = ttk.Label(cp.inner, text="—", style="Panel.TLabel"); lbl_vehicle.grid(row=2, column=1, sticky="w", padx=(0,24))
    ttk.Label(cp.inner, text="Entry Time", style="Subdued.TLabel").grid(row=3, column=0, sticky="w", pady=(10,0))
    lbl_entry = ttk.Label(cp.inner, text="—", style="Panel.TLabel"); lbl_entry.grid(row=4, column=0, sticky="w")

    yc = card(view_dashboard); yc.grid(row=4, column=0, sticky="ew", pady=(16,0))
    ttk.Label(yc.inner, text="Your Vehicles", style="H2.TLabel").grid(row=0, column=0, sticky="w", pady=(0,10))
    vehicles_list_container = ttk.Frame(yc.inner, style="Panel.TFrame"); vehicles_list_container.grid(row=1, column=0, sticky="ew")
    vehicles_list_container.grid_columnconfigure(0, weight=1)

    # ===== SLOT
    ttk.Label(view_slot, text="My Parking Slot", style="H1.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Label(view_slot, text="Your current parking information", style="Subdued.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 16))

    sc = card(view_slot); sc.grid(row=2, column=0, sticky="ew")
    lbl_slot_big = ttk.Label(sc.inner, text="—", style="H1.TLabel"); lbl_slot_big.grid(row=0, column=0, columnspan=3, sticky="w", pady=(4, 2))
    ttk.Label(sc.inner, text="Your assigned slot", style="Subdued.TLabel").grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 8))

    tiles = ttk.Frame(sc.inner, style="Panel.TFrame"); tiles.grid(row=2, column=0, sticky="w")
    for i in range(3): tiles.grid_columnconfigure(i, weight=0)
    def mini(parent, col, title):
        m = card(parent, padding=(12,12)); m.grid(row=0, column=col, padx=(0 if col==0 else 12, 0), pady=(4,4))
        ttk.Label(m.inner, text=title, style="Subdued.TLabel").grid(row=0, column=0, sticky="w")
        v = ttk.Label(m.inner, text="—", style="Panel.TLabel"); v.grid(row=1, column=0, sticky="w", pady=(2,0)); return v
    lbl_tile_vehicle = mini(tiles, 0, "Vehicle Number")
    lbl_tile_entry   = mini(tiles, 1, "Entry Time")
    lbl_tile_duration= mini(tiles, 2, "Duration")

    # ===== PROFILE
    ttk.Label(view_profile, text="Profile", style="H1.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Label(view_profile, text="Your account information", style="Subdued.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 16))

    pc = card(view_profile); pc.grid(row=2, column=0, sticky="ew")
    email = (current_user or {}).get('email', '—')
    college_id = (current_user or {}).get('college_id', '—')
    ttk.Label(pc.inner, text=name, style="H2.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
    ttk.Label(pc.inner, text=f"Email\\n{email}", style="Panel.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 2))
    ttk.Label(pc.inner, text=f"College ID\\n{college_id}", style="Panel.TLabel").grid(row=2, column=0, sticky="w", pady=(4, 8))

    vehicles_profile = card(pc.inner); vehicles_profile.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    ttk.Label(vehicles_profile.inner, text="Registered Vehicles", style="H2.TLabel").grid(row=0, column=0, sticky="w", pady=(0,8))
    vehicles_profile_list = ttk.Frame(vehicles_profile.inner, style="Panel.TFrame"); vehicles_profile_list.grid(row=1, column=0, sticky="w")
    add_row = ttk.Frame(vehicles_profile.inner, style="Panel.TFrame"); add_row.grid(row=2, column=0, sticky="w", pady=(8, 4))

    new_plate = tk.StringVar(value="")
    ttk.Entry(add_row, textvariable=new_plate, width=20).grid(row=0, column=0, padx=(0, 8))
    def _add_vehicle_profile():
        if not new_plate.get().strip(): return
        try:
            _member.add_vehicle(uid, new_plate.get().strip())
            messagebox.showinfo("Vehicles", "Vehicle added.")
            refresh_dashboard(); refresh_profile()
        except Exception as e:
            messagebox.showerror("Vehicles", str(e))
    ttk.Button(add_row, text="Add Vehicle", style="Primary.TButton", command=_add_vehicle_profile).grid(row=0, column=1)

    # ===== DATA HOOKS
    def refresh_dashboard():
        rows = _member.list_vehicles(uid)
        lbl_reg_count.config(text=str(len(rows)))
        for w in vehicles_list_container.winfo_children(): w.destroy()
        for i, v in enumerate(rows): pill_row(vehicles_list_container, v["plate_number"], row=i)
        v_status = _member.get_verification_status(uid); lbl_ver.config(text=v_status.capitalize())
        slot = _member.get_assigned_slot(uid)
        if slot:
            lbl_state.config(text="Parked"); lbl_slot.config(text=slot["code"])
            lbl_vehicle.config(text=rows[0]["plate_number"] if rows else "—")
            lbl_entry.config(text=str(slot["entry_time"]))
        else:
            lbl_state.config(text="Not Parked"); lbl_slot.config(text="—"); lbl_vehicle.config(text="—"); lbl_entry.config(text="—")

    def refresh_slot():
        slot = _member.get_assigned_slot(uid)
        if slot:
            lbl_slot_big.config(text=str(slot["code"])); lbl_tile_entry.config(text=str(slot["entry_time"]))
            rows = _member.list_vehicles(uid); lbl_tile_vehicle.config(text=rows[0]["plate_number"] if rows else "—")
            lbl_tile_duration.config(text="—")
        else:
            lbl_slot_big.config(text="No active assignment"); lbl_tile_entry.config(text="—"); lbl_tile_vehicle.config(text="—"); lbl_tile_duration.config(text="—")

    def refresh_profile():
        for w in vehicles_profile_list.winfo_children(): w.destroy()
        rows = _member.list_vehicles(uid)
        for i, v in enumerate(rows): pill_row(vehicles_profile_list, v["plate_number"], row=i)

    def set_active(view: str):
        nav_state["active"] = view
        for key, btn in nav_buttons.items(): btn.configure(style="NavSelected.TButton" if key == view else "Nav.TButton")
        for f in (view_dashboard, view_slot, view_profile): f.grid_remove()
        if view == "dashboard": refresh_dashboard(); view_dashboard.grid()
        elif view == "slot":    refresh_slot(); view_slot.grid()
        else:                   refresh_profile(); view_profile.grid()

    set_active("dashboard")
    return root
