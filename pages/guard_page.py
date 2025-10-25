import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from services.ocr_service import PlateOCR
from services.parking_service import ParkingService
from services.guard_service import GuardService


_ocr = PlateOCR()
_parking = ParkingService()
_guard = GuardService()


def card(parent, title: str = ""):
    """Create a card container"""
    frame = ttk.Labelframe(parent, text=title, style="Glass.TLabelframe")
    return frame


def _kpi_chip(parent, label_text: str, value_text: str):
    frame = ttk.Labelframe(parent, text=label_text, style="Glass.TLabelframe")
    ttk.Label(frame, text=value_text).grid(row=0, column=0, padx=8, pady=8)
    return frame


def _build_dashboard(tab, current_user: dict | None, refresh_callback=None):
    # KPI row
    kpi_row = ttk.Frame(tab)
    kpi_row.grid(row=0, column=0, pady=(0, 12))  # Align with top of content area
    
    # Quick actions
    actions = ttk.Frame(tab)
    actions.grid(row=1, column=0, pady=(12, 6), sticky="w")  # 12px gap from KPIs
    
    def _update_button_states(actions_frame, is_verified):
        """Update button states based on verification status"""
        for widget in actions_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                if not is_verified:
                    widget.config(state="disabled")
                else:
                    widget.config(state="normal")
    
    def _refresh_dashboard():
        # Clear existing KPIs
        for widget in kpi_row.winfo_children():
            widget.destroy()
        
        # Get fresh user data from database
        uid = (current_user or {}).get('id') or 0
        fresh_user_data = _guard.get_complete_profile_data(uid)
        is_verified = fresh_user_data.get('is_profile_verified', False)
        verification_status = "Verified" if is_verified else "Not Verified"
        
    # Live KPI values from DB
    kpis = [
        ("Vehicles Inside", str(_parking.count_active_inside())),
        ("Free Slots", str(_parking.count_free_slots())),
        ("Today Entries", str(_parking.count_today_entries())),
        ("Open Flags", str(_parking.count_open_flags())),
            ("Verification Status", verification_status),
    ]
    for idx, (lbl, val) in enumerate(kpis):
        c = _kpi_chip(kpi_row, lbl, val)
        c.grid(row=0, column=idx, padx=6)

        # Update button states
        _update_button_states(actions, is_verified)
        
        # Update current_user if callback provided
        if refresh_callback:
            refresh_callback(fresh_user_data)
    
    # Initial load
    _refresh_dashboard()
    
    # Create buttons with verification check
    def _open_vehicle_identification():
        # Switch to Vehicle Identification tab
        if hasattr(tab.master, 'select'):
            # Find the Vehicle Identification tab index
            for i in range(tab.master.index('end')):
                if tab.master.tab(i, 'text') == 'Vehicle Identification':
                    tab.master.select(i)
                    break
    
    scan_btn = ttk.Button(actions, text="Scan Vehicle", style="Role.TButton", command=_open_vehicle_identification)
    scan_btn.grid(row=0, column=0, padx=6)
    
    def _open_parking_slots():
        # Switch to Parking Slots tab
        if hasattr(tab.master, 'select'):
            # Find the Parking Slots tab index
            for i in range(tab.master.index('end')):
                if tab.master.tab(i, 'text') == 'Parking Slots':
                    tab.master.select(i)
                    break
    
    map_btn = ttk.Button(actions, text="Parking Map", style="Role.TButton", command=_open_parking_slots)
    map_btn.grid(row=0, column=1, padx=6)
    def _process_exit():
        # Get fresh verification status
        uid = (current_user or {}).get('id') or 0
        fresh_user_data = _guard.get_complete_profile_data(uid)
        is_verified = fresh_user_data.get('is_profile_verified', False)
        
        if not is_verified:
            messagebox.showwarning("Access Denied", "Profile must be verified to process exits.")
            return
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
    
    exit_btn = ttk.Button(actions, text="Process Exit", style="Role.TButton", command=_process_exit)
    exit_btn.grid(row=0, column=2, padx=6)
    
    flags_btn = ttk.Button(actions, text="Flags", style="Role.TButton")
    flags_btn.grid(row=0, column=3, padx=6)
    
    # Store refresh function for external access
    tab._refresh_dashboard = _refresh_dashboard

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
    zone_combo = ttk.Combobox(controls, values=["All"], width=12, state="readonly")
    zone_combo.grid(row=0, column=1, padx=(0, 12))
    zone_combo.set("All")
    
    ttk.Label(controls, text="Level:").grid(row=0, column=2, padx=(0, 6))
    level_combo = ttk.Combobox(controls, values=["All"], width=12, state="readonly")
    level_combo.grid(row=0, column=3)
    level_combo.set("All")

    # Slots display area
    grid = ttk.Labelframe(tab, text="Slots", style="Glass.TLabelframe")
    grid.grid(row=1, column=0, sticky="ew", pady=(12, 0))  # 12px gap from controls
    grid.grid_columnconfigure(0, weight=1)
    
    # Legend
    legend_frame = ttk.Frame(grid)
    legend_frame.grid(row=0, column=0, padx=8, pady=8, sticky="w")
    ttk.Label(legend_frame, text="Green = available, Red = occupied, Yellow = reserved").grid(row=0, column=0)
    
    # Slots grid container
    slots_container = ttk.Frame(grid)
    slots_container.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="ew")
    slots_container.grid_columnconfigure(0, weight=1)
    
    # Configure equal column weights for 6 columns
    for col in range(6):
        slots_container.grid_columnconfigure(col, weight=1, uniform="slot_col")
    
    def _load_slots():
        """Load and display slots from database"""
        # Clear existing slots
        for widget in slots_container.winfo_children():
            widget.destroy()
        
        # Get slots from database
        cur = _parking.conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM slots ORDER BY code")
            slots = cur.fetchall()
            
            if not slots:
                ttk.Label(slots_container, text="No slots found in database").grid(row=0, column=0, pady=20)
                return
            
            # Create slots grid (6 columns)
            cols = 6
            for i, slot in enumerate(slots):
                row = i // cols
                col = i % cols
                
                # Determine color based on status
                if slot['status'] == 'available':
                    bg_color = '#90EE90'  # Light green
                elif slot['status'] == 'occupied':
                    bg_color = '#FFB6C1'  # Light red
                elif slot['status'] == 'reserved':
                    bg_color = '#FFFF99'  # Light yellow
                else:
                    bg_color = '#F0F0F0'  # Light gray
                
                # Create slot button with consistent sizing
                slot_frame = tk.Frame(slots_container, bg=bg_color, relief="raised", bd=1, width=120, height=80)
                slot_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                slot_frame.grid_propagate(False)  # Prevent frame from shrinking
                
                # Configure slot frame grid
                slot_frame.grid_rowconfigure(0, weight=1)
                slot_frame.grid_rowconfigure(1, weight=1)
                slot_frame.grid_rowconfigure(2, weight=1)
                slot_frame.grid_columnconfigure(0, weight=1)
                
                # Slot code
                ttk.Label(slot_frame, text=slot['code'], font=("Arial", 10, "bold"), 
                         background=bg_color).grid(row=0, column=0, padx=4, pady=2, sticky="")
                
                # Slot status
                ttk.Label(slot_frame, text=slot['status'], font=("Arial", 8), 
                         background=bg_color).grid(row=1, column=0, padx=4, pady=1, sticky="")
                
                # Zone info
                ttk.Label(slot_frame, text=slot['zone'], font=("Arial", 7), 
                         background=bg_color).grid(row=2, column=0, padx=4, pady=1, sticky="")
        
        except Exception as e:
            ttk.Label(slots_container, text=f"Error loading slots: {str(e)}").grid(row=0, column=0, pady=20)
        finally:
            cur.close()
    
    # Load slots initially
    _load_slots()
    
    # Update zone and level comboboxes with actual data
    def _update_filters():
        cur = _parking.conn.cursor()
        try:
            # Get unique zones
            cur.execute("SELECT DISTINCT zone FROM slots ORDER BY zone")
            zones = ["All"] + [row[0] for row in cur.fetchall()]
            zone_combo['values'] = zones
            
            # Get unique levels
            cur.execute("SELECT DISTINCT level FROM slots ORDER BY level")
            levels = ["All"] + [row[0] for row in cur.fetchall()]
            level_combo['values'] = levels
            
        except Exception as e:
            print(f"Error updating filters: {e}")
        finally:
            cur.close()
    
    _update_filters()


def _build_profile(tab, current_user: dict | None, refresh_callback=None):
    uid = (current_user or {}).get('id') or 0
    
    def _refresh_profile():
        # Clear existing content
        for widget in tab.winfo_children():
            widget.destroy()
        
        # Get fresh profile data from database
        profile_data = _guard.get_complete_profile_data(uid)
        can_edit = profile_data.get('can_edit', True)
        verification_status = profile_data.get('status', 'pending')
        
        # Rebuild profile content
        _build_profile_content(tab, profile_data, uid, refresh_callback)
    
    # Initial load
    _refresh_profile()
    
    # Store refresh function for external access
    tab._refresh_profile = _refresh_profile

def _build_profile_content(tab, profile_data, uid, refresh_callback=None):
    can_edit = profile_data.get('can_edit', True)
    verification_status = profile_data.get('status', 'pending')
    
    # Profile view with enhanced verification features
    title_profile = ttk.Label(tab, text="Profile")
    title_profile.configure(font=("Segoe UI Semibold", 16))
    title_profile.grid(row=0, column=0, sticky="w", pady=(0, 8))  # Align with Dashboard button height
    
    # Status message based on verification status
    if verification_status == 'pending':
        status_text = "Profile under verification - editing disabled"
        status_color = "orange"
    elif verification_status == 'approved':
        status_text = "Profile verified - you can edit your information"
        status_color = "green"
    elif verification_status == 'rejected':
        status_text = "Profile rejected - you can update and resubmit"
        status_color = "red"
    else:
        status_text = "Complete your profile for verification"
        status_color = "black"
    
    status_label = ttk.Label(tab, text=status_text, foreground=status_color)
    status_label.grid(row=1, column=0, sticky="w", pady=(12, 16))  # 12px gap
    
    # Main profile form
    profile_form = card(tab, title="Profile Information")
    profile_form.grid(row=2, column=0, sticky="ew", pady=(0, 16))
    
    # Form fields
    form_fields = ttk.Frame(profile_form)
    form_fields.grid(row=0, column=0, padx=16, pady=16, sticky="ew")
    
    # Variables - fetch from database
    full_name_var = tk.StringVar(value=profile_data.get('full_name', ''))
    college_id_var = tk.StringVar(value=profile_data.get('college_id', ''))
    email_var = tk.StringVar(value=profile_data.get('email', ''))
    profile_image_path = tk.StringVar()
    college_id_image_path = tk.StringVar()
    
    # Full Name
    ttk.Label(form_fields, text="Full Name").grid(row=0, column=0, sticky="w", pady=4)
    full_name_entry = ttk.Entry(form_fields, textvariable=full_name_var, width=30)
    full_name_entry.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="w")
    if not can_edit:
        full_name_entry.config(state="disabled")
    
    # College ID
    ttk.Label(form_fields, text="College ID").grid(row=1, column=0, sticky="w", pady=4)
    college_id_entry = ttk.Entry(form_fields, textvariable=college_id_var, width=30)
    college_id_entry.grid(row=1, column=1, padx=(8, 0), pady=4, sticky="w")
    if not can_edit:
        college_id_entry.config(state="disabled")
    
    # Email
    ttk.Label(form_fields, text="Email").grid(row=2, column=0, sticky="w", pady=4)
    email_entry = ttk.Entry(form_fields, textvariable=email_var, width=30)
    email_entry.grid(row=2, column=1, padx=(8, 0), pady=4, sticky="w")
    if not can_edit:
        email_entry.config(state="disabled")
    
    # Image upload section
    images_section = card(profile_form, title="Verification Images")
    images_section.grid(row=1, column=0, sticky="ew", pady=(0, 16))
    
    images_container = ttk.Frame(images_section)
    images_container.grid(row=0, column=0, padx=16, pady=16, sticky="ew")
    
    # Profile Image Upload
    profile_section = ttk.Frame(images_container)
    profile_section.grid(row=0, column=0, padx=(0, 16), pady=8, sticky="w")
    ttk.Label(profile_section, text="Profile Image").grid(row=0, column=0, sticky="w", pady=(0, 4))
    
    profile_preview_frame = ttk.Frame(profile_section)
    profile_preview_frame.grid(row=1, column=0, pady=4)
    profile_image_label = ttk.Label(profile_preview_frame, text="No image", width=15, relief="sunken")
    profile_image_label.grid(row=0, column=0, padx=(0, 8))
    
    def _upload_profile_image():
        path = filedialog.askopenfilename(
            title="Select Profile Image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")]
        )
        if path:
            try:
                _guard.upload_profile_image(uid, path)
                profile_image_path.set(path)
                # Update preview
                from PIL import Image, ImageTk
                img = Image.open(path)
                img = img.resize((100, 100), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                profile_image_label.configure(image=photo, text="")
                profile_image_label.image = photo  # Keep reference
                messagebox.showinfo("Success", "Profile image uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload image: {str(e)}")
    
    profile_upload_btn = ttk.Button(profile_section, text="Upload Profile Image", command=_upload_profile_image)
    profile_upload_btn.grid(row=2, column=0, pady=4)
    if not can_edit:
        profile_upload_btn.config(state="disabled")
    
    # College ID Image Upload
    college_section = ttk.Frame(images_container)
    college_section.grid(row=0, column=1, padx=(16, 0), pady=8, sticky="w")
    ttk.Label(college_section, text="College ID Image").grid(row=0, column=0, sticky="w", pady=(0, 4))
    
    college_preview_frame = ttk.Frame(college_section)
    college_preview_frame.grid(row=1, column=0, pady=4)
    college_id_image_label = ttk.Label(college_preview_frame, text="No image", width=15, relief="sunken")
    college_id_image_label.grid(row=0, column=0, padx=(0, 8))
    
    def _upload_college_id_image():
        path = filedialog.askopenfilename(
            title="Select College ID Image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")]
        )
        if path:
            try:
                _guard.upload_college_id_image(uid, path)
                college_id_image_path.set(path)
                # Update preview
                from PIL import Image, ImageTk
                img = Image.open(path)
                img = img.resize((100, 100), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                college_id_image_label.configure(image=photo, text="")
                college_id_image_label.image = photo  # Keep reference
                messagebox.showinfo("Success", "College ID image uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload image: {str(e)}")
    
    college_upload_btn = ttk.Button(college_section, text="Upload College ID", command=_upload_college_id_image)
    college_upload_btn.grid(row=2, column=0, pady=4)
    if not can_edit:
        college_upload_btn.config(state="disabled")
    
    # Action buttons
    buttons_frame = ttk.Frame(profile_form)
    buttons_frame.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="w")
    
    def _save_profile():
        try:
            _guard.update_profile_data(
                uid, 
                full_name_var.get().strip(), 
                college_id_var.get().strip(), 
                email_var.get().strip()
            )
            messagebox.showinfo("Success", "Profile updated successfully!")
            # Enable verification button
            verify_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")
    
    def _submit_for_verification():
        try:
            _guard.submit_for_verification(uid)
            messagebox.showinfo("Success", "Profile submitted for verification!")
            verify_btn.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit for verification: {str(e)}")
    
    save_btn = ttk.Button(buttons_frame, text="Save Profile", command=_save_profile)
    save_btn.grid(row=0, column=0, padx=(0, 8))
    if not can_edit:
        save_btn.config(state="disabled")
    
    # Verification button logic
    if verification_status == 'pending':
        verify_btn_text = "Under Review"
        verify_btn_state = "disabled"
    elif verification_status == 'approved':
        verify_btn_text = "Verified"
        verify_btn_state = "disabled"
    elif verification_status == 'rejected':
        verify_btn_text = "Resubmit for Verification"
        verify_btn_state = "normal"
    else:
        verify_btn_text = "Send for Verification"
        verify_btn_state = "normal"
    
    verify_btn = ttk.Button(buttons_frame, text=verify_btn_text, command=_submit_for_verification, state=verify_btn_state)
    verify_btn.grid(row=0, column=1)
    
    # Load existing images from database
    def _refresh_profile():
        try:
            # Use the profile data we already fetched
            if profile_data.get('profile_image_url'):
                from PIL import Image, ImageTk
                img = Image.open(profile_data['profile_image_url'])
                img = img.resize((100, 100), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                profile_image_label.configure(image=photo, text="")
                profile_image_label.image = photo
            if profile_data.get('id_image_url'):
                from PIL import Image, ImageTk
                img = Image.open(profile_data['id_image_url'])
                img = img.resize((100, 100), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                college_id_image_label.configure(image=photo, text="")
                college_id_image_label.image = photo
        except Exception:
            pass  # Ignore errors when loading images
    
    _refresh_profile()


def render(parent, on_logout, current_user=None):
    # Clear existing content
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
    name = (current_user or {}).get('full_name', 'Guard')

    # Sidebar
    sidebar = ttk.Frame(wrapper, width=180)  # Set width directly in constructor
    sidebar.grid(row=0, column=0, sticky="nsw", padx=(16, 0), pady=16)
    sidebar.grid_propagate(False)  # Prevent grid from overriding width

    # Topbar in sidebar
    ttk.Label(sidebar, text="Security Guard", font=("Segoe UI Semibold", 13)).grid(row=0, column=0, sticky="ew", pady=(0, 16))

    # Content area
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
    page.grid(row=0, column=0, sticky="nsew", padx=24, pady=(8, 24))  # 8px gap from top
    page.grid_columnconfigure(0, weight=1)
    page.grid_rowconfigure(0, weight=1)

    # Helper: card
    def card(parent, title: str | None = None):
        frame = ttk.Labelframe(parent, text=title or "", style="Glass.TLabelframe") if title else ttk.Frame(parent)
        return frame

    # Views
    view_dashboard = tk.Frame(page, bg="#ffffff")
    view_identification = tk.Frame(page, bg="#ffffff")
    view_slots = tk.Frame(page, bg="#ffffff")
    view_profile = tk.Frame(page, bg="#ffffff")
    for v in (view_dashboard, view_identification, view_slots, view_profile):
        v.grid(row=0, column=0, sticky="nsew")
        v.grid_columnconfigure(0, weight=1)
        v.grid_rowconfigure(0, weight=0)  # Don't expand vertically to push content to top
        v.grid_remove()

    # Sidebar buttons
    def set_active(view: str):
        for f in (view_dashboard, view_identification, view_slots, view_profile):
            f.grid_remove()
        if view == "dashboard":
            refresh_dashboard()
            view_dashboard.grid()
        elif view == "identification":
            refresh_identification()
            view_identification.grid()
        elif view == "slots":
            refresh_slots()
            view_slots.grid()
        else:
            refresh_profile()
            view_profile.grid()

    # Check verification status for button states
    is_verified = (current_user or {}).get('is_profile_verified', False)
    
    # Sidebar navigation buttons
    ttk.Button(sidebar, text="Dashboard", command=lambda: set_active("dashboard")).grid(row=1, column=0, sticky="ew", pady=4)
    
    ident_btn = ttk.Button(sidebar, text="Vehicle Identification", command=lambda: set_active("identification"))
    ident_btn.grid(row=2, column=0, sticky="ew", pady=4)
    if not is_verified:
        ident_btn.config(state="disabled")
    
    slots_btn = ttk.Button(sidebar, text="Parking Slots", command=lambda: set_active("slots"))
    slots_btn.grid(row=3, column=0, sticky="ew", pady=4)
    if not is_verified:
        slots_btn.config(state="disabled")
    
    ttk.Button(sidebar, text="Profile", command=lambda: set_active("profile")).grid(row=4, column=0, sticky="ew", pady=4)
    ttk.Button(sidebar, text="Logout", command=on_logout).grid(row=10, column=0, sticky="ew", pady=(24, 0))

    # Dashboard view
    def refresh_dashboard():
        # Clear existing content
        for widget in view_dashboard.winfo_children():
            widget.destroy()
        
        # Get fresh user data
        fresh_user_data = _guard.get_complete_profile_data(uid)
        is_verified = fresh_user_data.get('is_profile_verified', False)
        verification_status = "Verified" if is_verified else "Not Verified"
        
        # Welcome message
        heading = ttk.Label(view_dashboard, text=f"Welcome, {name}")
        heading.configure(font=("Segoe UI Semibold", 16))
        heading.grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Label(view_dashboard, text="Manage parking operations and vehicle access").grid(row=1, column=0, sticky="w", pady=(12, 16))
        
        # KPIs
        kpis = ttk.Frame(view_dashboard)
        kpis.grid(row=2, column=0, sticky="w")
        
        kpi_vehicles = card(kpis)
        kpi_vehicles.grid(row=0, column=0, padx=(0, 16), pady=(0, 16))
        ttk.Label(kpi_vehicles, text="Vehicles Inside").grid(row=0, column=0, padx=8, pady=4)
        ttk.Label(kpi_vehicles, text=str(_parking.count_active_inside())).grid(row=1, column=0, padx=8, pady=4)
        
        kpi_slots = card(kpis)
        kpi_slots.grid(row=0, column=1, padx=(0, 16), pady=(0, 16))
        ttk.Label(kpi_slots, text="Free Slots").grid(row=0, column=0, padx=8, pady=4)
        ttk.Label(kpi_slots, text=str(_parking.count_free_slots())).grid(row=1, column=0, padx=8, pady=4)
        
        kpi_entries = card(kpis)
        kpi_entries.grid(row=0, column=2, padx=(0, 16), pady=(0, 16))
        ttk.Label(kpi_entries, text="Today Entries").grid(row=0, column=0, padx=8, pady=4)
        ttk.Label(kpi_entries, text=str(_parking.count_today_entries())).grid(row=1, column=0, padx=8, pady=4)
        
        kpi_flags = card(kpis)
        kpi_flags.grid(row=0, column=3, padx=(0, 16), pady=(0, 16))
        ttk.Label(kpi_flags, text="Open Flags").grid(row=0, column=0, padx=8, pady=4)
        ttk.Label(kpi_flags, text=str(_parking.count_open_flags())).grid(row=1, column=0, padx=8, pady=4)
        
        kpi_verification = card(kpis)
        kpi_verification.grid(row=0, column=4, padx=(0, 16), pady=(0, 16))
        ttk.Label(kpi_verification, text="Verification Status").grid(row=0, column=0, padx=8, pady=4)
        ttk.Label(kpi_verification, text=verification_status).grid(row=1, column=0, padx=8, pady=4)
        
        # Quick actions (only non-duplicate functions)
        actions = ttk.Frame(view_dashboard)
        actions.grid(row=3, column=0, sticky="w", pady=(16, 0))
        
        def _process_exit():
            if not is_verified:
                messagebox.showwarning("Access Denied", "Profile must be verified to process exits.")
                return
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
        
        exit_btn = ttk.Button(actions, text="Process Exit", command=_process_exit)
        exit_btn.grid(row=0, column=0, padx=(0, 8))
        if not is_verified:
            exit_btn.config(state="disabled")
        
        flags_btn = ttk.Button(actions, text="Flags")
        flags_btn.grid(row=0, column=1)
        if not is_verified:
            flags_btn.config(state="disabled")
        
        # Active Parking Events Table
        table_frame = ttk.Frame(view_dashboard)
        table_frame.grid(row=4, column=0, sticky="ew", pady=(16, 0))
        table_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(table_frame, text="Active Parking Events", font=("Segoe UI Semibold", 14)).grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # Create Treeview for parking events
        columns = ("Parking ID", "Vehicle Number", "User", "Slot Allocated", "Entry Time", "Exit Time", "Duration")
        parking_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        
        # Configure column widths
        parking_tree.column("Parking ID", width=80)
        parking_tree.column("Vehicle Number", width=120)
        parking_tree.column("User", width=150)
        parking_tree.column("Slot Allocated", width=100)
        parking_tree.column("Entry Time", width=150)
        parking_tree.column("Exit Time", width=150)
        parking_tree.column("Duration", width=100)
        
        # Configure headings
        for col in columns:
            parking_tree.heading(col, text=col)
        
        parking_tree.grid(row=1, column=0, sticky="ew")
        
        def _update_parking_table():
            """Update the parking events table with fresh data"""
            # Clear existing items
            for item in parking_tree.get_children():
                parking_tree.delete(item)
            
            # Get fresh data
            events = _parking.list_active_parking_events()
            
            for event in events:
                # Calculate duration
                entry_time = event['entry_time']
                exit_time = event['exit_time']
                
                if exit_time:
                    # Vehicle has exited
                    duration = str(exit_time - entry_time).split('.')[0]  # Remove microseconds
                else:
                    # Vehicle is still parked - calculate current duration
                    from datetime import datetime
                    current_time = datetime.now()
                    duration = str(current_time - entry_time).split('.')[0]
                
                # Format times
                entry_str = entry_time.strftime("%H:%M:%S") if entry_time else ""
                exit_str = exit_time.strftime("%H:%M:%S") if exit_time else ""
                
                parking_tree.insert("", "end", values=(
                    event['parking_id'],
                    event['plate_number'],
                    event['user_name'],
                    event['slot_code'],
                    entry_str,
                    exit_str,
                    duration
                ))
        
        # Initial load
        _update_parking_table()
        
        # Schedule periodic updates for duration (every 5 seconds)
        def _schedule_duration_update():
            _update_parking_table()
            view_dashboard.after(5000, _schedule_duration_update)  # Update every 5 seconds
        
        _schedule_duration_update()
        
        ttk.Label(view_dashboard, text="Use sidebar navigation to access Vehicle Identification and Parking Slots.").grid(row=5, column=0, pady=(8, 0), sticky="w")

    def refresh_identification():
        # Clear existing content
        for widget in view_identification.winfo_children():
            widget.destroy()
        _build_identification(view_identification, guard_user_id=int(uid))

    def refresh_slots():
        # Clear existing content
        for widget in view_slots.winfo_children():
            widget.destroy()
        _build_slots(view_slots)

    def refresh_profile():
        # Clear existing content
        for widget in view_profile.winfo_children():
            widget.destroy()
        _build_profile_content(view_profile, _guard.get_complete_profile_data(uid), uid)

    # Initial load
    set_active("dashboard")

    return wrapper


