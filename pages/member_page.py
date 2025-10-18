import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from services.member_service import MemberService


_member = MemberService()


def render(parent, on_logout, current_user=None):
    for w in parent.winfo_children():
        try:
            w.destroy()
        except Exception:
            pass
    parent.update_idletasks()

    wrapper = ttk.Frame(parent)
    wrapper.grid(row=0, column=0, sticky="nsew")
    wrapper.grid_columnconfigure(0, weight=0)  # Sidebar fixed width
    wrapper.grid_columnconfigure(2, weight=1)  # Content area expands
    wrapper.grid_rowconfigure(0, weight=1)

    uid = (current_user or {}).get('id') or 0
    name = (current_user or {}).get('full_name', 'Student')

    # Sidebar
    sidebar = ttk.Frame(wrapper, width=180)  # Set width directly in constructor
    sidebar.grid(row=0, column=0, sticky="nsw", padx=(16, 0), pady=16)
    sidebar.grid_propagate(False)  # Prevent grid from overriding width

    ttk.Label(sidebar, text="Campus Parking").grid(row=0, column=0, sticky="w", pady=(0, 16))
    nav_state = {"active": "dashboard"}

    # Vertical divider between sidebar and page
    divider = ttk.Separator(wrapper, orient='vertical')
    divider.grid(row=0, column=1, sticky='ns', padx=24, pady=16)

    # Main content wrapper
    content = ttk.Frame(wrapper)
    content.grid(row=0, column=2, sticky="nsew", padx=(0, 0), pady=0)
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(0, weight=1)

    # White page background to match screenshot
    page_bg = tk.Frame(content, bg="#ffffff")
    page_bg.grid(row=0, column=0, sticky="nsew")
    page_bg.grid_columnconfigure(0, weight=1)
    page_bg.grid_rowconfigure(0, weight=1)
    # Inner page with gutters
    page = tk.Frame(page_bg, bg="#ffffff")
    page.grid(row=0, column=0, sticky="nsew", padx=24, pady=(0, 24))  # Remove top padding
    page.grid_columnconfigure(0, weight=1)
    page.grid_rowconfigure(0, weight=1)

    # Helper: card
    def card(parent, title: str | None = None):
        frame = ttk.Labelframe(parent, text=title or "", style="Glass.TLabelframe") if title else ttk.Frame(parent)
        return frame

    # Views
    view_dashboard = tk.Frame(page, bg="#ffffff")
    view_slot = tk.Frame(page, bg="#ffffff")
    view_profile = tk.Frame(page, bg="#ffffff")
    for v in (view_dashboard, view_slot, view_profile):
        v.grid(row=0, column=0, sticky="nsew")
        v.grid_columnconfigure(0, weight=1)
        v.grid_rowconfigure(0, weight=0)  # Don't expand vertically to push content to top
        v.grid_remove()

    # Sidebar buttons
    def set_active(view: str):
        nav_state["active"] = view
        for f in (view_dashboard, view_slot, view_profile):
            f.grid_remove()
        if view == "dashboard":
            refresh_dashboard()
            view_dashboard.grid()
        elif view == "slot":
            refresh_slot()
            view_slot.grid()
        else:
            refresh_profile()
            view_profile.grid()

    ttk.Button(sidebar, text="Dashboard", command=lambda: set_active("dashboard")).grid(row=1, column=0, sticky="ew", pady=4)
    ttk.Button(sidebar, text="My Slot", command=lambda: set_active("slot")).grid(row=2, column=0, sticky="ew", pady=4)
    ttk.Button(sidebar, text="Profile", command=lambda: set_active("profile")).grid(row=3, column=0, sticky="ew", pady=4)
    ttk.Button(sidebar, text="Logout", command=on_logout).grid(row=10, column=0, sticky="ew", pady=(24, 0))

    # Dashboard view
    heading = ttk.Label(view_dashboard, text=f"Welcome, {name}")
    heading.configure(font=("Segoe UI Semibold", 16))
    heading.grid(row=0, column=0, sticky="w", pady=(0, 8))
    ttk.Label(view_dashboard, text="Manage your parking and profile").grid(row=1, column=0, sticky="w", pady=(12, 16))  # 12px gap

    kpis = ttk.Frame(view_dashboard)
    kpis.grid(row=2, column=0, sticky="w")
    kpi_reg = card(kpis)
    kpi_reg.grid(row=0, column=0, padx=(0, 16), pady=(0, 16))
    ttk.Label(kpi_reg, text="Registered Vehicles").grid(row=0, column=0, padx=16, pady=(12, 0), sticky="w")
    lbl_reg_count = ttk.Label(kpi_reg, text="–")
    lbl_reg_count.configure(font=("Segoe UI Semibold", 14))
    lbl_reg_count.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

    kpi_ver = card(kpis)
    kpi_ver.grid(row=0, column=1, padx=(0, 16), pady=(0, 16))
    ttk.Label(kpi_ver, text="Verification Status").grid(row=0, column=0, padx=16, pady=(12, 0), sticky="w")
    lbl_ver = ttk.Label(kpi_ver, text="–")
    lbl_ver.configure(font=("Segoe UI Semibold", 14))
    lbl_ver.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

    kpi_state = card(kpis)
    kpi_state.grid(row=0, column=2, padx=(0, 16), pady=(0, 16))
    ttk.Label(kpi_state, text="Current Status").grid(row=0, column=0, padx=16, pady=(12, 0), sticky="w")
    lbl_state = ttk.Label(kpi_state, text="–")
    lbl_state.configure(font=("Segoe UI Semibold", 14))
    lbl_state.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

    current_parking = card(view_dashboard, title="Current Parking")
    current_parking.grid(row=3, column=0, sticky="ew", pady=(0, 20))
    ttk.Label(current_parking, text="Slot Number").grid(row=0, column=0, padx=16, pady=(12, 0), sticky="w")
    lbl_slot = ttk.Label(current_parking, text="–")
    lbl_slot.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")
    ttk.Label(current_parking, text="Vehicle").grid(row=0, column=1, padx=32, pady=(12, 0), sticky="w")
    lbl_vehicle = ttk.Label(current_parking, text="–")
    lbl_vehicle.grid(row=1, column=1, padx=32, pady=(0, 12), sticky="w")
    ttk.Label(current_parking, text="Entry Time").grid(row=2, column=0, padx=16, pady=(0, 0), sticky="w")
    lbl_entry = ttk.Label(current_parking, text="–")
    lbl_entry.grid(row=3, column=0, padx=16, pady=(0, 12), sticky="w")

    vehicles_card = card(view_dashboard, title="Your Vehicles")
    vehicles_card.grid(row=4, column=0, sticky="ew", pady=(0, 12))
    vehicles_list_container = ttk.Frame(vehicles_card)
    vehicles_list_container.grid(row=0, column=0, padx=12, pady=12, sticky="ew")

    # My Slot view
    title_slot = ttk.Label(view_slot, text="My Parking Slot")
    title_slot.configure(font=("Segoe UI Semibold", 16))
    title_slot.grid(row=0, column=0, sticky="w", pady=(0, 8))  # Align with Dashboard button height
    ttk.Label(view_slot, text="Your current parking information").grid(row=1, column=0, sticky="w", pady=(12, 16))  # 12px gap

    slot_card = card(view_slot)
    slot_card.grid(row=2, column=0, sticky="ew", pady=(0, 20))
    lbl_slot_big = ttk.Label(slot_card, text="–")
    lbl_slot_big.configure(font=("Segoe UI Semibold", 28))
    lbl_slot_big.grid(row=0, column=0, columnspan=3, padx=16, pady=(16, 6))
    ttk.Label(slot_card, text="Your assigned slot").grid(row=1, column=0, columnspan=3, padx=16, pady=(0, 16))
    # three tiles
    tile_vehicle = card(slot_card)
    tile_vehicle.grid(row=2, column=0, padx=12, pady=12)
    ttk.Label(tile_vehicle, text="Vehicle Number").grid(row=0, column=0, padx=12, pady=(12, 0))
    lbl_tile_vehicle = ttk.Label(tile_vehicle, text="–")
    lbl_tile_vehicle.grid(row=1, column=0, padx=12, pady=(0, 12))
    tile_entry = card(slot_card)
    tile_entry.grid(row=2, column=1, padx=12, pady=12)
    ttk.Label(tile_entry, text="Entry Time").grid(row=0, column=0, padx=12, pady=(12, 0))
    lbl_tile_entry = ttk.Label(tile_entry, text="–")
    lbl_tile_entry.grid(row=1, column=0, padx=12, pady=(0, 12))
    tile_duration = card(slot_card)
    tile_duration.grid(row=2, column=2, padx=12, pady=12)
    ttk.Label(tile_duration, text="Duration").grid(row=0, column=0, padx=12, pady=(12, 0))
    lbl_tile_duration = ttk.Label(tile_duration, text="–")
    lbl_tile_duration.grid(row=1, column=0, padx=12, pady=(0, 12))

    # Profile view with vehicles management
    title_profile = ttk.Label(view_profile, text="Profile")
    title_profile.configure(font=("Segoe UI Semibold", 16))
    title_profile.grid(row=0, column=0, sticky="w", pady=(0, 8))  # Align with Dashboard button height
    ttk.Label(view_profile, text="Your account information").grid(row=1, column=0, sticky="w", pady=(12, 16))  # 12px gap
    profile_card = card(view_profile)
    profile_card.grid(row=2, column=0, sticky="ew")
    ttk.Label(profile_card, text=name).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")
    email = (current_user or {}).get('email', '—')
    college_id = (current_user or {}).get('college_id', '—')
    ttk.Label(profile_card, text=f"Email\n{email}").grid(row=1, column=0, padx=16, pady=6, sticky="w")
    ttk.Label(profile_card, text=f"College ID\n{college_id}").grid(row=2, column=0, padx=16, pady=6, sticky="w")

    vehicles_profile = card(profile_card)
    vehicles_profile.grid(row=3, column=0, padx=12, pady=(12, 16), sticky="ew")
    ttk.Label(vehicles_profile, text="Registered Vehicles").grid(row=0, column=0, padx=12, pady=(12, 0), sticky="w")
    vehicles_profile_list = ttk.Frame(vehicles_profile)
    vehicles_profile_list.grid(row=1, column=0, padx=12, pady=8, sticky="w")
    add_row = ttk.Frame(vehicles_profile)
    add_row.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="w")
    new_plate = tk.StringVar(value="")
    ttk.Entry(add_row, textvariable=new_plate, width=20).grid(row=0, column=0, padx=(0, 8))
    def _add_vehicle_profile():
        if not new_plate.get():
            return
        try:
            _member.add_vehicle(uid, new_plate.get().strip())
            messagebox.showinfo("Vehicles", "Vehicle added.")
            refresh_dashboard()
            refresh_profile()
        except Exception as e:
            messagebox.showerror("Vehicles", str(e))
    ttk.Button(add_row, text="Add Vehicle", style="Role.TButton", command=_add_vehicle_profile).grid(row=0, column=1)

    # Refresh helpers
    def refresh_dashboard():
        rows = _member.list_vehicles(uid)
        lbl_reg_count.config(text=str(len(rows)))
        for w in vehicles_list_container.winfo_children():
            w.destroy()
        for i, v in enumerate(rows):
            rowf = ttk.Frame(vehicles_list_container)
            rowf.grid(row=i, column=0, sticky="ew", pady=4)
            ttk.Label(rowf, text=v['plate_number']).grid(row=0, column=0, padx=8)
        v_status = _member.get_verification_status(uid)
        lbl_ver.config(text=v_status.capitalize())
        slot = _member.get_assigned_slot(uid)
        if slot:
            lbl_state.config(text="Parked")
            lbl_slot.config(text=slot['code'])
            lbl_vehicle.config(text=rows[0]['plate_number'] if rows else "–")
            lbl_entry.config(text=str(slot['entry_time']))
        else:
            lbl_state.config(text="Not Parked")
            lbl_slot.config(text="–")
            lbl_vehicle.config(text="–")
            lbl_entry.config(text="–")

    def refresh_slot():
        slot = _member.get_assigned_slot(uid)
        if slot:
            lbl_slot_big.config(text=str(slot['code']))
            lbl_tile_entry.config(text=str(slot['entry_time']))
            rows = _member.list_vehicles(uid)
            lbl_tile_vehicle.config(text=rows[0]['plate_number'] if rows else "–")
            lbl_tile_duration.config(text="—")
        else:
            lbl_slot_big.config(text="No active assignment")
            lbl_tile_entry.config(text="–")
            lbl_tile_vehicle.config(text="–")
            lbl_tile_duration.config(text="–")

    def refresh_profile():
        for w in vehicles_profile_list.winfo_children():
            w.destroy()
        rows = _member.list_vehicles(uid)
        for i, v in enumerate(rows):
            ttk.Label(vehicles_profile_list, text=v['plate_number']).grid(row=i, column=0, padx=8, pady=2, sticky="w")

    # Initial view
    set_active("dashboard")

    return wrapper


