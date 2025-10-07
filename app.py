import tkinter as tk
from tkinter import ttk, messagebox
from services.auth_service import AuthService
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps
import os


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Parking Management System")
        self.geometry("900x640")
        self.resizable(True, True)

        # Theming and subtle glass-like styling
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        default_font = ("Segoe UI", 11)
        header_font = ("Segoe UI Semibold", 12)
        button_font = ("Segoe UI", 11)
        self.option_add("*Font", default_font)

        style.configure("Glass.TLabelframe", padding=24)
        style.configure("Glass.TLabelframe.Label", font=header_font)
        style.configure("Role.TButton", padding=(18, 10), font=button_font)
        style.map(
            "Role.TButton",
            relief=[("pressed", "sunken"), ("active", "raised")],
        )

        self.auth = AuthService()
        self.current_user = None

        # Resolve assets directory relative to this file
        self._base_dir = os.path.dirname(os.path.abspath(__file__))
        self._assets_dir = os.path.join(self._base_dir, "assets")

        # Background image canvas
        self.bg = tk.Canvas(self, highlightthickness=0, bd=0)
        self.bg.pack(fill=tk.BOTH, expand=True)
        self._bg_src = None
        self._bg_img = None
        self._bg_item = None
        self._render_background()
        self.bind("<Configure>", self._on_resize)

        self.container = ttk.Frame(self.bg)
        self.container.place(relx=0.5, rely=0.10, anchor="n")

        # Landing drawing state
        self._landing_items = []
        self._landing_roles = []
        self._mode = "landing"  # 'landing' or 'auth'

        self.show_landing()

    def clear(self):
        for child in self.container.winfo_children():
            child.destroy()
        # Also clear any landing grid placed on the background canvas
        if hasattr(self, "_landing_grid") and self._landing_grid is not None:
            try:
                self._landing_grid.destroy()
            except Exception:
                pass
            self._landing_grid = None
        # Clear canvas drawn landing artifacts
        if hasattr(self, "_landing_items") and self._landing_items:
            for item in self._landing_items:
                try:
                    self.bg.delete(item)
                except Exception:
                    pass
            self._landing_items = []

    def show_landing(self):
        self.clear()
        self._mode = "landing"
        # Hide auth container while on landing
        try:
            self.container.place_forget()
        except Exception:
            pass
        # Data used for landing draw
        self._landing_roles = [
            ("Security Guard", "guard", os.path.join(self._assets_dir, "security_guard-removebg-preview.png")),
            ("Campus Student", "member", os.path.join(self._assets_dir, "student-removebg-preview.png")),
            ("Campus Management", "admin", os.path.join(self._assets_dir, "management-removebg-preview.png")),
        ]
        self._draw_landing()

    def show_auth(self, role):
        self.clear()
        self._mode = "auth"
        # Ensure landing will not redraw while in auth
        self._landing_roles = []
        # Show container for auth
        self.container.place(relx=0.5, rely=0.10, anchor="n")
        display_role = {
            "guard": "Security Guard",
            "member": "Campus Student",
            "admin": "Campus Management",
        }.get(role, role.title())

        # Build a tidy auth layout with only the selected role image at the top
        card = ttk.Frame(self.container)
        card.grid(row=0, column=0, padx=24, pady=12)

        # Back button
        back_bar = ttk.Frame(card)
        back_bar.grid(row=0, column=0, sticky="w")
        ttk.Button(back_bar, text="← Back", command=self.show_landing).pack(pady=(0, 4))

        # Role image header
        img_path = {
            "guard": os.path.join(self._assets_dir, "security_guard-removebg-preview.png"),
            "member": os.path.join(self._assets_dir, "student-removebg-preview.png"),
            "admin": os.path.join(self._assets_dir, "management-removebg-preview.png"),
        }.get(role, "")
        self._auth_role_img = self._load_role_image(img_path, size=(140, 140))
        img_lbl = tk.Label(card, image=self._auth_role_img, bd=0, highlightthickness=0)
        img_lbl.grid(row=1, column=0, pady=(4, 6))

        title = ttk.Label(card, text=f"{display_role} - Login / Register")
        title.configure(font=("Segoe UI Semibold", 13))
        title.grid(row=2, column=0, pady=(0, 8))

        # Form container with notebook
        form_wrap = ttk.Frame(card)
        form_wrap.grid(row=3, column=0)
        nb = ttk.Notebook(form_wrap)
        nb.pack(fill=tk.BOTH, expand=True)

        login_frame = ttk.Frame(nb)
        register_frame = ttk.Frame(nb)
        nb.add(login_frame, text="Login")
        nb.add(register_frame, text="Register")

        # Login tab
        ttk.Label(login_frame, text="Email").grid(row=0, column=0, sticky=tk.W, padx=8, pady=8)
        email_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=email_var, width=32).grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(login_frame, text="Password").grid(row=1, column=0, sticky=tk.W, padx=8, pady=8)
        password_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=password_var, show="*", width=32).grid(row=1, column=1, padx=8, pady=8)

        def on_login():
            user = self.auth.login(email_var.get().strip(), password_var.get())
            if not user or user["role"] != role:
                messagebox.showerror("Login failed", "Invalid credentials or role mismatch")
                return
            self.current_user = user
            messagebox.showinfo("Success", f"Welcome {user['full_name']}")
            # Next: route to role dashboard (placeholder)
            self.show_landing()

        ttk.Button(login_frame, text="Login", style="Role.TButton", command=on_login).grid(row=2, column=0, columnspan=2, pady=12)

        # Register tab
        reg_fields = {
            "College ID": tk.StringVar(),
            "Full Name": tk.StringVar(),
            "Email": tk.StringVar(),
            "Password": tk.StringVar(),
        }

        for i, (label, var) in enumerate(reg_fields.items()):
            ttk.Label(register_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=8, pady=8)
            show = "*" if label == "Password" else None
            ttk.Entry(register_frame, textvariable=var, show=show, width=32).grid(row=i, column=1, padx=8, pady=8)

        def on_register():
            try:
                self.auth.register(
                    reg_fields["College ID"].get().strip(),
                    reg_fields["Full Name"].get().strip(),
                    reg_fields["Email"].get().strip(),
                    reg_fields["Password"].get(),
                    role,
                )
                messagebox.showinfo("Registered", "Registration successful. You can now login.")
                nb.select(0)
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(register_frame, text="Register", style="Role.TButton", command=on_register).grid(row=len(reg_fields), column=0, columnspan=2, pady=12)

    def _render_background(self):
        w = max(self.winfo_width(), 1)
        h = max(self.winfo_height(), 1)
        if w < 10 or h < 10:
            # window not fully initialized yet
            self.after(50, self._render_background)
            return
        self.bg.config(width=w, height=h)
        try:
            if self._bg_src is None:
                bg_path = os.path.join(self._assets_dir, "college_background.jpg")
                self._bg_src = Image.open(bg_path).convert("RGB")
            # Fit image to canvas while preserving aspect ratio (cover)
            fitted = ImageOps.fit(self._bg_src, (w, h), Image.LANCZOS)
            fitted = fitted.filter(ImageFilter.GaussianBlur(radius=1.8))
            fitted = ImageEnhance.Brightness(fitted).enhance(1.06)
            self._bg_img = ImageTk.PhotoImage(fitted)
            if self._bg_item is None:
                self._bg_item = self.bg.create_image(0, 0, image=self._bg_img, anchor="nw")
            else:
                self.bg.itemconfig(self._bg_item, image=self._bg_img)
        except Exception:
            # fallback to flat color if image missing
            self.bg.delete("all")
            self._bg_item = None
            self.bg.create_rectangle(0, 0, w, h, fill="#e9effa", outline="")
        # Fade-in window
        try:
            self.attributes("-alpha", 0.0)
            def fade():
                alpha = float(self.attributes("-alpha"))
                if alpha < 1.0:
                    alpha = min(1.0, alpha + 0.07)
                    self.attributes("-alpha", alpha)
                    self.after(25, fade)
            fade()
        except Exception:
            pass

    def _load_role_image(self, path: str, size=(180, 180)):
        try:
            img = Image.open(path).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            print(f"[UI] Role image missing or failed to load: {path}")
            # Placeholder if missing
            ph = Image.new("RGBA", size, (255, 255, 255, 0))
            return ImageTk.PhotoImage(ph)

    def _on_resize(self, _event):
        # Throttle re-render to avoid excessive processing
        if hasattr(self, "_resize_job") and self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(60, self._render_background)
        # Keep landing centered on resize only in landing mode
        if self._mode == "landing" and hasattr(self, "_landing_roles") and self._landing_roles:
            if hasattr(self, "_relayout_job") and self._relayout_job:
                self.after_cancel(self._relayout_job)
            self._relayout_job = self.after(80, self._draw_landing)

    def _draw_landing(self):
        # Remove previous landing items
        if hasattr(self, "_landing_items") and self._landing_items:
            for item in self._landing_items:
                try:
                    self.bg.delete(item)
                except Exception:
                    pass
        self._landing_items = []

        w = max(self.winfo_width(), 1)
        h = max(self.winfo_height(), 1)
        cx = w // 2

        # Title and subtitle on transparent background
        title_id = self.bg.create_text(
            cx,
            int(h * 0.13),
            text="Welcome to Michigan Vehicle Parking Management System",
            font=("Segoe UI Semibold", 16),
            fill="#0f1b2d",
        )
        # Glassy strip behind title
        t_bbox = self.bg.bbox(title_id)
        if t_bbox:
            pad_x, pad_y = 16, 8
            rect_t = self.bg.create_rectangle(
                t_bbox[0] - pad_x,
                t_bbox[1] - pad_y,
                t_bbox[2] + pad_x,
                t_bbox[3] + pad_y,
                fill="#ffffff",
                outline="",
                stipple="gray25",
            )
            self.bg.tag_lower(rect_t, title_id)
            self._landing_items.append(rect_t)

        subtitle_id = self.bg.create_text(
            cx,
            int(h * 0.18),
            text="Choose your role",
            font=("Segoe UI", 11),
            fill="#27364a",
        )
        s_bbox = self.bg.bbox(subtitle_id)
        if s_bbox:
            pad_x, pad_y = 12, 6
            rect_s = self.bg.create_rectangle(
                s_bbox[0] - pad_x,
                s_bbox[1] - pad_y,
                s_bbox[2] + pad_x,
                s_bbox[3] + pad_y,
                fill="#ffffff",
                outline="",
                stipple="gray25",
            )
            self.bg.tag_lower(rect_s, subtitle_id)
            self._landing_items.append(rect_s)
        self._landing_items.extend([title_id, subtitle_id])

        # Draw role images centered horizontally
        tile_w, tile_h = 200, 200
        spacing = 48
        total_w = tile_w * 3 + spacing * 2
        start_x = cx - total_w // 2 + tile_w // 2
        y_top = int(h * 0.26)

        # Keep references to PhotoImages
        self._role_images = []
        for idx, (label, role, path) in enumerate(self._landing_roles):
            x = start_x + idx * (tile_w + spacing)
            img = self._load_role_image(path, size=(tile_w, tile_h))
            self._role_images.append(img)
            tag_img = f"role_img_{role}"
            tag_txt = f"role_txt_{role}"
            iid = self.bg.create_image(x, y_top + tile_h // 2, image=img, tags=(tag_img,))
            tid = self.bg.create_text(x, y_top + tile_h + 24, text=label, font=("Segoe UI", 10))
            # Glass strip behind role label
            lb = self.bg.bbox(tid)
            if lb:
                pad_x, pad_y = 10, 5
                rect_l = self.bg.create_rectangle(
                    lb[0] - pad_x,
                    lb[1] - pad_y,
                    lb[2] + pad_x,
                    lb[3] + pad_y,
                    fill="#ffffff",
                    outline="",
                    stipple="gray25",
                )
                self.bg.tag_lower(rect_l, tid)
                self._landing_items.append(rect_l)
            self._landing_items.extend([iid, tid])

            def _click(_e=None, r=role):
                self.show_auth(r)

            self.bg.tag_bind(tag_img, "<Button-1>", _click)
            self.bg.tag_bind(tag_txt, "<Button-1>", _click)


if __name__ == "__main__":
    app = App()
    app.mainloop()


