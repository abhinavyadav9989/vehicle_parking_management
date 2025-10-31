"""
CustomTkinter authentication pages with two-panel layout
Left panel (60%): Role-specific illustration
Right panel (40%): Login/Registration form
"""

import customtkinter as ctk
from customtkinter import CTkFont, CTkImage
from tkinter import messagebox
from PIL import Image, ImageTk
import os


class AuthPage:
    """Base class for authentication pages with two-panel layout"""
    
    def __init__(self, parent, role, auth_service, on_back, on_success):
        self.parent = parent
        self.role = role
        self.auth_service = auth_service
        self.on_back = on_back
        self.on_success = on_success
        
        # Role configuration
        self.role_config = {
            "guard": {
                "title": "Security Guard",
                "description": "Manage vehicle access and parking operations",
                "image": "security_guard-removebg-preview.png",
                "icon": "🛡️"
            },
            "member": {
                "title": "Campus Student",
                "description": "View parking status and manage profile",
                "image": "student-removebg-preview.png",
                "icon": "🎓"
            },
            "admin": {
                "title": "Campus Management",
                "description": "Administer system and resolve issues",
                "image": "management-removebg-preview.png",
                "icon": "👔"
            }
        }
        
        self.config = self.role_config.get(role, {})
        self._base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._assets_dir = os.path.join(self._base_dir, "assets")
        
        # Set appearance mode
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create main container
        self.main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Back button at top
        back_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        back_frame.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=20)
        
        back_btn = ctk.CTkButton(
            back_frame,
            text="← Back",
            width=80,
            height=30,
            fg_color="transparent",
            hover_color="#f3f4f6",
            text_color="#6b7280",
            font=CTkFont(size=12),
            command=on_back
        )
        back_btn.pack(side="left")
        
        # Configure grid weights for 60/40 split
        self.main_frame.grid_columnconfigure(0, weight=6)  # Left panel 60%
        self.main_frame.grid_columnconfigure(1, weight=4)  # Right panel 40%
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Create panels
        self.create_left_panel()
        self.create_right_panel()
        
    def create_left_panel(self):
        """Create left panel with role illustration - centered and responsive"""
        left_panel = ctk.CTkFrame(self.main_frame, fg_color="#ffffff")
        left_panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configure grid for vertical centering
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(0, weight=1)  # Top spacer
        left_panel.grid_rowconfigure(1, weight=0)  # Content (no expansion)
        left_panel.grid_rowconfigure(2, weight=1)  # Bottom spacer
        
        # Top spacer for vertical centering
        top_spacer = ctk.CTkFrame(left_panel, fg_color="transparent")
        top_spacer.grid(row=0, column=0, sticky="ew")
        
        # Container for image and text - centered vertically
        content_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="", padx=20, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Load role image path first
        img_path = os.path.join(self._assets_dir, self.config.get("image", ""))
        
        # Get panel dimensions for responsive sizing
        def update_image_size():
            """Update image size based on panel dimensions - auto-adjusts with screen"""
            try:
                left_panel.update_idletasks()
                panel_width = left_panel.winfo_width()
                panel_height = left_panel.winfo_height()
                
                # Calculate responsive image size (35% of panel height, max 500px)
                if panel_height > 100:  # Ensure panel is rendered
                    img_size = min(int(panel_height * 0.35), 500)
                    img_size = max(img_size, 250)  # Minimum size
                else:
                    img_size = 350  # Default size
                
                # Update image if it exists
                if hasattr(content_frame, '_image_label') and content_frame._image_label.winfo_exists():
                    try:
                        pil_image = Image.open(img_path).convert("RGBA")
                        pil_image = pil_image.resize((img_size, img_size), Image.Resampling.LANCZOS)
                        ctk_image = CTkImage(light_image=pil_image, dark_image=pil_image, size=(img_size, img_size))
                        content_frame._image_label.configure(image=ctk_image)
                        content_frame._image_label.image = ctk_image  # Keep reference
                    except Exception:
                        pass
                
                # Update font sizes based on panel size - auto-adjusts
                if hasattr(content_frame, '_title_label') and content_frame._title_label.winfo_exists():
                    title_font_size = min(int(panel_height * 0.04), 32)
                    title_font_size = max(title_font_size, 20)
                    content_frame._title_label.configure(font=CTkFont(size=title_font_size, weight="bold"))
                
                if hasattr(content_frame, '_desc_label') and content_frame._desc_label.winfo_exists():
                    desc_font_size = min(int(panel_height * 0.02), 18)
                    desc_font_size = max(desc_font_size, 12)
                    content_frame._desc_label.configure(font=CTkFont(size=desc_font_size))
                    
            except Exception:
                pass
        
        # Load initial image
        try:
            # Load initial image
            pil_image = Image.open(img_path).convert("RGBA")
            initial_size = 350
            pil_image = pil_image.resize((initial_size, initial_size), Image.Resampling.LANCZOS)
            ctk_image = CTkImage(light_image=pil_image, dark_image=pil_image, size=(initial_size, initial_size))
            
            # Image label centered
            image_label = ctk.CTkLabel(
                content_frame,
                image=ctk_image,
                text="",
                fg_color="transparent"
            )
            image_label.grid(row=0, column=0, pady=(0, 20))
            content_frame._image_label = image_label  # Store reference
            
        except Exception as e:
            # Fallback if image not found
            icon_label = ctk.CTkLabel(
                content_frame,
                text=self.config.get("icon", "👤"),
                font=CTkFont(size=120),
                fg_color="transparent"
            )
            icon_label.grid(row=0, column=0, pady=(0, 20))
        
        # Role title - responsive font size
        title_label = ctk.CTkLabel(
            content_frame,
            text=self.config.get("title", ""),
            font=CTkFont(size=28, weight="bold"),
            text_color="#1f2937",
            fg_color="transparent",
            wraplength=400
        )
        title_label.grid(row=1, column=0, pady=(0, 10))
        content_frame._title_label = title_label  # Store reference
        
        # Role description - responsive font size
        desc_label = ctk.CTkLabel(
            content_frame,
            text=self.config.get("description", ""),
            font=CTkFont(size=14),
            text_color="#6b7280",
            fg_color="transparent",
            wraplength=400
        )
        desc_label.grid(row=2, column=0, pady=(0, 0))
        content_frame._desc_label = desc_label  # Store reference
        
        # Bottom spacer for vertical centering
        bottom_spacer = ctk.CTkFrame(left_panel, fg_color="transparent")
        bottom_spacer.grid(row=2, column=0, sticky="ew")
        
        # Bind resize event to update sizes - auto-adjusts on screen resize
        def on_panel_resize(event):
            # Throttle resize updates to avoid excessive processing
            if hasattr(left_panel, '_resize_job'):
                left_panel.after_cancel(left_panel._resize_job)
            left_panel._resize_job = left_panel.after(50, update_image_size)
        
        left_panel.bind("<Configure>", on_panel_resize)
        
        # Initial size update after panel is rendered
        left_panel.after(200, update_image_size)
        
    def create_right_panel(self):
        """Create right panel with login/registration form - centered vertically, aligned left"""
        right_panel = ctk.CTkFrame(self.main_frame, fg_color="#ffffff")
        right_panel.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        
        # Configure grid for vertical centering (same as left panel)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)  # Top spacer
        right_panel.grid_rowconfigure(1, weight=0)  # Content (no expansion)
        right_panel.grid_rowconfigure(2, weight=1)  # Bottom spacer
        
        # Top spacer for vertical centering
        top_spacer_right = ctk.CTkFrame(right_panel, fg_color="transparent")
        top_spacer_right.grid(row=0, column=0, sticky="ew")
        
        # Container for tabs - centered vertically, aligned to left
        tabs_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        tabs_container.grid(row=1, column=0, sticky="w", padx=40, pady=20)  # sticky="w" aligns to left
        tabs_container.grid_columnconfigure(0, weight=1)
        
        # Create tabbed interface for Login/Register
        self.create_tabs(tabs_container)
        
        # Store references for responsive scaling
        self.right_panel = right_panel
        self.tabs_container = tabs_container
        
        # Bottom spacer for vertical centering
        bottom_spacer_right = ctk.CTkFrame(right_panel, fg_color="transparent")
        bottom_spacer_right.grid(row=2, column=0, sticky="ew")
        
        # Bind resize event to update form sizes - auto-adjusts with screen
        def on_right_panel_resize(event):
            # Throttle resize updates
            if hasattr(right_panel, '_resize_job'):
                right_panel.after_cancel(right_panel._resize_job)
            right_panel._resize_job = right_panel.after(50, update_form_sizes)
        
        def update_form_sizes():
            """Update form element sizes based on panel dimensions"""
            try:
                right_panel.update_idletasks()
                panel_height = right_panel.winfo_height()
                
                if panel_height < 100:
                    return
                
                # Calculate responsive sizes based on panel height
                # Title font size (scales with screen)
                title_font_size = min(int(panel_height * 0.035), 32)
                title_font_size = max(title_font_size, 20)
                
                # Label font size
                label_font_size = min(int(panel_height * 0.018), 16)
                label_font_size = max(label_font_size, 11)
                
                # Input font size
                input_font_size = min(int(panel_height * 0.020), 18)
                input_font_size = max(input_font_size, 13)
                
                # Input height
                input_height = min(int(panel_height * 0.05), 45)
                input_height = max(input_height, 30)
                
                # Button height
                button_height = min(int(panel_height * 0.055), 50)
                button_height = max(button_height, 35)
                
                # Button font size
                button_font_size = min(int(panel_height * 0.022), 18)
                button_font_size = max(button_font_size, 13)
                
                # Link font size
                link_font_size = min(int(panel_height * 0.018), 15)
                link_font_size = max(link_font_size, 11)
                
                # Update form elements if they exist - using stored references
                if hasattr(self, 'tabview') and self.tabview.winfo_exists():
                    # Update login form
                    try:
                        login_tab = self.tabview.tab("Sign In")
                        if hasattr(login_tab, '_form_elements'):
                            elements = login_tab._form_elements
                            if 'title' in elements:
                                elements['title'].configure(font=CTkFont(size=title_font_size, weight="bold"))
                            if 'email_label' in elements:
                                elements['email_label'].configure(font=CTkFont(size=label_font_size))
                            if 'password_label' in elements:
                                elements['password_label'].configure(font=CTkFont(size=label_font_size))
                            if 'email_entry' in elements:
                                elements['email_entry'].configure(height=input_height, font=CTkFont(size=input_font_size))
                            if 'password_entry' in elements:
                                elements['password_entry'].configure(height=input_height, font=CTkFont(size=input_font_size))
                            if 'signin_btn' in elements:
                                elements['signin_btn'].configure(height=button_height, font=CTkFont(size=button_font_size, weight="bold"))
                            if 'link_btn' in elements:
                                elements['link_btn'].configure(font=CTkFont(size=link_font_size, weight="bold"))
                    except Exception:
                        pass
                    
                    # Update register form
                    try:
                        register_tab = self.tabview.tab("Sign Up")
                        if hasattr(register_tab, '_form_elements'):
                            elements = register_tab._form_elements
                            if 'title' in elements:
                                elements['title'].configure(font=CTkFont(size=title_font_size, weight="bold"))
                            # Update all labels
                            for key in elements.keys():
                                if key.endswith('_label'):
                                    elements[key].configure(font=CTkFont(size=label_font_size))
                                elif key.endswith('_entry'):
                                    elements[key].configure(height=input_height, font=CTkFont(size=input_font_size))
                                elif key.endswith('_btn'):
                                    btn_text = elements[key].cget("text")
                                    if btn_text in ["Register"]:
                                        elements[key].configure(height=button_height, font=CTkFont(size=button_font_size, weight="bold"))
                                    else:
                                        elements[key].configure(font=CTkFont(size=link_font_size, weight="bold"))
                    except Exception:
                        pass
                    
            except Exception:
                pass
        
        right_panel.bind("<Configure>", on_right_panel_resize)
        
        # Initial size update after panel is rendered
        right_panel.after(250, update_form_sizes)
        
    def create_tabs(self, parent):
        """Create tabbed interface for login and registration"""
        # Tab view - store reference
        self.tabview = ctk.CTkTabview(parent, fg_color="transparent")
        self.tabview.pack(fill="x", expand=False, padx=0, pady=20, anchor="w")  # anchor="w" aligns to left
        
        # Login tab
        login_tab = self.tabview.add("Sign In")
        login_tab.grid_columnconfigure(0, weight=1)
        self.create_login_form(login_tab)
        
        # Register tab
        register_tab = self.tabview.add("Sign Up")
        register_tab.grid_columnconfigure(0, weight=1)
        self.create_register_form(register_tab)
        
    def create_login_form(self, parent):
        """Create login form matching image design"""
        # Store references for responsive scaling
        if not hasattr(parent, '_form_elements'):
            parent._form_elements = {}
        
        # Title
        title_label = ctk.CTkLabel(
            parent,
            text="Sign in",
            font=CTkFont(size=24, weight="bold"),
            text_color="#3b82f6",
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(20, 40))
        parent._form_elements['title'] = title_label
        
        # Username/Email field
        email_frame = ctk.CTkFrame(parent, fg_color="transparent")
        email_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        email_frame.grid_columnconfigure(0, weight=1)
        
        email_label = ctk.CTkLabel(
            email_frame,
            text="Email",
            font=CTkFont(size=12),
            text_color="#6b7280",
            anchor="w"
        )
        email_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        parent._form_elements['email_label'] = email_label
        
        self.email_entry = ctk.CTkEntry(
            email_frame,
            placeholder_text="",
            height=35,
            border_width=1,
            corner_radius=5,
            fg_color="#ffffff",
            border_color="#d1d5db",
            font=CTkFont(size=14)
        )
        self.email_entry.grid(row=1, column=0, sticky="ew", pady=(0, 0))
        parent._form_elements['email_entry'] = self.email_entry
        
        # Bind focus events for better visibility
        def on_email_focus_in(event):
            self.email_entry.configure(border_color="#3b82f6")
        def on_email_focus_out(event):
            self.email_entry.configure(border_color="#d1d5db")
        self.email_entry.bind("<FocusIn>", on_email_focus_in)
        self.email_entry.bind("<FocusOut>", on_email_focus_out)
        
        # Password field
        password_frame = ctk.CTkFrame(parent, fg_color="transparent")
        password_frame.grid(row=2, column=0, sticky="ew", pady=(0, 30))
        password_frame.grid_columnconfigure(0, weight=1)
        
        password_label = ctk.CTkLabel(
            password_frame,
            text="Password",
            font=CTkFont(size=12),
            text_color="#6b7280",
            anchor="w"
        )
        password_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        parent._form_elements['password_label'] = password_label
        
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="",
            height=35,
            border_width=1,
            corner_radius=5,
            fg_color="#ffffff",
            border_color="#d1d5db",
            show="*",
            font=CTkFont(size=14)
        )
        self.password_entry.grid(row=1, column=0, sticky="ew", pady=(0, 0))
        parent._form_elements['password_entry'] = self.password_entry
        
        # Bind focus events for better visibility
        def on_password_focus_in(event):
            self.password_entry.configure(border_color="#3b82f6")
        def on_password_focus_out(event):
            self.password_entry.configure(border_color="#d1d5db")
        self.password_entry.bind("<FocusIn>", on_password_focus_in)
        self.password_entry.bind("<FocusOut>", on_password_focus_out)
        
        # Sign in button
        signin_btn = ctk.CTkButton(
            parent,
            text="Sign in",
            width=250,
            height=40,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            corner_radius=5,
            font=CTkFont(size=14, weight="bold"),
            command=self.handle_login
        )
    def create_login_form(self, parent):
        """Create login form matching image design"""
        # Store references for responsive scaling
        if not hasattr(parent, '_form_elements'):
            parent._form_elements = {}
        
        # Title
        title_label = ctk.CTkLabel(
            parent,
            text="Sign in",
            font=CTkFont(size=24, weight="bold"),
            text_color="#3b82f6",
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(20, 40))
        parent._form_elements['title'] = title_label
        
        # Username/Email field
        email_frame = ctk.CTkFrame(parent, fg_color="transparent")
        email_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        email_frame.grid_columnconfigure(0, weight=1)
        
        email_label = ctk.CTkLabel(
            email_frame,
            text="Email",
            font=CTkFont(size=12),
            text_color="#6b7280",
            anchor="w"
        )
        email_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        parent._form_elements['email_label'] = email_label
        
        self.email_entry = ctk.CTkEntry(
            email_frame,
            placeholder_text="",
            height=35,
            border_width=1,
            corner_radius=5,
            fg_color="#ffffff",
            border_color="#d1d5db",
            font=CTkFont(size=14)
        )
        self.email_entry.grid(row=1, column=0, sticky="ew", pady=(0, 0))
        parent._form_elements['email_entry'] = self.email_entry
        
        # Bind focus events for better visibility
        def on_email_focus_in(event):
            self.email_entry.configure(border_color="#3b82f6")
        def on_email_focus_out(event):
            self.email_entry.configure(border_color="#d1d5db")
        self.email_entry.bind("<FocusIn>", on_email_focus_in)
        self.email_entry.bind("<FocusOut>", on_email_focus_out)
        
        # Password field
        password_frame = ctk.CTkFrame(parent, fg_color="transparent")
        password_frame.grid(row=2, column=0, sticky="ew", pady=(0, 30))
        password_frame.grid_columnconfigure(0, weight=1)
        
        password_label = ctk.CTkLabel(
            password_frame,
            text="Password",
            font=CTkFont(size=12),
            text_color="#6b7280",
            anchor="w"
        )
        password_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        parent._form_elements['password_label'] = password_label
        
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="",
            height=35,
            border_width=1,
            corner_radius=5,
            fg_color="#ffffff",
            border_color="#d1d5db",
            show="*",
            font=CTkFont(size=14)
        )
        self.password_entry.grid(row=1, column=0, sticky="ew", pady=(0, 0))
        parent._form_elements['password_entry'] = self.password_entry
        
        # Bind focus events for better visibility
        def on_password_focus_in(event):
            self.password_entry.configure(border_color="#3b82f6")
        def on_password_focus_out(event):
            self.password_entry.configure(border_color="#d1d5db")
        self.password_entry.bind("<FocusIn>", on_password_focus_in)
        self.password_entry.bind("<FocusOut>", on_password_focus_out)
        
        # Sign in button
        signin_btn = ctk.CTkButton(
            parent,
            text="Sign in",
            width=250,
            height=40,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            corner_radius=5,
            font=CTkFont(size=14, weight="bold"),
            command=self.handle_login
        )
        signin_btn.grid(row=3, column=0, sticky="w", pady=(0, 20))  # sticky="w" aligns button to left
        parent._form_elements['signin_btn'] = signin_btn
        
        # Sign up link
        link_frame = ctk.CTkFrame(parent, fg_color="transparent")
        link_frame.grid(row=4, column=0, sticky="w")
        
        link_label = ctk.CTkLabel(
            link_frame,
            text="Don't have an account? ",
            font=CTkFont(size=12),
            text_color="#6b7280",
            anchor="w"
        )
        link_label.pack(side="left")
        
        link_btn = ctk.CTkButton(
            link_frame,
            text="Sign up",
            font=CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color="#f3f4f6",
            text_color="#3b82f6",
            anchor="w",
            command=self.switch_to_register
        )
        link_btn.pack(side="left")
        parent._form_elements['link_btn'] = link_btn
        
    def create_register_form(self, parent):
        """Create registration form matching image design"""
        # Store references for responsive scaling
        if not hasattr(parent, '_form_elements'):
            parent._form_elements = {}
        
        # Title
        title_label = ctk.CTkLabel(
            parent,
            text="Register",
            font=CTkFont(size=24, weight="bold"),
            text_color="#3b82f6",
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(20, 40))
        parent._form_elements['title'] = title_label
        
        # Fields based on role
        self.register_fields = {}
        row = 1
        
        # Common fields
        common_fields = [
            ("Full Name", "full_name"),
            ("College ID", "college_id"),
            ("Email", "email"),
            ("Password", "password")
        ]
        
        # Role-specific fields
        role_fields = {
            "guard": [],
            "member": [],
            "admin": []
        }
        
        all_fields = common_fields + role_fields.get(self.role, [])
        
        # Create form fields
        for field_label, field_key in all_fields:
            field_frame = ctk.CTkFrame(parent, fg_color="transparent")
            field_frame.grid(row=row, column=0, sticky="ew", pady=(0, 20))
            field_frame.grid_columnconfigure(0, weight=1)
            
            label = ctk.CTkLabel(
                field_frame,
                text=field_label,
                font=CTkFont(size=12),
                text_color="#6b7280",
                anchor="w"
            )
            label.grid(row=0, column=0, sticky="w", pady=(0, 5))
            parent._form_elements[f'{field_key}_label'] = label  # Store reference
            
            entry = ctk.CTkEntry(
                field_frame,
                placeholder_text="",
                height=35,
                border_width=1,
                corner_radius=5,
                fg_color="#ffffff",
                border_color="#d1d5db",
                show="*" if field_key == "password" else None,
                font=CTkFont(size=14)
            )
            entry.grid(row=1, column=0, sticky="ew", pady=(0, 0))
            parent._form_elements[f'{field_key}_entry'] = entry  # Store reference
            
            # Bind focus events for better visibility
            def on_focus_in(event, e=entry):
                e.configure(border_color="#3b82f6")
            def on_focus_out(event, e=entry):
                e.configure(border_color="#d1d5db")
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
            
            self.register_fields[field_key] = entry
            row += 1
        
        # Register button
        register_btn = ctk.CTkButton(
            parent,
            text="Register",
            width=250,
            height=40,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            corner_radius=5,
            font=CTkFont(size=14, weight="bold"),
            command=self.handle_register
        )
        register_btn.grid(row=row, column=0, sticky="w", pady=(10, 20))  # sticky="w" aligns button to left
        parent._form_elements['register_btn'] = register_btn
        
        # Sign in link
        link_frame = ctk.CTkFrame(parent, fg_color="transparent")
        link_frame.grid(row=row+1, column=0, sticky="w")
        
        link_label = ctk.CTkLabel(
            link_frame,
            text="Already have an account? ",
            font=CTkFont(size=12),
            text_color="#6b7280",
            anchor="w"
        )
        link_label.pack(side="left")
        
        link_btn = ctk.CTkButton(
            link_frame,
            text="Sign in",
            font=CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color="#f3f4f6",
            text_color="#3b82f6",
            anchor="w",
            command=self.switch_to_login
        )
        link_btn.pack(side="left")
        parent._form_elements['link_btn'] = link_btn
        
    def switch_to_register(self):
        """Switch to register tab"""
        self.tabview.set("Sign Up")
        
    def switch_to_login(self):
        """Switch to login tab"""
        self.tabview.set("Sign In")
        
    def handle_login(self):
        """Handle login submission"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showwarning("Input Required", "Please enter both email and password.")
            return
        
        try:
            user = self.auth_service.login(email, password)
            if not user:
                messagebox.showerror("Login Failed", "Invalid credentials")
                return
            
            # Check role match
            if self.role == "admin":
                admin_email = "ravi.abhinavyadav@gmail.com"
                if user["email"] != admin_email:
                    messagebox.showerror("Access Denied", 
                                       f"Admin access is restricted to {admin_email} only.")
                    return
                if user["role"] != "admin":
                    messagebox.showerror("Login Failed", "Invalid role for admin access")
                    return
            else:
                if user["role"] != self.role:
                    messagebox.showerror("Login Failed", "Invalid credentials or role mismatch")
                    return
            
            messagebox.showinfo("Success", f"Welcome {user['full_name']}")
            self.on_success(user)
            
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")
            
    def handle_register(self):
        """Handle registration submission"""
        # Get field values
        college_id_entry = self.register_fields.get("college_id")
        full_name_entry = self.register_fields.get("full_name")
        email_entry = self.register_fields.get("email")
        password_entry = self.register_fields.get("password")
        
        if not all([college_id_entry, full_name_entry, email_entry, password_entry]):
            messagebox.showwarning("Input Required", "Please fill in all fields.")
            return
        
        college_id = college_id_entry.get().strip()
        full_name = full_name_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get()
        
        # Validate
        if not all([college_id, full_name, email, password]):
            messagebox.showwarning("Input Required", "Please fill in all fields.")
            return
        
        # Check admin restriction
        if self.role == "admin":
            admin_email = "ravi.abhinavyadav@gmail.com"
            if email != admin_email:
                messagebox.showwarning("Admin Registration Restricted",
                                     f"Admin access is restricted to {admin_email} only.")
                return
        
        try:
            self.auth_service.register(college_id, full_name, email, password, self.role)
            messagebox.showinfo("Registered", "Registration successful. You can now login.")
            # Switch to login tab
            self.switch_to_login()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def destroy(self):
        """Clean up"""
        try:
            # Destroy all widgets properly
            if hasattr(self, 'main_frame'):
                self.main_frame.destroy()
        except Exception:
            pass

