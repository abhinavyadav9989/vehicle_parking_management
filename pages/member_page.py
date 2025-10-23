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
    page.grid(row=0, column=0, sticky="nsew", padx=24, pady=(8, 24))  # 8px gap from top
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

    # Profile view with enhanced verification features
    title_profile = ttk.Label(view_profile, text="Profile")
    title_profile.configure(font=("Segoe UI Semibold", 16))
    title_profile.grid(row=0, column=0, sticky="w", pady=(0, 8))  # Align with Dashboard button height
    ttk.Label(view_profile, text="Complete your profile for verification").grid(row=1, column=0, sticky="w", pady=(12, 16))  # 12px gap
    
    # Main profile form
    profile_form = card(view_profile, title="Profile Information")
    profile_form.grid(row=2, column=0, sticky="ew", pady=(0, 16))
    
    # Form variables
    full_name_var = tk.StringVar()
    college_id_var = tk.StringVar()
    email_var = tk.StringVar()
    profile_image_path = tk.StringVar()
    college_id_image_path = tk.StringVar()
    
    # Load existing data
    profile_data = _member.get_profile_data(uid)
    full_name_var.set(profile_data.get('full_name', ''))
    college_id_var.set(profile_data.get('college_id', ''))
    email_var.set(profile_data.get('email', ''))
    
    # Image preview variables
    profile_image_label = None
    college_id_image_label = None
    
    # Form fields
    form_fields = ttk.Frame(profile_form)
    form_fields.grid(row=0, column=0, padx=16, pady=16, sticky="ew")
    
    # Full Name
    ttk.Label(form_fields, text="Full Name").grid(row=0, column=0, sticky="w", pady=4)
    ttk.Entry(form_fields, textvariable=full_name_var, width=30).grid(row=0, column=1, padx=(8, 0), pady=4, sticky="w")
    
    # College ID
    ttk.Label(form_fields, text="College ID").grid(row=1, column=0, sticky="w", pady=4)
    ttk.Entry(form_fields, textvariable=college_id_var, width=30).grid(row=1, column=1, padx=(8, 0), pady=4, sticky="w")
    
    # Email
    ttk.Label(form_fields, text="Email").grid(row=2, column=0, sticky="w", pady=4)
    ttk.Entry(form_fields, textvariable=email_var, width=30).grid(row=2, column=1, padx=(8, 0), pady=4, sticky="w")
    
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
                _member.upload_profile_image(uid, path)
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
    
    ttk.Button(profile_section, text="Upload Profile Image", command=_upload_profile_image).grid(row=2, column=0, pady=4)
    
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
                _member.upload_college_id_image(uid, path)
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
    
    ttk.Button(college_section, text="Upload College ID", command=_upload_college_id_image).grid(row=2, column=0, pady=4)
    
    # Action buttons
    buttons_frame = ttk.Frame(profile_form)
    buttons_frame.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="w")
    
    def _save_profile():
        try:
            _member.update_profile_data(
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
            _member.submit_for_verification(uid)
            messagebox.showinfo("Success", "Profile submitted for verification! Admin will review your documents.")
            refresh_dashboard()  # Update verification status
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit for verification: {str(e)}")
    
    ttk.Button(buttons_frame, text="Save Profile", style="Role.TButton", command=_save_profile).grid(row=0, column=0, padx=(0, 8))
    verify_btn = ttk.Button(buttons_frame, text="Send for Verification", style="Role.TButton", command=_submit_for_verification, state="disabled")
    verify_btn.grid(row=0, column=1)
    
    # Registered Vehicles section
    vehicles_profile = card(profile_form, title="Registered Vehicles")
    vehicles_profile.grid(row=3, column=0, sticky="ew")
    
    ttk.Label(vehicles_profile, text="Your registered vehicles").grid(row=0, column=0, padx=16, pady=(12, 8), sticky="w")
    vehicles_profile_list = ttk.Frame(vehicles_profile)
    vehicles_profile_list.grid(row=1, column=0, padx=16, pady=8, sticky="w")
    
    add_row = ttk.Frame(vehicles_profile)
    add_row.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="w")
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
        # Refresh vehicles list
        for w in vehicles_profile_list.winfo_children():
            w.destroy()
        rows = _member.list_vehicles(uid)
        for i, v in enumerate(rows):
            ttk.Label(vehicles_profile_list, text=v['plate_number']).grid(row=i, column=0, padx=8, pady=2, sticky="w")
        
        # Load existing images if any
        try:
            images = _member.get_verification_images(uid)
            if images.get('profile_image_url'):
                from PIL import Image, ImageTk
                img = Image.open(images['profile_image_url'])
                img = img.resize((100, 100), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                profile_image_label.configure(image=photo, text="")
                profile_image_label.image = photo
            if images.get('id_image_url'):
                from PIL import Image, ImageTk
                img = Image.open(images['id_image_url'])
                img = img.resize((100, 100), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                college_id_image_label.configure(image=photo, text="")
                college_id_image_label.image = photo
        except Exception:
            pass  # Images might not exist yet

    # Initial view
    set_active("dashboard")

    return wrapper


