# Main application entry point
import customtkinter as ctk
from services.auth_service import AuthService
from pages.auth_pages import AuthPage

class App(ctk.CTk):
    # Initializing the main application window
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("light")
        self.title("Parking Management System")
        self.geometry("900x600")
        self.resizable(False, False)
        self.font_title = ctk.CTkFont(family="Inter", size=22, weight="bold")
        self.font_subtitle = ctk.CTkFont(family="Inter", size=16)
        self.font_bx = ctk.CTkFont(family="Inter", size=16)
        self.font_footer = ctk.CTkFont(family="Inter", size=14)
        self.auth = AuthService()
        self.current_user = None 
        self._selected_role = "member"
        self.container = ctk.CTkFrame(self, fg_color="#ffffff")
        self.container.pack(fill="both", expand=True)
        self.container.pack_propagate(False)
        self._mode = None
        self.auth_page: AuthPage | None = None
        self.landing_fm: ctk.CTkFrame | None = None  
        self.dashboard_fm: ctk.CTkFrame | None = None 
        self.show_landing()

    # Clearing all current views and widgets
    def clear(self) -> None:
        if self.auth_page is not None:
            if hasattr(self.auth_page, 'destroy'):
                self.auth_page.destroy()
            self.auth_page = None
        for child in list(self.container.winfo_children()):
            if hasattr(child, 'destroy'):
                child.destroy()
        self.landing_fm = None
        self.dashboard_fm = None

    # Displaying the landing page with role selection
    def show_landing(self) -> None:
        self.clear()
        self._mode = "landing"
        fm = ctk.CTkFrame(self.container, fg_color="#ffffff", width=800, height=500)
        fm.pack(fill="both", expand=True)
        fm.pack_propagate(False)
        title_bx = ctk.CTkFrame(fm, fg_color="#ffffff", width=770, height=60)
        title_bx.place(x=35, y=30)
        title_label = ctk.CTkLabel(fm, text="Welcome To Vehicle Parking Management System", font=self.font_title, text_color="#000000", width=730, height=35)
        title_label.place(x=80, y=34)
        subtitle_lbl = ctk.CTkLabel(fm, text="Choose Your Role", font=self.font_subtitle, text_color="#000000", width=375, height=30)
        subtitle_lbl.place(x=230, y=111)
        self._mk_role_bx(fm, role="member", bx_cords=(65, 210, 210, 128), lbl_cords=(80, 258, 156, 43), text="Campus Student")
        self._mk_role_bx(fm, role="guard", bx_cords=(323, 211, 210, 128), lbl_cords=(338, 258, 156, 43), text="Security Guard")
        self._mk_role_bx(fm, role="admin", bx_cords=(567, 211, 245, 128), lbl_cords=(582, 258, 211, 43), text="Campus Management")
        foot_lbl = ctk.CTkLabel(fm, text="@ 2025 Central Michigan University, All rights are reserved", font=self.font_footer, text_color="#999999", width=560, height=40)
        foot_lbl.place(x=180, y=430)
        self.landing_fm = fm
    
    # Creating role selection boxes with hover effects
    def _mk_role_bx(self, parent: ctk.CTkFrame, *, role: str, bx_cords: tuple[int, int, int, int], lbl_cords: tuple[int, int, int, int], text: str) -> None:
        bx_x, bx_y, bx_w, bx_h = bx_cords
        lbl_x, lbl_y, lbl_w, lbl_h = lbl_cords
        bx = ctk.CTkFrame(parent, fg_color="#1647E8", corner_radius=18, width=bx_w, height=bx_h, border_width=1, border_color="#000000")
        bx.place(x=bx_x, y=bx_y)
        lbl = ctk.CTkLabel(bx, text=text, font=self.font_bx, text_color="#ffffff", width=lbl_w, height=lbl_h)
        lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Handling the click events for the role selection boxes
        def _handle_clk(_event=None) -> None:
            self.show_auth(role)

        # Changing the box color hover effect
        def _on_enter(_event=None) -> None:
            bx.configure(fg_color="#1d5bff")
            lbl.configure(text_color="#ffffff")
        # Restting the box color to normal
        def _on_exit(_event=None) -> None:
            bx.configure(fg_color="#1647E8")
            lbl.configure(text_color="#ffffff")
        for widget in (bx, lbl):
            widget.bind("<Button-1>", _handle_clk)
            widget.bind("<Enter>", _on_enter)
            widget.bind("<Leave>", _on_exit)

    # Showing the authentication page based onthe selected role
    def show_auth(self, role: str | None = None) -> None:
        self.clear()
        self._mode = "auth"
        selected_role = role or self._selected_role or "member"
        self._selected_role = selected_role
        self.auth_page = AuthPage(
            parent=self.container,
            role=selected_role,
            auth_service=self.auth,
            on_back=self.show_landing,    
            on_success=self.on_auth_success
        )
    # When the user succesfully logs in, redirects to the dashboard
    def on_auth_success(self, user: dict) -> None:
        self.current_user = user
        self.show_dashboard()

    # Showing the dashboard based on the user role
    def show_dashboard(self) -> None:
        from pages import campus_student, security_guard, campus_management
        self.clear()
        self._mode = "dashboard"
        role = (self.current_user or {}).get("role", "member")
        render_map = {
            "member": campus_student.render_student_vw, 
            "guard": security_guard.render,            
            "admin": campus_management.render}
        render_func = render_map.get(role)
        if render_func is None:
            render_func = campus_student.render_student_vw

        self.dashboard_fm = render_func(
            parent=self.container,
            user=self.current_user,
            on_logout=self.logout)
    
    # When the user logs out, redirects to the landing page
    def logout(self) -> None:
        self.current_user = None
        self.show_landing()

# Starting the application
if __name__ == "__main__":
    app = App()
    app.mainloop()


