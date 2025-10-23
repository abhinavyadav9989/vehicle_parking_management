import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from services.admin_service import AdminService
from PIL import Image, ImageTk
import os

_admin = AdminService()


def _view_user_details(tree, current_user):
    """Show detailed user information in a popup window"""
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select a user to view details.")
        return
    
    # Get user ID from selected row
    item = tree.item(selection[0])
    user_id = int(item['values'][0])
    
    try:
        # Get detailed user information
        user_details = _admin.get_user_details_for_verification(user_id)
        
        # Create popup window
        popup = tk.Toplevel()
        popup.title(f"User Details - {user_details.get('full_name', 'Unknown')}")
        popup.geometry("600x500")
        popup.resizable(True, True)
        
        # Create scrollable frame
        canvas = tk.Canvas(popup)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # User information section
        info_frame = ttk.LabelFrame(scrollable_frame, text="User Information", padding=10)
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Basic info
        ttk.Label(info_frame, text="Full Name:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text=user_details.get('full_name', 'N/A')).grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Label(info_frame, text="Email:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text=user_details.get('email', 'N/A')).grid(row=1, column=1, sticky="w", pady=2)
        
        ttk.Label(info_frame, text="College ID:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text=user_details.get('college_id', 'N/A')).grid(row=2, column=1, sticky="w", pady=2)
        
        ttk.Label(info_frame, text="Status:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=2)
        status = user_details.get('status', 'pending')
        status_color = "green" if status == "approved" else "red" if status == "rejected" else "orange"
        ttk.Label(info_frame, text=status.upper(), foreground=status_color).grid(row=3, column=1, sticky="w", pady=2)
        
        # Profile image section
        profile_frame = ttk.LabelFrame(scrollable_frame, text="Profile Image", padding=10)
        profile_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        profile_image_label = ttk.Label(profile_frame, text="No profile image available")
        profile_image_label.grid(row=0, column=0, pady=10)
        
        # College ID image section
        college_frame = ttk.LabelFrame(scrollable_frame, text="College ID Image", padding=10)
        college_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        college_image_label = ttk.Label(college_frame, text="No college ID image available")
        college_image_label.grid(row=0, column=0, pady=10)
        
        # Load and display images if available
        profile_image_url = user_details.get('profile_image_url')
        if profile_image_url:
            if os.path.exists(profile_image_url):
                try:
                    img = Image.open(profile_image_url)
                    img = img.resize((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    profile_image_label.configure(image=photo, text="")
                    profile_image_label.image = photo  # Keep a reference
                except Exception as e:
                    profile_image_label.configure(text=f"Error loading profile image: {str(e)}")
            else:
                profile_image_label.configure(text=f"Profile image not found: {profile_image_url}")
        else:
            profile_image_label.configure(text="No profile image URL in database")
        
        college_id_image_url = user_details.get('id_image_url')
        if college_id_image_url:
            if os.path.exists(college_id_image_url):
                try:
                    img = Image.open(college_id_image_url)
                    img = img.resize((200, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    college_image_label.configure(image=photo, text="")
                    college_image_label.image = photo  # Keep a reference
                except Exception as e:
                    college_image_label.configure(text=f"Error loading college ID image: {str(e)}")
            else:
                college_image_label.configure(text=f"College ID image not found: {college_id_image_url}")
        else:
            college_image_label.configure(text="No college ID image URL in database")
        
        # Vehicles section
        vehicles_frame = ttk.LabelFrame(scrollable_frame, text="Registered Vehicles", padding=10)
        vehicles_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        vehicles_frame.grid_columnconfigure(0, weight=1)
        
        vehicles = user_details.get('vehicles', [])
        if vehicles:
            for i, vehicle in enumerate(vehicles):
                vehicle_info = f"Plate: {vehicle['plate_number']} | Active: {'Yes' if vehicle['is_active'] else 'No'}"
                ttk.Label(vehicles_frame, text=vehicle_info).grid(row=i, column=0, sticky="w", pady=2)
        else:
            ttk.Label(vehicles_frame, text="No vehicles registered").grid(row=0, column=0, pady=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load user details: {str(e)}")


def _approve_selected(tree, current_user):
    """Approve the selected user verification"""
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select a user to approve.")
        return
    
    # Get user ID from selected row
    item = tree.item(selection[0])
    user_id = int(item['values'][0])
    user_name = item['values'][1]
    
    # Confirm action
    if messagebox.askyesno("Confirm Approval", f"Are you sure you want to approve {user_name}?"):
        try:
            _admin.approve_verification(user_id, current_user.get('id', 0))
            messagebox.showinfo("Success", f"User {user_name} has been approved.")
            # Refresh the tree
            _refresh_verification_tree(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve user: {str(e)}")


def _reject_selected(tree, current_user):
    """Reject the selected user verification"""
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select a user to reject.")
        return
    
    # Get user ID from selected row
    item = tree.item(selection[0])
    user_id = int(item['values'][0])
    user_name = item['values'][1]
    
    # Ask for rejection reason
    reason = tk.simpledialog.askstring("Rejection Reason", f"Please provide a reason for rejecting {user_name}:")
    if reason is None:  # User cancelled
        return
    
    # Confirm action
    if messagebox.askyesno("Confirm Rejection", f"Are you sure you want to reject {user_name}?"):
        try:
            _admin.reject_verification(user_id, current_user.get('id', 0), reason)
            messagebox.showinfo("Success", f"User {user_name} has been rejected.")
            # Refresh the tree
            _refresh_verification_tree(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reject user: {str(e)}")


def _refresh_verification_tree(tree):
    """Refresh the verification tree with updated data"""
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
    
    # Load new data
    rows = _admin.list_pending_verifications()
    for r in rows:
        tree.insert("", "end", values=(
            r['id'],
            r['full_name'],
            r['email'],
            r.get('college_id', 'N/A'),
            r.get('status', 'pending'),
'N/A'
        ))


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
    title = ttk.Label(bar, text="Campus Management Dashboard - Admin Access")
    title.configure(font=("Segoe UI Semibold", 13))
    title.grid(row=0, column=0, sticky="w")
    ttk.Button(bar, text="Logout", command=on_logout).grid(row=0, column=1, sticky="e")

    # Tabs
    tabs_card = ttk.Frame(wrapper)
    tabs_card.grid(row=1, column=0, padx=24, pady=(4, 12), sticky="nsew")
    tabs_card.grid_rowconfigure(0, weight=1)
    tabs_card.grid_columnconfigure(0, weight=1)
    nb = ttk.Notebook(tabs_card)
    nb.grid(row=0, column=0, sticky="nsew")

    dash_tab = ttk.Frame(nb)
    verify_tab = ttk.Frame(nb)
    flags_tab = ttk.Frame(nb)
    
    # Configure tabs to expand
    for tab in (dash_tab, verify_tab, flags_tab):
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

    nb.add(dash_tab, text="Dashboard")
    nb.add(verify_tab, text="Verification")
    nb.add(flags_tab, text="Flags")

    # Dashboard KPIs
    kpi_row = ttk.Frame(dash_tab)
    kpi_row.grid(row=0, column=0, pady=(0, 12))  # Align with top of content area
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

    # Enhanced Verification UI
    verify_tab.grid_rowconfigure(1, weight=1)  # Only table row expands
    verify_tab.grid_columnconfigure(0, weight=1)
    
    # Header - positioned 2-20px below tabs
    header = ttk.Frame(verify_tab)
    header.grid(row=0, column=0, sticky="ew", pady=(8, 8))  # 8px gap from tabs, 8px gap to table
    header.grid_columnconfigure(0, weight=1)

    ttk.Label(header, text="User Verification", font=("Arial", 16, "bold")).grid(
        row=0, column=0, sticky="w"
    )

    # Create the verification table - positioned below title with gap
    table_frame = ttk.Frame(verify_tab)
    table_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 8))  # No top gap, 8px gap to buttons
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    # Create Treeview for verification list
    columns = ("ID", "Full Name", "Email", "College ID", "Status", "Submitted")
    verification_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
    
    # Configure column headings and widths
    verification_tree.heading("ID", text="ID")
    verification_tree.heading("Full Name", text="Full Name")
    verification_tree.heading("Email", text="Email")
    verification_tree.heading("College ID", text="College ID")
    verification_tree.heading("Status", text="Status")
    verification_tree.heading("Submitted", text="Submitted")
    
    verification_tree.column("ID", width=50, minwidth=50)
    verification_tree.column("Full Name", width=150, minwidth=100)
    verification_tree.column("Email", width=200, minwidth=150)
    verification_tree.column("College ID", width=100, minwidth=80)
    verification_tree.column("Status", width=80, minwidth=60)
    verification_tree.column("Submitted", width=120, minwidth=100)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=verification_tree.yview)
    verification_tree.configure(yscrollcommand=scrollbar.set)

    # Grid the treeview and scrollbar
    verification_tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Control buttons frame - positioned below table
    controls_frame = ttk.Frame(verify_tab)
    controls_frame.grid(row=2, column=0, sticky="ew", pady=(0, 0))  # No gaps, directly below table
    controls_frame.grid_columnconfigure(0, weight=1)

    # Buttons
    btn_frame = ttk.Frame(controls_frame)
    btn_frame.grid(row=0, column=0, sticky="e")

    view_details_btn = ttk.Button(
        btn_frame,
        text="View Details",
        command=lambda: _view_user_details(verification_tree, current_user),
        state="disabled"
    )
    view_details_btn.grid(row=0, column=0, padx=(0, 8))

    approve_btn = ttk.Button(
        btn_frame,
        text="Approve Selected",
        command=lambda: _approve_selected(verification_tree, current_user),
        state="disabled"
    )
    approve_btn.grid(row=0, column=1, padx=(0, 8))

    reject_btn = ttk.Button(
        btn_frame,
        text="Reject Selected",
        command=lambda: _reject_selected(verification_tree, current_user),
        state="disabled"
    )
    reject_btn.grid(row=0, column=2)

    # Bind selection event
    def on_verification_select(event):
        selection = verification_tree.selection()
        if selection:
            view_details_btn.config(state="normal")
            approve_btn.config(state="normal")
            reject_btn.config(state="normal")
        else:
            view_details_btn.config(state="disabled")
            approve_btn.config(state="disabled")
            reject_btn.config(state="disabled")
    
    verification_tree.bind("<<TreeviewSelect>>", on_verification_select)

    # Load verification data
    rows = _admin.list_pending_verifications()
    for row in verification_tree.get_children():
        verification_tree.delete(row)
    
    for r in rows:
        verification_tree.insert("", "end", values=(
            r['id'],
            r['full_name'],
            r['email'],
            r.get('college_id', 'N/A'),
            r.get('status', 'pending'),
            str(r.get('created_at', 'N/A'))[:10] if r.get('created_at') else 'N/A'
        ))

    # Flags
    flags = _admin.list_open_flags()
    ttk.Label(flags_tab, text=f"Open Flags: {len(flags)}").grid(row=0, column=0, padx=8, pady=(0, 8), sticky="w")  # Align with top
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