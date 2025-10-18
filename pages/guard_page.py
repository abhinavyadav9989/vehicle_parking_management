import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from services.ocr_service import PlateOCR
from services.parking_service import ParkingService


_ocr = PlateOCR()
_parking = ParkingService()


def _kpi_chip(parent, label_text: str, value_text: str):
    frame = ttk.Labelframe(parent, text=label_text, style="Glass.TLabelframe")
    ttk.Label(frame, text=value_text).grid(row=0, column=0, padx=8, pady=8)
    return frame


def _build_dashboard(tab):
    # KPI row
    kpi_row = ttk.Frame(tab)
    kpi_row.grid(row=0, column=0, pady=(0, 12))  # Align with top of content area
    # Live KPI values from DB
    kpis = [
        ("Vehicles Inside", str(_parking.count_active_inside())),
        ("Free Slots", str(_parking.count_free_slots())),
        ("Today Entries", str(_parking.count_today_entries())),
        ("Open Flags", str(_parking.count_open_flags())),
    ]
    for idx, (lbl, val) in enumerate(kpis):
        c = _kpi_chip(kpi_row, lbl, val)
        c.grid(row=0, column=idx, padx=6)

    # Quick actions
    actions = ttk.Frame(tab)
    actions.grid(row=1, column=0, pady=(12, 6), sticky="w")  # 12px gap from KPIs
    ttk.Button(actions, text="Scan Vehicle", style="Role.TButton").grid(row=0, column=0, padx=6)
    ttk.Button(actions, text="Parking Map", style="Role.TButton").grid(row=0, column=1, padx=6)
    def _process_exit():
        plate = filedialog.askstring("Process Exit", "Enter plate number:")
        if not plate:
            return
        try:
            ok = _parking.process_exit(plate.strip().upper())
            if ok:
                messagebox.showinfo("Exit", "Vehicle exited and slot freed.")
            else:
                messagebox.showwarning("Exit", "No active parking event for this plate.")
        except Exception as e:
            messagebox.showerror("Exit", str(e))
    ttk.Button(actions, text="Process Exit", style="Role.TButton", command=_process_exit).grid(row=0, column=2, padx=6)
    ttk.Button(actions, text="Flags", style="Role.TButton").grid(row=0, column=3, padx=6)

    ttk.Label(tab, text="Use actions above to manage entries, slots, and exits.").grid(row=2, column=0, pady=(8, 0), sticky="w")


def _build_identification(tab, guard_user_id: int):
    plate_var = tk.StringVar(value="—")
    conf_var = tk.StringVar(value="—")
    status_var = tk.StringVar(value="")
    slots_values: list[tuple[int, str]] = []
    selected_slot = tk.StringVar(value="")
    current_vehicle = {"vehicle_id": None, "user_id": None}

    # Left: capture/upload
    left = ttk.Labelframe(tab, text="Capture / Upload", style="Glass.TLabelframe")
    left.grid(row=0, column=0, padx=(0, 8), pady=(0, 8), sticky="n")  # Align with top
    ttk.Button(left, text="Open Camera", style="Role.TButton", state="disabled").grid(row=0, column=0, padx=8, pady=8)
    def _upload_image():
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")])
        if not path:
            return
        plate, conf = _ocr.extract_plate(path)
        if not plate:
            messagebox.showwarning("OCR", "No text detected. Try again.")
            return
        plate_var.set(plate)
        conf_var.set(f"{conf:.2f}")
        # Lookup in DB
        record = _parking.find_vehicle(plate)
        if not record:
            status_var.set("Access Denied: Not found in database")
            return
        current_vehicle["vehicle_id"] = record["vehicle_id"]
        current_vehicle["user_id"] = record["user_id"]
        status_var.set(f"Member Found: {record['full_name']}")
        # Load slots
        slots = _parking.get_available_slots()
        nonlocal slots_values
        slots_values = [(s["id"], s["code"]) for s in slots]
        selected_slot.set(slots_values[0][1] if slots_values else "")
        combo_slot["values"] = [code for _, code in slots_values]

    ttk.Button(left, text="Upload Image", style="Role.TButton", command=_upload_image).grid(row=0, column=1, padx=8, pady=8)
    ttk.Button(left, text="Read Plate (OCR)", style="Role.TButton", state="disabled").grid(row=1, column=0, columnspan=2, padx=8, pady=8)

    # Right: result
    right = ttk.Labelframe(tab, text="Result", style="Glass.TLabelframe")
    right.grid(row=0, column=1, padx=(8, 0), pady=(0, 8), sticky="n")  # Align with top
    ttk.Label(right, textvariable=plate_var).grid(row=0, column=1, padx=8, pady=(8, 2), sticky="w")
    ttk.Label(right, text="Plate:").grid(row=0, column=0, padx=8, pady=(8, 2), sticky="w")
    ttk.Label(right, text="Confidence:").grid(row=1, column=0, padx=8, pady=(0, 8), sticky="w")
    ttk.Label(right, textvariable=conf_var).grid(row=1, column=1, padx=8, pady=(0, 8), sticky="w")

    # Actions after lookup
    actions = ttk.Labelframe(tab, text="Actions", style="Glass.TLabelframe")
    actions.grid(row=1, column=0, columnspan=2, sticky="w", pady=(12, 8))  # 12px gap from above
    ttk.Label(actions, textvariable=status_var).grid(row=0, column=0, padx=8, pady=8, columnspan=4, sticky="w")
    ttk.Label(actions, text="Available Slot:").grid(row=1, column=0, padx=8, pady=(0, 8), sticky="w")
    combo_slot = ttk.Combobox(actions, values=[], width=20, state="readonly", textvariable=selected_slot)
    combo_slot.grid(row=1, column=1, padx=8, pady=(0, 8))
    def _allocate():
        if not current_vehicle["vehicle_id"]:
            messagebox.showwarning("Allocate", "Identify a member vehicle first.")
            return
        if not slots_values:
            messagebox.showwarning("Allocate", "No available slots.")
            return
        # Find selected slot id
        try:
            slot_id = next(i for i, code in slots_values if code == selected_slot.get())
        except StopIteration:
            messagebox.showwarning("Allocate", "Select a slot.")
            return
        try:
            _parking.allocate(
                vehicle_id=current_vehicle["vehicle_id"],
                slot_id=slot_id,
                guard_user_id=guard_user_id,
                ocr_plate_text=plate_var.get() if plate_var.get() != "—" else None,
                ocr_conf=float(conf_var.get()) if conf_var.get() not in ("—", "") else None,
            )
            messagebox.showinfo("Allocated", f"Assigned slot {selected_slot.get()}.")
            status_var.set(f"Allocated to slot {selected_slot.get()}")
        except Exception as e:
            messagebox.showerror("Allocate", str(e))

    def _raise_flag():
        try:
            _parking.raise_flag(raised_by_guard_id=guard_user_id, reason="no_slots", vehicle_id=current_vehicle["vehicle_id"])  # type: ignore[arg-type]
            messagebox.showinfo("Flag", "Flag raised for admin review.")
        except Exception as e:
            messagebox.showerror("Flag", str(e))

    ttk.Button(actions, text="Allocate Slot", style="Role.TButton", command=_allocate).grid(row=1, column=2, padx=8, pady=(0, 8))
    ttk.Button(actions, text="Raise Flag", style="Role.TButton", command=_raise_flag).grid(row=1, column=3, padx=8, pady=(0, 8))


def _build_slots(tab):
    # Filters and grid placeholder
    controls = ttk.Frame(tab)
    controls.grid(row=0, column=0, pady=(0, 8), sticky="w")  # Align with top
    ttk.Label(controls, text="Zone:").grid(row=0, column=0, padx=(0, 6))
    ttk.Combobox(controls, values=["All"], width=12, state="readonly").grid(row=0, column=1, padx=(0, 12))
    ttk.Label(controls, text="Level:").grid(row=0, column=2, padx=(0, 6))
    ttk.Combobox(controls, values=["All"], width=12, state="readonly").grid(row=0, column=3)

    grid = ttk.Labelframe(tab, text="Slots", style="Glass.TLabelframe")
    grid.grid(row=1, column=0, sticky="w", pady=(12, 0))  # 12px gap from controls
    ttk.Label(grid, text="Green = available, Red = occupied, Yellow = reserved").grid(row=0, column=0, padx=8, pady=8)


def _build_profile(tab, current_user: dict | None):
    # Basic profile info
    info = ttk.Labelframe(tab, text="My Profile", style="Glass.TLabelframe")
    info.grid(row=0, column=0, sticky="w", pady=(0, 0))  # Align with top
    name = (current_user or {}).get('full_name', '—')
    email = (current_user or {}).get('email', '—')
    verified = "Approved" if (current_user or {}).get('is_profile_verified') else "Pending"
    ttk.Label(info, text=f"Full Name: {name}").grid(row=0, column=0, padx=8, pady=4, sticky="w")
    ttk.Label(info, text=f"Email: {email}").grid(row=1, column=0, padx=8, pady=4, sticky="w")
    ttk.Label(info, text=f"Verification: {verified}").grid(row=2, column=0, padx=8, pady=4, sticky="w")


def render(parent, on_logout, current_user=None):
    wrapper = ttk.Frame(parent)
    wrapper.grid(row=0, column=0, sticky="nsew")
    
    # Configure wrapper to expand
    wrapper.grid_rowconfigure(1, weight=1)  # Tabs row expands
    wrapper.grid_columnconfigure(0, weight=1)  # Main column expands

    # Topbar
    bar = ttk.Frame(wrapper)
    bar.grid(row=0, column=0, sticky="ew")
    bar.grid_columnconfigure(0, weight=1)
    title = ttk.Label(bar, text="Security Guard")
    title.configure(font=("Segoe UI Semibold", 13))
    title.grid(row=0, column=0, sticky="w")
    ttk.Button(bar, text="Logout", command=on_logout).grid(row=0, column=1, sticky="e")

    # Tabs container
    tabs_card = ttk.Frame(wrapper)
    tabs_card.grid(row=1, column=0, padx=24, pady=(4, 12), sticky="nsew")
    tabs_card.grid_rowconfigure(0, weight=1)
    tabs_card.grid_columnconfigure(0, weight=1)

    nb = ttk.Notebook(tabs_card)
    nb.grid(row=0, column=0, sticky="nsew")

    dash_tab = ttk.Frame(nb)
    ident_tab = ttk.Frame(nb)
    slots_tab = ttk.Frame(nb)
    profile_tab = ttk.Frame(nb)
    
    # Configure tabs to expand
    for tab in (dash_tab, ident_tab, slots_tab, profile_tab):
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

    nb.add(dash_tab, text="Dashboard")
    nb.add(ident_tab, text="Vehicle Identification")
    nb.add(slots_tab, text="Parking Slots")
    nb.add(profile_tab, text="Profile")

    _build_dashboard(dash_tab)
    guard_id = (current_user or {}).get('id') or 0
    _build_identification(ident_tab, guard_user_id=int(guard_id))
    _build_slots(slots_tab)
    _build_profile(profile_tab, current_user=current_user)

    # Gate tabs for unverified profiles
    if not (current_user or {}).get('is_profile_verified'):
        idx_ident = nb.index(ident_tab)
        idx_slots = nb.index(slots_tab)
        nb.tab(idx_ident, state='disabled')
        nb.tab(idx_slots, state='disabled')

    return wrapper


