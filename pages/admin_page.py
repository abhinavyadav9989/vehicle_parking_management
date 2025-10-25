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
        info_frame = ttk.LabelFrame(scrollable_frame, text="User Information", padding=8)
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Basic info
        ttk.Label(info_frame, text="Full Name:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=1)
        ttk.Label(info_frame, text=user_details.get('full_name', 'N/A')).grid(row=0, column=1, sticky="w", pady=1)
        
        ttk.Label(info_frame, text="College ID:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=1)
        ttk.Label(info_frame, text=user_details.get('college_id', 'N/A')).grid(row=1, column=1, sticky="w", pady=1)
        
        ttk.Label(info_frame, text="Email:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=1)
        ttk.Label(info_frame, text=user_details.get('email', 'N/A')).grid(row=2, column=1, sticky="w", pady=1)
        
        ttk.Label(info_frame, text="Role:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=1)
        ttk.Label(info_frame, text=user_details.get('role', 'N/A')).grid(row=3, column=1, sticky="w", pady=1)
        
        ttk.Label(info_frame, text="Profile Verified:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=1)
        verified_status = "Yes" if user_details.get('is_profile_verified') else "No"
        ttk.Label(info_frame, text=verified_status).grid(row=4, column=1, sticky="w", pady=1)
        
        # Verification status
        verification_frame = ttk.LabelFrame(scrollable_frame, text="Verification Status", padding=8)
        verification_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        verification_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(verification_frame, text="Status:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=1)
        ttk.Label(verification_frame, text=user_details.get('status', 'N/A')).grid(row=0, column=1, sticky="w", pady=1)
        
        ttk.Label(verification_frame, text="Submitted At:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=1)
        ttk.Label(verification_frame, text=str(user_details.get('created_at', 'N/A'))[:10]).grid(row=1, column=1, sticky="w", pady=1)
        
        # Vehicle information
        vehicle_frame = ttk.LabelFrame(scrollable_frame, text="Vehicle Information", padding=8)
        vehicle_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        vehicle_frame.grid_columnconfigure(1, weight=1)
        
        if user_details.get('vehicles'):
            for i, vehicle in enumerate(user_details['vehicles']):
                ttk.Label(vehicle_frame, text=f"Vehicle {i+1}:", font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=1)
                ttk.Label(vehicle_frame, text=f"{vehicle.get('plate_number', 'N/A')} - {vehicle.get('make', 'N/A')} {vehicle.get('model', 'N/A')}").grid(row=i, column=1, sticky="w", pady=1)
        else:
            ttk.Label(vehicle_frame, text="No vehicles registered").grid(row=0, column=0, columnspan=2, pady=1)
        
        # Images section
        images_frame = ttk.LabelFrame(scrollable_frame, text="Verification Images", padding=8)
        images_frame.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        
        # Profile image
        if user_details.get('profile_image_url'):
            try:
                profile_img = Image.open(user_details['profile_image_url'])
                profile_img = profile_img.resize((150, 150), Image.Resampling.LANCZOS)
                profile_photo = ImageTk.PhotoImage(profile_img)
                profile_label = ttk.Label(images_frame, image=profile_photo)
                profile_label.image = profile_photo  # Keep a reference
                profile_label.grid(row=0, column=0, padx=8, pady=4)
                ttk.Label(images_frame, text="Profile Image").grid(row=1, column=0, padx=8)
            except Exception as e:
                ttk.Label(images_frame, text=f"Profile image not available: {str(e)}").grid(row=0, column=0, padx=8, pady=4)
        else:
            ttk.Label(images_frame, text="No profile image").grid(row=0, column=0, padx=8, pady=4)
        
        # ID image
        if user_details.get('id_image_url'):
            try:
                id_img = Image.open(user_details['id_image_url'])
                id_img = id_img.resize((150, 150), Image.Resampling.LANCZOS)
                id_photo = ImageTk.PhotoImage(id_img)
                id_label = ttk.Label(images_frame, image=id_photo)
                id_label.image = id_photo  # Keep a reference
                id_label.grid(row=0, column=1, padx=8, pady=4)
                ttk.Label(images_frame, text="ID Image").grid(row=1, column=1, padx=8)
            except Exception as e:
                ttk.Label(images_frame, text=f"ID image not available: {str(e)}").grid(row=0, column=1, padx=8, pady=4)
        else:
            ttk.Label(images_frame, text="No ID image").grid(row=0, column=1, padx=8, pady=4)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load user details: {str(e)}")

def _navigate_to_view(view_func, wrapper):
    """Navigate to a specific view"""
    if not view_func:
        return
    
    # Clear current content
    for widget in wrapper._page.winfo_children():
        widget.destroy()
    
    # Build new view
    view_func(wrapper._page, wrapper._current_user)

def _build_dashboard_view(parent, current_user):
    """Build enhanced dashboard view with KPIs and user management"""
    # Welcome section
    heading = ttk.Frame(parent)
    heading.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    heading.grid_columnconfigure(0, weight=1)
    
    ttk.Label(heading, text="Welcome, Admin", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
    ttk.Label(heading, text="Manage System Operations and User Access", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=(12, 16))
    
    # KPI row
    kpi_row = ttk.Frame(parent)
    kpi_row.grid(row=1, column=0, sticky="ew", pady=(0, 16))
    
    def _refresh_dashboard():
        """Refresh dashboard KPIs"""
        for widget in kpi_row.winfo_children():
            widget.destroy()
        
    chips = [
        ("Users", _admin.count_users()),
        ("Guards", _admin.count_guards()),
        ("Vehicles", _admin.count_vehicles()),
        ("Open Flags", _admin.count_open_flags()),
    ]
        
    for idx, (lbl, val) in enumerate(chips):
            chip = ttk.Frame(kpi_row, style="Glass.TFrame")
            chip.grid(row=0, column=idx, padx=6)
            ttk.Label(chip, text=lbl, font=("Segoe UI", 9)).grid(row=0, column=0, padx=8, pady=4)
            ttk.Label(chip, text=str(val), font=("Segoe UI", 16, "bold")).grid(row=1, column=0, padx=8, pady=4)
    
    _refresh_dashboard()
    
    # User Management Section
    user_mgmt_frame = ttk.Frame(parent)
    user_mgmt_frame.grid(row=2, column=0, sticky="nsew", pady=(16, 0))
    user_mgmt_frame.grid_rowconfigure(2, weight=1)
    user_mgmt_frame.grid_columnconfigure(0, weight=1)
    
    # User Management Header
    user_header = ttk.Frame(user_mgmt_frame)
    user_header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    user_header.grid_columnconfigure(0, weight=1)
    
    ttk.Label(user_header, text="User Management", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
    
    # Filter controls
    filter_frame = ttk.Frame(user_mgmt_frame)
    filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
    
    ttk.Label(filter_frame, text="Filter by User Type:").grid(row=0, column=0, padx=(0, 8))
    user_type_combo = ttk.Combobox(filter_frame, values=["All", "Students", "Security Guards"], 
                                   state="readonly", width=15)
    user_type_combo.grid(row=0, column=1, padx=(0, 8))
    user_type_combo.set("All")
    
    # Users table
    table_frame = ttk.Frame(user_mgmt_frame)
    table_frame.grid(row=2, column=0, sticky="nsew")
    table_frame.grid_rowconfigure(1, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    
    # Table
    columns = ("ID", "Name", "Email", "Role", "College ID", "Verified", "Created")
    users_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
    
    # Configure columns
    users_tree.column("ID", width=50)
    users_tree.column("Name", width=150)
    users_tree.column("Email", width=200)
    users_tree.column("Role", width=100)
    users_tree.column("College ID", width=100)
    users_tree.column("Verified", width=80)
    users_tree.column("Created", width=100)
    
    # Configure headings
    for col in columns:
        users_tree.heading(col, text=col)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=users_tree.yview)
    users_tree.configure(yscrollcommand=scrollbar.set)
    
    users_tree.grid(row=1, column=0, sticky="nsew")
    scrollbar.grid(row=1, column=1, sticky="ns")
    
    def _load_filtered_users():
        """Load users based on selected filter"""
        for item in users_tree.get_children():
            users_tree.delete(item)
        
        try:
            cur = _admin.conn.cursor(dictionary=True)
            user_type = user_type_combo.get()
            
            if user_type == "All":
                cur.execute("""
                    SELECT id, full_name, email, role, college_id, is_profile_verified, created_at
                    FROM users 
                    ORDER BY created_at DESC
                """)
            elif user_type == "Students":
                cur.execute("""
                    SELECT id, full_name, email, role, college_id, is_profile_verified, created_at
                    FROM users 
                    WHERE role='member'
                    ORDER BY created_at DESC
                """)
            elif user_type == "Security Guards":
                cur.execute("""
                    SELECT id, full_name, email, role, college_id, is_profile_verified, created_at
                    FROM users 
                    WHERE role='guard'
                    ORDER BY created_at DESC
                """)
            
            users = cur.fetchall()
            
            for user in users:
                verified = "Yes" if user['is_profile_verified'] else "No"
                created = str(user['created_at'])[:10] if user['created_at'] else 'N/A'
                
                users_tree.insert("", "end", values=(
                    user['id'],
                    user['full_name'],
                    user['email'],
                    user['role'],
                    user['college_id'],
                    verified,
                    created
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")
        finally:
            cur.close()
    
    # Bind filter change event
    user_type_combo.bind("<<ComboboxSelected>>", lambda e: _load_filtered_users())
    
    # Load initial data
    _load_filtered_users()


def _build_vehicles_view(parent, current_user):
    """Build vehicles management view"""
    # Header
    header = ttk.Frame(parent)
    header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    header.grid_columnconfigure(0, weight=1)
    
    ttk.Label(header, text="Vehicle Management", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
    ttk.Label(header, text="Manage all registered vehicles in the system", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=(8, 0))
    
    # Table frame
    table_frame = ttk.Frame(parent)
    table_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
    table_frame.grid_rowconfigure(1, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    
    # Table
    columns = ("ID", "Plate Number", "Owner", "Make", "Model", "Color", "Status", "Registered")
    vehicles_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
    
    # Configure columns
    vehicles_tree.column("ID", width=50)
    vehicles_tree.column("Plate Number", width=120)
    vehicles_tree.column("Owner", width=150)
    vehicles_tree.column("Make", width=100)
    vehicles_tree.column("Model", width=100)
    vehicles_tree.column("Color", width=100)
    vehicles_tree.column("Status", width=80)
    vehicles_tree.column("Registered", width=100)
    
    # Configure headings
    for col in columns:
        vehicles_tree.heading(col, text=col)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=vehicles_tree.yview)
    vehicles_tree.configure(yscrollcommand=scrollbar.set)
    
    vehicles_tree.grid(row=1, column=0, sticky="nsew")
    scrollbar.grid(row=1, column=1, sticky="ns")
    
    def _load_vehicles():
        """Load vehicles from database"""
        for item in vehicles_tree.get_children():
            vehicles_tree.delete(item)
        
        try:
            cur = _admin.conn.cursor(dictionary=True)
            cur.execute("""
                SELECT v.id, v.plate_number, u.full_name as owner, v.make, v.model, v.color, 
                       v.is_active, v.created_at
                FROM vehicles v
                JOIN users u ON u.id = v.user_id
                ORDER BY v.created_at DESC
            """)
            vehicles = cur.fetchall()
            
            for vehicle in vehicles:
                status = "Active" if vehicle['is_active'] else "Inactive"
                registered = str(vehicle['created_at'])[:10] if vehicle['created_at'] else 'N/A'
                
                vehicles_tree.insert("", "end", values=(
                    vehicle['id'],
                    vehicle['plate_number'],
                    vehicle['owner'],
                    vehicle['make'],
                    vehicle['model'],
                    vehicle['color'],
                    status,
                    registered
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load vehicles: {str(e)}")
        finally:
            cur.close()
    
    _load_vehicles()

def _build_verification_view(parent, current_user):
    """Build verification management view with proper action buttons"""
    # Header
    header = ttk.Frame(parent)
    header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    header.grid_columnconfigure(0, weight=1)
    
    ttk.Label(header, text="User Verification", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
    ttk.Label(header, text="Review and approve user profile verifications", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=(8, 0))
    
    # Table frame
    table_frame = ttk.Frame(parent)
    table_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
    table_frame.grid_rowconfigure(1, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    
    # Table (without Actions column)
    columns = ("User ID", "Name", "College ID", "Status", "Submitted")
    verification_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
    
    # Configure columns
    verification_tree.column("User ID", width=80)
    verification_tree.column("Name", width=200)
    verification_tree.column("College ID", width=150)
    verification_tree.column("Status", width=100)
    verification_tree.column("Submitted", width=120)
    
    # Configure headings
    for col in columns:
        verification_tree.heading(col, text=col)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=verification_tree.yview)
    verification_tree.configure(yscrollcommand=scrollbar.set)
    
    verification_tree.grid(row=1, column=0, sticky="nsew")
    scrollbar.grid(row=1, column=1, sticky="ns")
    
    # Action buttons frame (below table)
    actions_frame = ttk.Frame(parent)
    actions_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
    actions_frame.grid_columnconfigure(0, weight=1)
    
    def _view_user_details_local():
        """View details for selected user (only one at a time)"""
        selection = verification_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to view details.")
            return
        if len(selection) > 1:
            messagebox.showwarning("Multiple Selection", "Please select only one user to view details.")
            return
        
        # Get user ID from selected row
        item = verification_tree.item(selection[0])
        user_id = int(item['values'][0])
        # Call the global _view_user_details function
        _view_user_details(verification_tree, current_user)
    
    def _approve_selected():
        """Approve selected users"""
        selection = verification_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select users to approve.")
            return
        
        if messagebox.askyesno("Confirm Approval", f"Approve {len(selection)} user(s)?"):
            try:
                for item_id in selection:
                    item = verification_tree.item(item_id)
                    user_id = int(item['values'][0])
                    print(f"Approving user ID: {user_id} by admin: {current_user['id']}")
                    _admin.approve_verification(user_id, current_user['id'])
                
                messagebox.showinfo("Success", f"Approved {len(selection)} user(s).")
                _load_verifications()  # Refresh table
            except Exception as e:
                print(f"Error approving users: {str(e)}")
                messagebox.showerror("Error", f"Failed to approve users: {str(e)}")
    
    def _reject_selected():
        """Reject selected users"""
        selection = verification_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select users to reject.")
            return
        
        reason = simpledialog.askstring("Rejection Reason", "Enter reason for rejection:")
        if not reason:
            return
        
        if messagebox.askyesno("Confirm Rejection", f"Reject {len(selection)} user(s)?"):
            try:
                for item_id in selection:
                    item = verification_tree.item(item_id)
                    user_id = int(item['values'][0])
                    print(f"Rejecting user ID: {user_id} by admin: {current_user['id']} with reason: {reason}")
                    _admin.reject_verification(user_id, current_user['id'], reason)
                
                messagebox.showinfo("Success", f"Rejected {len(selection)} user(s).")
                _load_verifications()  # Refresh table
            except Exception as e:
                print(f"Error rejecting users: {str(e)}")
                messagebox.showerror("Error", f"Failed to reject users: {str(e)}")
    
    # Action buttons
    ttk.Button(actions_frame, text="View Details", command=_view_user_details_local).grid(row=0, column=0, padx=(0, 8))
    ttk.Button(actions_frame, text="Approve Selected", command=_approve_selected).grid(row=0, column=1, padx=(0, 8))
    ttk.Button(actions_frame, text="Reject Selected", command=_reject_selected).grid(row=0, column=2)
    
    def _load_verifications():
        """Load pending verifications from database"""
        for item in verification_tree.get_children():
            verification_tree.delete(item)
        
        try:
            verifications = _admin.list_pending_verifications()
            
            for r in verifications:
                status = r.get('status', 'pending')
                submitted = str(r.get('created_at', 'N/A'))[:10]
                
                verification_tree.insert("", "end", values=(
                    r['user_id'],
                    r['full_name'],
                    r['college_id'],
                    status,
                    submitted
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load verifications: {str(e)}")
    
    _load_verifications()

def _build_flags_view(parent, current_user):
    """Build flags management view with card-based layout"""
    # Header
    header = ttk.Frame(parent)
    header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    header.grid_columnconfigure(0, weight=1)
    
    ttk.Label(header, text="Manage Flags", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
    ttk.Label(header, text="Review and resolve issues raised by security personnel", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=(8, 0))
    
    # Filter tabs
    filter_frame = ttk.Frame(parent)
    filter_frame.grid(row=1, column=0, sticky="ew", pady=(16, 8))
    
    # Tab buttons
    open_btn = ttk.Button(filter_frame, text="Open Flags (0)", command=lambda: _switch_tab("open"))
    open_btn.grid(row=0, column=0, padx=(0, 8))
    
    resolved_btn = ttk.Button(filter_frame, text="Resolved (0)", command=lambda: _switch_tab("resolved"))
    resolved_btn.grid(row=0, column=1)
    
    # Flags container (scrollable)
    flags_container = ttk.Frame(parent)
    flags_container.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
    flags_container.grid_rowconfigure(0, weight=1)
    flags_container.grid_columnconfigure(0, weight=1)
    
    # Create canvas and scrollbar for scrollable flags
    canvas = tk.Canvas(flags_container, bg="white")
    scrollbar = ttk.Scrollbar(flags_container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    
    def _create_flag_card(flag_data, parent_frame, row_index):
        """Create a flag card with the design from the image"""
        # Main card frame
        card = ttk.Frame(parent_frame, style="Glass.TFrame")
        card.grid(row=row_index, column=0, sticky="ew", padx=8, pady=8)
        card.grid_columnconfigure(1, weight=1)
        
        # Flag icon and status
        icon_frame = ttk.Frame(card)
        icon_frame.grid(row=0, column=0, rowspan=3, padx=8, pady=8, sticky="nw")
        
        # Flag icon (red square with flag)
        flag_icon = tk.Frame(icon_frame, bg="#FF6B6B", width=40, height=40)
        flag_icon.grid(row=0, column=0)
        flag_icon.grid_propagate(False)
        
        # Status tag
        status_color = "#FF6B6B" if flag_data['status'] == 'open' else "#4CAF50"
        status_tag = tk.Frame(card, bg=status_color, height=20)
        status_tag.grid(row=0, column=1, sticky="ne", padx=8, pady=8)
        status_tag.grid_propagate(False)
        
        ttk.Label(status_tag, text=flag_data['status'].upper(), 
                 foreground="white", font=("Arial", 8, "bold")).grid(row=0, column=0, padx=8, pady=2)
        
        # Flag title
        title = ttk.Label(card, text=flag_data['title'], 
                         font=("Segoe UI", 12, "bold"))
        title.grid(row=1, column=1, sticky="w", padx=8, pady=(0, 4))
        
        # Details frame
        details_frame = ttk.Frame(card)
        details_frame.grid(row=2, column=1, sticky="ew", padx=8, pady=4)
        
        # Vehicle number
        ttk.Label(details_frame, text=f"🚗 {flag_data['vehicle']}", 
                 font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        
        # Date and time
        ttk.Label(details_frame, text=f"🕐 {flag_data['created_at']}", 
                 font=("Arial", 9)).grid(row=1, column=0, sticky="w")
        
        # Raised by
        ttk.Label(details_frame, text=f"👤 Raised by: {flag_data['raised_by']}", 
                 font=("Arial", 9)).grid(row=2, column=0, sticky="w")
        
        # Notes section
        notes_frame = ttk.Frame(card)
        notes_frame.grid(row=3, column=1, sticky="ew", padx=8, pady=8)
        notes_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(notes_frame, text="Notes:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        
        notes_text = tk.Text(notes_frame, height=3, width=50, wrap="word", 
                           font=("Arial", 9), bg="#F5F5F5", relief="flat")
        notes_text.grid(row=1, column=0, sticky="ew", pady=4)
        notes_text.insert("1.0", flag_data['notes'])
        notes_text.config(state="disabled")
        
        # Resolve button (only for open flags)
        if flag_data['status'] == 'open':
            resolve_btn = ttk.Button(card, text="Resolve Flag", 
                                   command=lambda: _resolve_flag(flag_data['id']))
            resolve_btn.grid(row=4, column=1, sticky="e", padx=8, pady=8)
        
        return card
    
    def _load_flags():
        """Load flags from database and create cards"""
        # Clear existing cards
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        try:
            cur = _admin.conn.cursor(dictionary=True)
            cur.execute("""
                SELECT f.id, f.reason, f.status, f.created_at, f.resolution_note,
                       u.full_name as raised_by, v.plate_number as vehicle
                FROM flags f
                JOIN users u ON u.id = f.raised_by_guard_id
                LEFT JOIN vehicles v ON v.id = f.vehicle_id
                WHERE f.status = %s
                ORDER BY f.created_at DESC
            """, (current_filter,))
            
            flags = cur.fetchall()
            
            # Update tab button text
            open_count = len([f for f in flags if f['status'] == 'open'])
            resolved_count = len([f for f in flags if f['status'] == 'closed'])
            
            open_btn.config(text=f"Open Flags ({open_count})")
            resolved_btn.config(text=f"Resolved ({resolved_count})")
            
            # Create flag cards in vertical scrollable list
            for i, flag in enumerate(flags):
                # Map reason to title
                reason_titles = {
                    'no_slots': 'No parking slots available',
                    'suspicious': 'Suspicious vehicle activity',
                    'mismatch': 'Vehicle verified but slot allocation failed',
                    'other': 'Other parking issue'
                }
                
                flag_data = {
                    'id': flag['id'],
                    'title': reason_titles.get(flag['reason'], flag['reason']),
                    'status': flag['status'],
                    'vehicle': flag['vehicle'] or 'N/A',
                    'created_at': str(flag['created_at'])[:19].replace('T', ' '),
                    'raised_by': flag['raised_by'],
                    'notes': flag['resolution_note'] or 'No notes provided'
                }
                
                # Create each flag card in a new row
                _create_flag_card(flag_data, scrollable_frame, i)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load flags: {str(e)}")
        finally:
            cur.close()
    
    def _switch_tab(filter_type):
        """Switch between open and resolved flags"""
        nonlocal current_filter
        current_filter = filter_type
        _load_flags()
    
    def _resolve_flag(flag_id):
        """Resolve a flag"""
        resolution = simpledialog.askstring("Resolve Flag", "Enter resolution notes:")
        if not resolution:
            return
        
        try:
            cur = _admin.conn.cursor()
            cur.execute("""
                UPDATE flags 
                SET status='closed', closed_by_admin_id=%s, closed_at=NOW(), resolution_note=%s
                WHERE id=%s
            """, (current_user['id'], resolution, flag_id))
            _admin.conn.commit()
            
            messagebox.showinfo("Success", "Flag resolved successfully.")
            _load_flags()  # Refresh the view
            except Exception as e:
            messagebox.showerror("Error", f"Failed to resolve flag: {str(e)}")
        finally:
            cur.close()
    
    # Initialize with open flags
    current_filter = "open"
    _load_flags()

def render(parent, on_logout, current_user=None):
    """Render the admin page with left sidebar navigation"""
    # Main wrapper
    wrapper = ttk.Frame(parent)
    wrapper.grid(row=0, column=0, sticky="nsew")
    wrapper.grid_rowconfigure(0, weight=1)
    wrapper.grid_columnconfigure(1, weight=1)
    
    # Left sidebar
    sidebar = ttk.Frame(wrapper, width=180)
    sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=8)
    sidebar.grid_propagate(False)
    
    # Sidebar title
    ttk.Label(sidebar, text="Admin Dashboard", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=8, pady=(8, 16))
    
    # Navigation buttons (removed Users - now in Dashboard)
    nav_buttons = [
        ("Dashboard", _build_dashboard_view),
        ("Vehicles", _build_vehicles_view),
        ("Verification", _build_verification_view),
        ("Flags", _build_flags_view),
        ("Logout", None)
    ]
    
    for i, (text, command) in enumerate(nav_buttons):
        if text == "Logout":
            btn = ttk.Button(sidebar, text=text, command=on_logout)
        else:
            btn = ttk.Button(sidebar, text=text, command=lambda cmd=command: _navigate_to_view(cmd, wrapper))
        btn.grid(row=i+1, column=0, sticky="ew", padx=8, pady=2)
    
    # Main content area
    content = ttk.Frame(wrapper)
    content.grid(row=0, column=1, sticky="nsew", padx=(0, 8), pady=8)
    content.grid_rowconfigure(0, weight=1)
    content.grid_columnconfigure(0, weight=1)
    
    # Content background
    page_bg = ttk.Frame(content)
    page_bg.grid(row=0, column=0, sticky="nsew")
    page_bg.grid_rowconfigure(0, weight=1)
    page_bg.grid_columnconfigure(0, weight=1)
    
    # Page container
    page = ttk.Frame(page_bg)
    page.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
    page.grid_rowconfigure(0, weight=1)
    page.grid_columnconfigure(0, weight=1)
    
    # Store references for navigation
    wrapper._content = content
    wrapper._page = page
    wrapper._current_user = current_user
    
    # Show dashboard by default
    _navigate_to_view(_build_dashboard_view, wrapper)

    return wrapper
