import customtkinter as ctk

from services.auth_service import AuthService
from pages.auth_pages import AuthPage


class App(ctk.CTk):
    """Simplified application shell with landing, auth, and dashboard views."""

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Parking Management System")
        self.geometry("900x600")
        self.resizable(False, False)

        self.font_title = ctk.CTkFont(family="Inter", size=22, weight="bold")
        self.font_subtitle = ctk.CTkFont(family="Inter", size=16)
        self.font_box = ctk.CTkFont(family="Inter", size=16)
        self.font_footer = ctk.CTkFont(family="Inter", size=14)

        self.auth = AuthService()
        self.current_user = None
        self._selected_role = "member"

        self.container = ctk.CTkFrame(self, fg_color="#ffffff")
        self.container.pack(fill="both", expand=True)
        self.container.pack_propagate(False)

        self._mode = None
        self.auth_page: AuthPage | None = None
        self.landing_frame: ctk.CTkFrame | None = None
        self.dashboard_frame: ctk.CTkFrame | None = None

        self.show_landing()

    def clear(self) -> None:
        """Remove any existing view widgets."""
        if self.auth_page is not None:
            try:
                self.auth_page.destroy()
            except Exception:
                pass
            self.auth_page = None

        for child in list(self.container.winfo_children()):
            try:
                child.destroy()
            except Exception:
                pass

        self.landing_frame = None
        self.dashboard_frame = None

    def show_landing(self) -> None:
        """Render the landing screen matching the provided layout."""
        self.clear()
        self._mode = "landing"

        frame = ctk.CTkFrame(self.container, fg_color="#ffffff", width=800, height=500)
        frame.pack(fill="both", expand=True)
        frame.pack_propagate(False)

        title_box = ctk.CTkFrame(frame, fg_color="#ffffff", width=770, height=60)
        title_box.place(x=35, y=30)

        title_label = ctk.CTkLabel(
            frame,
            text="Welcome To Vehicle Parking Management System",
            font=self.font_title,
            text_color="#000000",
            width=730,
            height=35,
        )
        title_label.place(x=80, y=34)

        subtitle_label = ctk.CTkLabel(
            frame,
            text="Choose Your Role",
            font=self.font_subtitle,
            text_color="#000000",
            width=375,
            height=30,
        )
        subtitle_label.place(x=230, y=111)

        self._create_role_box(
            frame,
            role="member",
            box_coords=(65, 210, 210, 128),
            label_coords=(80, 258, 156, 43),
            text="Campus Student",
        )
        self._create_role_box(
            frame,
            role="guard",
            box_coords=(323, 211, 210, 128),
            label_coords=(338, 258, 156, 43),
            text="Security Guard",
        )
        self._create_role_box(
            frame,
            role="admin",
            box_coords=(567, 211, 245, 128),
            label_coords=(582, 258, 211, 43),
            text="Campus Management",
        )

        footer_label = ctk.CTkLabel(
            frame,
            text="@ 2025 Central Michigan University, All rights are reserved",
            font=self.font_footer,
            text_color="#999999",
            width=560,
            height=40,
        )
        footer_label.place(x=180, y=430)

        self.landing_frame = frame

    def _create_role_box(
        self,
        parent: ctk.CTkFrame,
        *,
        role: str,
        box_coords: tuple[int, int, int, int],
        label_coords: tuple[int, int, int, int],
        text: str,
    ) -> None:
        box_x, box_y, box_w, box_h = box_coords
        label_x, label_y, label_w, label_h = label_coords

        box = ctk.CTkFrame(
            parent,
            fg_color="#1647E8",
            corner_radius=4,
            width=box_w,
            height=box_h,
            border_width=3,
            border_color="#000000",
        )
        box.place(x=box_x, y=box_y)

        label = ctk.CTkLabel(
            box,
            text=text,
            font=self.font_box,
            text_color="#ffffff",
            width=label_w,
            height=label_h,
        )
        label.place(relx=0.5, rely=0.5, anchor="center")

        def _handle_click(_event=None) -> None:
            self.show_auth(role)

        def _on_enter(_event=None) -> None:
            box.configure(fg_color="#1d5bff")
            label.configure(text_color="#ffffff")

        def _on_leave(_event=None) -> None:
            box.configure(fg_color="#1647E8")
            label.configure(text_color="#ffffff")

        for widget in (box, label):
            widget.bind("<Button-1>", _handle_click)
            widget.bind("<Enter>", _on_enter)
            widget.bind("<Leave>", _on_leave)

    def show_auth(self, role: str | None = None) -> None:
        """Render the authentication view."""
        self.clear()
        self._mode = "auth"

        selected_role = role or self._selected_role or "member"
        self._selected_role = selected_role

        self.auth_page = AuthPage(
            parent=self.container,
            role=selected_role,
            auth_service=self.auth,
            on_back=self.show_landing,
            on_success=self.handle_auth_success,
        )

    def handle_auth_success(self, user: dict) -> None:
        """Persist authenticated user and open dashboard."""
        self.current_user = user
        self.show_dashboard()

    def show_dashboard(self) -> None:
        """Render the role specific dashboard page."""
        from pages import campus_member, security_guard, campus_management

        self.clear()
        self._mode = "dashboard"

        role = (self.current_user or {}).get("role", "member")

        renderers = {
            "member": campus_member.render,
            "guard": security_guard.render,
            "admin": campus_management.render,
        }

        renderer = renderers.get(role)
        if renderer is None:
            renderer = campus_member.render

        self.dashboard_frame = renderer(
            parent=self.container,
            user=self.current_user,
            on_logout=self.logout,
        )

    def logout(self) -> None:
        """Return to landing view and clear user state."""
        self.current_user = None
        self.show_landing()


if __name__ == "__main__":
    app = App()
    app.mainloop()


