"""Campus member dashboard view."""

from __future__ import annotations
from datetime import datetime
from typing import Any
import customtkinter as ctk
from services.member_service import MemberService

_member_service = MemberService()

def render(parent, user=None, on_logout=None):
    """Render the campus member dashboard page."""
    root = ctk.CTkFrame(parent, fg_color="#f5f7ff")
    root.pack(fill="both", expand=True)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    sidebar = _build_sidebar(root, on_logout)
    sidebar.grid(row=0, column=0, sticky="nsw")

    content = ctk.CTkFrame(root, fg_color="#ffffff")
    content.grid(row=0, column=1, sticky="nsew")
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(0, weight=1)

    views = {
        "dashboard": _build_dashboard_view(content, user),
        "slots": _build_placeholder_view(content, "My Slots"),
        "profile": _build_placeholder_view(content, "Profile"),
    }

    def set_view(view: str) -> None:
        for child in views.values():
            child.grid_remove()
        views[view].grid(row=0, column=0, sticky="nsew")
        sidebar.update_selection(view)

    sidebar.configure_navigator(set_view)
    set_view("dashboard")
    return root


def _build_sidebar(parent, on_logout) -> ctk.CTkFrame:
    sidebar = ctk.CTkFrame(parent, fg_color="#e5edff", width=180)
    sidebar.grid_propagate(False)
    sidebar.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0)
    sidebar.grid_rowconfigure(7, weight=1)

    nav_title_font = ctk.CTkFont(family="Inter", size=16, weight="bold")
    nav_font = ctk.CTkFont(family="Inter", size=15)

    ctk.CTkLabel(
        sidebar,
        text="",
        width=1,
        height=20,
        fg_color="transparent",
    ).grid(row=0, column=0, pady=(20, 10))

    nav_buttons: dict[str, ctk.CTkButton] = {}

    def _make_button(text: str, view_name: str, row_index: int, primary: bool = False) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            sidebar,
            text=text,
            width=140,
            height=46,
            fg_color="#ffffff" if primary else "transparent",
            hover_color="#f3f4ff" if primary else "#dbe4ff",
            text_color="#2563eb" if primary else "#111827",
            font=nav_title_font if primary else nav_font,
            corner_radius=18,
        )
        btn.grid(row=row_index, column=0, padx=20, pady=6)
        nav_buttons[view_name] = btn
        return btn

    _make_button("Dashboard", "dashboard", 1, primary=True)
    _make_button("My Slots", "slots", 2)
    _make_button("Profile", "profile", 3)

    if on_logout is not None:
        ctk.CTkButton(
            sidebar,
            text="Logout",
            width=140,
            height=40,
            fg_color="transparent",
            hover_color="#fee2e2",
            text_color="#2563eb",
            font=nav_title_font,
            corner_radius=18,
            command=on_logout,
        ).grid(row=7, column=0, padx=20, pady=24, sticky="s")

    def update_selection(view: str) -> None:
        for key, btn in nav_buttons.items():
            primary = key == view
            btn.configure(
                fg_color="#ffffff" if primary else "transparent",
                text_color="#2563eb" if primary else "#111827",
            )

    def configure_navigator(callback):
        for name, btn in nav_buttons.items():
            btn.configure(command=lambda v=name: callback(v))

    sidebar.configure_navigator = configure_navigator  # type: ignore[attr-defined]
    sidebar.update_selection = update_selection  # type: ignore[attr-defined]
    update_selection("dashboard")

    return sidebar


def _build_dashboard_view(parent: ctk.CTkFrame, user: dict | None) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(parent, fg_color="#ffffff")
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=1)

    header_fonts = {
        "title": ctk.CTkFont(family="Inter", size=26, weight="bold"),
        "subtitle": ctk.CTkFont(family="Inter", size=16, weight="bold"),
        "meta": ctk.CTkFont(family="Inter", size=13),
    }

    user_name = (user or {}).get("full_name", "Member")

    header = ctk.CTkFrame(frame, fg_color="#ffffff")
    header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
    header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        header,
        text=f"Welcome {user_name}",
        font=header_fonts["title"],
        text_color="#111827",
    ).grid(row=0, column=0, sticky="w")

    datetime_frame = ctk.CTkFrame(header, fg_color="#ffffff")
    datetime_frame.grid(row=0, column=1, sticky="e", padx=(12, 0))

    ctk.CTkLabel(
        datetime_frame,
        text="Date :",
        font=header_fonts["meta"],
        text_color="#1f2937",
    ).pack(side="left", padx=(0, 6))
    date_label = _info_pill(datetime_frame, header_fonts["meta"], width=140)

    ctk.CTkLabel(
        datetime_frame,
        text="Time :",
        font=header_fonts["meta"],
        text_color="#1f2937",
    ).pack(side="left", padx=(12, 6))
    time_label = _info_pill(datetime_frame, header_fonts["meta"], width=140)

    body = ctk.CTkFrame(frame, fg_color="#ffffff")
    body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    body.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        body,
        text="Manage Your Parking and Profile",
        font=header_fonts["subtitle"],
        text_color="#1f2937",
    ).grid(row=0, column=0, sticky="w", pady=(0, 16))

    snapshot = _load_snapshot(user)

    metrics_grid = ctk.CTkFrame(body, fg_color="#ffffff")
    metrics_grid.grid(row=1, column=0, sticky="ew")
    for col in range(3):
        metrics_grid.grid_columnconfigure(col, weight=1)

    _metric_card(
        metrics_grid,
        row=0,
        column=0,
        title="Registered Vehicles",
        value=str(snapshot.get("registered_count", 0)),
        bg="#e7f1ff",
    )

    verification_status = snapshot.get("verification_status", "pending").title()
    verification_bg = {
        "Approved": "#c4f5cb",
        "Rejected": "#fecaca",
        "Pending": "#fef08a",
    }.get(verification_status, "#fef08a")

    _metric_card(
        metrics_grid,
        row=0,
        column=1,
        title="Verification Status",
        value=verification_status,
        bg=verification_bg,
    )

    _metric_card(
        metrics_grid,
        row=0,
        column=2,
        title="Current Status",
        value=snapshot.get("parking_status", "Not Parked"),
        bg="#e7f1ff",
    )

    status_grid = ctk.CTkFrame(body, fg_color="#ffffff")
    status_grid.grid(row=2, column=0, sticky="ew", pady=(16, 12))
    for col in range(3):
        status_grid.grid_columnconfigure(col, weight=1)

    _metric_card(
        status_grid,
        row=0,
        column=0,
        title="Slot No",
        value=snapshot.get("slot_code") or "—",
        bg="#e7f1ff",
    )

    _metric_card(
        status_grid,
        row=0,
        column=1,
        title="Vehicle Number",
        value=snapshot.get("vehicle_number") or "—",
        bg="#e7f1ff",
    )

    entry_time = snapshot.get("entry_time")
    entry_value = entry_time.strftime("%H:%M:%S") if entry_time else "—"
    _metric_card(
        status_grid,
        row=0,
        column=2,
        title="Entry Time",
        value=entry_value,
        bg="#fef3c7",
    )

    vehicles_frame = ctk.CTkFrame(body, fg_color="#ffffff")
    vehicles_frame.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    vehicles_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        vehicles_frame,
        text="Your Vehicles",
        font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
        text_color="#1f2937",
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))

    vehicles = snapshot.get("vehicles") or []
    if vehicles:
        for idx, plate in enumerate(vehicles, start=1):
            ctk.CTkLabel(
                vehicles_frame,
                text=f"• {plate}",
                font=ctk.CTkFont(family="Inter", size=14),
                text_color="#111827",
            ).grid(row=idx, column=0, sticky="w", pady=2)
    else:
        ctk.CTkLabel(
            vehicles_frame,
            text="No vehicles registered yet.",
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#6b7280",
        ).grid(row=1, column=0, sticky="w", pady=2)

    def _update_clock() -> None:
        now = datetime.now()
        date_label.configure(text=now.strftime("%d-%m-%Y"))
        time_label.configure(text=now.strftime("%H:%M:%S"))
        frame.after(1000, _update_clock)

    _update_clock()
    return frame


def _metric_card(parent, *, row: int, column: int, title: str, value: Any, bg: str) -> ctk.CTkFrame:
    card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=20, width=220, height=170)
    card.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
    card.grid_propagate(False)

    ctk.CTkLabel(
        card,
        text=title,
        font=ctk.CTkFont(family="Inter", size=14),
        text_color="#1f2937",
    ).pack(pady=(20, 10))

    ctk.CTkLabel(
        card,
        text=str(value),
        font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
        text_color="#111827",
    ).pack(pady=(0, 14))

    return card


def _info_pill(parent, font: ctk.CTkFont, width: int = 120) -> ctk.CTkLabel:
    wrapper = ctk.CTkFrame(parent, fg_color="#e8f1ff", corner_radius=8, width=width, height=48)
    wrapper.pack(side="left", padx=6)
    wrapper.pack_propagate(False)

    pill = ctk.CTkLabel(
        wrapper,
        text="",
        font=font,
        text_color="#1f2937",
    )
    pill.pack(expand=True)
    return pill


def _build_placeholder_view(parent: ctk.CTkFrame, title: str) -> ctk.CTkFrame:
    view = ctk.CTkFrame(parent, fg_color="#ffffff")
    view.grid_columnconfigure(0, weight=1)
    view.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(
        view,
        text=title,
        font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
        text_color="#111827",
    ).grid(row=0, column=0, pady=(40, 12))

    ctk.CTkLabel(
        view,
        text="Still Building",
        font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
        text_color="#6b7280",
    ).grid(row=1, column=0)

    return view


def _load_snapshot(user: dict | None) -> dict[str, Any]:
    user_id = (user or {}).get("id")
    if not user_id:
        return {}
    try:
        return _member_service.get_dashboard_snapshot(int(user_id))
    except Exception:
        return {}

