import customtkinter as ctk
from customtkinter import CTkFont
from tkinter import messagebox

HEADER_COLOR = "#1e3a8a"  
REGISTER_ACTIVE = "#f59e0b"  
TOGGLE_INACTIVE_FG = "#ffffff"  
TOGGLE_INACTIVE_BORDER = "#d1d5db"  
PRIMARY_GREEN = "#10b981"  

class AuthPage:
    def __init__(self, parent, role, auth_service, on_back, on_success):
        self.parent = parent
        self.role = (role or "member").lower()
        self.auth_service = auth_service
        self.on_back = on_back
        self.on_success = on_success
        self.role_display = {"member": "Campus Student", "guard": "Security Guard", "admin": "Campus Management"}.get(self.role, self.role.title())
        self.main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        card = ctk.CTkFrame(self.main_frame, fg_color="#ffffff", corner_radius=10)
        card.pack(expand=True, pady=20, padx=20)
        card.grid_columnconfigure(0, weight=1)
        self.card = card
        header_bar = ctk.CTkFrame(card, fg_color=HEADER_COLOR, corner_radius=8)
        header_bar.pack(fill="x", padx=22, pady=(22, 28))
        ctk.CTkLabel(header_bar,text=f"Welcome {self.role_display}",font=CTkFont(size=22, weight="bold"),text_color="#ffffff",).pack(pady=12)
        toggles = ctk.CTkFrame(card, fg_color="transparent")
        toggles.pack(pady=(0, 18))
        self.register_button = ctk.CTkButton(toggles, text="Register", width=140, height=40, corner_radius=6, command=lambda: self._show_view("register"))
        self.register_button.grid(row=0, column=0, padx=(0, 4))
        self.login_button = ctk.CTkButton(toggles, text="Login", width=140, height=40, corner_radius=6, fg_color=TOGGLE_INACTIVE_FG, text_color="#111827", hover_color="#f3f4f6", border_width=1, border_color=TOGGLE_INACTIVE_BORDER, command=lambda: self._show_view("login"))
        self.login_button.grid(row=0, column=1, padx=(4, 0))
        self.views = {"register": self._build_register_view(card), "login": self._build_login_view(card)}
        self.current_view: str | None = None
        toolbar = ctk.CTkFrame(card, fg_color="transparent")
        toolbar.pack(fill="x", padx=22, pady=(0, 8))
        ctk.CTkButton(toolbar,text="← Back",width=80, height=28, fg_color="transparent", hover_color="#f3f4f6", text_color="#374151", font=CTkFont(size=12), command=self.on_back).pack(anchor="w")
        self._show_view("register")
 
    # Building the Registration form
    def _build_register_view(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        fm = ctk.CTkFrame(parent, fg_color="transparent")
        fm.grid_columnconfigure(1, weight=1)
        fields = [
            ("Full Name", "register_full_name_entry"),
            ("College ID", "register_college_id_entry"),
            ("Email", "register_email_entry"),
            ("Password", "register_password_entry"),]
        for idx, (label_text, attr_name) in enumerate(fields):
            ctk.CTkLabel(fm, text=label_text, font=CTkFont(size=14), text_color="#111827").grid(row=idx, column=0, sticky="e", padx=(22, 18), pady=8)
            entry = ctk.CTkEntry(fm, height=36, width=270, show="*" if "password" in attr_name else "")
            entry.grid(row=idx, column=1, sticky="w", pady=8)
            setattr(self, attr_name, entry)
        submit = ctk.CTkButton(fm, text="Click To Register", fg_color=PRIMARY_GREEN, hover_color="#0f9a74", font=CTkFont(size=14, weight="bold"), height=42, width=260, command=self.handle_register)
        submit.grid(row=len(fields), column=0, columnspan=2, pady=(24, 12))
        return fm
    
    # Building the Login form
    def _build_login_view(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        fm = ctk.CTkFrame(parent, fg_color="transparent")
        fm.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(fm, text="Email", font=CTkFont(size=14), text_color="#111827").grid(row=0, column=0, sticky="e", padx=(22, 18), pady=8)
        self.login_email_entry = ctk.CTkEntry(fm, height=36, width=270)
        self.login_email_entry.grid(row=0, column=1, sticky="w", pady=8)
        ctk.CTkLabel(fm, text="Password", font=CTkFont(size=14), text_color="#111827").grid(row=1, column=0, sticky="e", padx=(22, 18), pady=8)
        self.login_password_entry = ctk.CTkEntry(fm, height=36, width=270, show="*")
        self.login_password_entry.grid(row=1, column=1, sticky="w", pady=8)
        submit = ctk.CTkButton(fm, text="Click To Login", fg_color=PRIMARY_GREEN, hover_color="#0f9a74", font=CTkFont(size=14, weight="bold"), height=42, width=260, command=self.handle_login)
        submit.grid(row=2, column=0, columnspan=2, pady=(24, 12))
        return fm

    # Showing the selected view
    def _show_view(self, view: str) -> None:
        if self.current_view == view:
            return
        if self.current_view:
            self.views[self.current_view].pack_forget()
        self.views[view].pack(fill="x", padx=22, pady=4)
        self.current_view = view
        self._update_toggle_styles()

    # Updating the button styles to highlight
    def _update_toggle_styles(self) -> None:
        register_active = self.current_view == "register"
        if register_active:
            self.register_button.configure(fg_color=REGISTER_ACTIVE, hover_color="#e08e0a", text_color="#ffffff", border_width=0)
            self.login_button.configure(fg_color=TOGGLE_INACTIVE_FG, text_color="#111827", hover_color="#f3f4f6", border_width=1, border_color=TOGGLE_INACTIVE_BORDER)
        else:
            self.login_button.configure(fg_color=REGISTER_ACTIVE, hover_color="#e08e0a", text_color="#ffffff", border_width=0)
            self.register_button.configure(fg_color=TOGGLE_INACTIVE_FG, text_color="#111827", hover_color="#f3f4f6", border_width=1, border_color=TOGGLE_INACTIVE_BORDER)

    # switching the view to register
    def switch_to_register(self):
        self._show_view("register")

    # switching the view to login
    def switch_to_login(self):
        self._show_view("login")

    # handling the logn process
    def handle_login(self):
        email = self.login_email_entry.get().strip()
        password = self.login_password_entry.get()
        if not email or not password:
            messagebox.showwarning("Input Required", "Please enter both email and password.")
            return
        user = self.auth_service.login(email, password)
        if user is None:
            messagebox.showerror("Login Failed", "Invalid credentials")
            return
        if user.get("role") != self.role:
            messagebox.showerror("Role Mismatch","Please use the correct portal for your role.")
            return
        messagebox.showinfo("Success", f"Welcome {user['full_name']}")
        self.on_success(user)
    
    # handling the regsitration process
    def handle_register(self):
        full_name = getattr(self, "register_full_name_entry", None)
        college_id = getattr(self, "register_college_id_entry", None)
        email_entry = getattr(self, "register_email_entry", None)
        password_entry = getattr(self, "register_password_entry", None)

        full_name_val = full_name.get().strip() if full_name else ""
        college_id_val = college_id.get().strip() if college_id else ""
        email_val = email_entry.get().strip() if email_entry else ""
        password_val = password_entry.get() if password_entry else ""

        if not all([full_name_val, college_id_val, email_val, password_val]):
            messagebox.showwarning("Input Required", "Please fill in all fields.")
            return

        self.auth_service.register(college_id_val, full_name_val, email_val, password_val, self.role)
        messagebox.showinfo("Registered", "Registration successful. You can now sign in.")
        self.switch_to_login()
    
    # destroying the auth page
    def destroy(self):
        if hasattr(self.main_frame, 'destroy'):
            self.main_frame.destroy()




