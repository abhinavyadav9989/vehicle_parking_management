"""Campus member dashboard view."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import customtkinter as ctk
from PIL import Image

from services.member_service import MemberService

assets_path = Path(__file__).resolve().parents[1] / "assets"
mem_servc = MemberService()
_icon_cache: dict[tuple[str, tuple[int, int]], ctk.CTkImage] = {}


def render_member_vw(parent, user=None, on_logout=None):
    """Render the campus member dashboard page."""
    root = ctk.CTkFrame(parent, fg_color="#f5f7ff")
    root.pack(fill="both", expand=True)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    sbar = _mk_sbar(root, on_logout)
    sbar.grid(row=0, column=0, sticky="nsw")

    main_panel = ctk.CTkFrame(root, fg_color="#ffffff")
    main_panel.grid(row=0, column=1, sticky="nsew")
    main_panel.grid_columnconfigure(0, weight=1)
    main_panel.grid_rowconfigure(0, weight=1)

    vw = {
        "dashboard": _mk_dashboard_vw(main_panel, user),
        "slots": _mk_placeholder_vw(main_panel, "My Slots"),
        "profile": _mk_placeholder_vw(main_panel, "Profile"),
    }

    def set_vw(view: str) -> None:
        for child in vw.values():
            child.grid_remove()
        vw[view].grid(row=0, column=0, sticky="nsew")
        sbar.upd_select(view)

    sbar.config_nav(set_vw)
    set_vw("dashboard")
    return root


def _mk_sbar(parent, on_logout) -> ctk.CTkFrame:
    sbar = ctk.CTkFrame(parent, fg_color="#e5edff", width=180)
    sbar.grid_propagate(False)
    sbar.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0)
    sbar.grid_rowconfigure(7, weight=1)

    nav_title_font = ctk.CTkFont(family="Inter", size=14, weight="bold")
    nav_font = ctk.CTkFont(family="Inter", size=13)

    ctk.CTkLabel(
        sbar,
        text="",
        width=1,
        height=20,
        fg_color="transparent",
    ).grid(row=0, column=0, pady=(20, 10))

    nav_buttons: dict[str, ctk.CTkButton] = {}
    icon_map = {
        "dashboard": _get_icon("dashboard.png", (20, 20)),
        "slots": _get_icon("jeep_715882.png", (20, 20)),
        "profile": _get_icon("profile.png", (20, 20)),
    }

    def mk_btn(text: str, view_name: str, row_index: int, primary: bool = False) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            sbar,
            text=text,
            image=icon_map.get(view_name),
            compound="left",
            width=150,
            height=42,
            fg_color="#ffffff" if primary else "transparent",
            hover_color="#f3f4ff" if primary else "#dbe4ff",
            text_color="#2563eb" if primary else "#111827",
            font=nav_title_font if primary else nav_font,
            corner_radius=18,
        )
        btn.grid(row=row_index, column=0, padx=18, pady=6, sticky="ew")
        nav_buttons[view_name] = btn
        return btn

    mk_btn("Dashboard", "dashboard", 1, primary=True)
    mk_btn("My Slots", "slots", 2)
    mk_btn("Profile", "profile", 3)

    if on_logout is not None:
        logout_icon = _get_icon("logout.png", (18, 18))
        ctk.CTkButton(
            sbar,
            text="Logout",
            width=140,
            height=40,
            fg_color="transparent",
            hover_color="#fee2e2",
            text_color="#2563eb",
            font=nav_title_font,
            corner_radius=18,
            image=logout_icon,
            compound="left",
            command=on_logout,
        ).grid(row=7, column=0, padx=20, pady=24, sticky="s")

    def upd_select(view: str) -> None:
        for key, btn in nav_buttons.items():
            primary = key == view
            btn.configure(
                fg_color="#ffffff" if primary else "transparent",
                text_color="#2563eb" if primary else "#111827",
            )

    def config_nav(callback):
        for name, btn in nav_buttons.items():
            btn.configure(command=lambda v=name: callback(v))

    sbar.config_nav = config_nav  # type: ignore[attr-defined]
    sbar.upd_select = upd_select  # type: ignore[attr-defined]
    upd_select("dashboard")

    return sbar


def _mk_dashboard_vw(parent: ctk.CTkFrame, user: dict | None) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(parent, fg_color="#ffffff")
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=1)

    header_font = {
        "title": ctk.CTkFont(family="Inter", size=24, weight="bold"),
        "subtitle": ctk.CTkFont(family="Inter", size=14, weight="bold"),
        "meta": ctk.CTkFont(family="Inter", size=12),
    }

    user_name = (user or {}).get("full_name", "Member")

    header = ctk.CTkFrame(frame, fg_color="#ffffff")
    header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
    header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        header,
        text=f"Welcome {user_name}",
        font=header_font["title"],
        text_color="#111827",
    ).grid(row=0, column=0, sticky="w")

    date_time_fm = ctk.CTkFrame(header, fg_color="#ffffff")
    date_time_fm.grid(row=0, column=1, sticky="e", padx=(12, 0))

    ctk.CTkLabel(
        date_time_fm,
        text="Date :",
        font=header_font["meta"],
        text_color="#1f2937",
    ).pack(side="left", padx=(0, 6))
    date_lbl = _mk_info_fill(date_time_fm, header_font["meta"], width=140)

    ctk.CTkLabel(
        date_time_fm,
        text="Time :",
        font=header_font["meta"],
        text_color="#1f2937",
    ).pack(side="left", padx=(12, 6))
    time_lbl = _mk_info_fill(date_time_fm, header_font["meta"], width=140)

    body = ctk.CTkFrame(frame, fg_color="#ffffff")
    body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    body.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        body,
        text="Manage Your Parking and Profile",
        font=header_font["subtitle"],
        text_color="#1f2937",
    ).grid(row=0, column=0, sticky="w", pady=(0, 16))

    dashboard_info = _get_snapshot(user)

    kpi_grid = ctk.CTkFrame(body, fg_color="#ffffff")
    kpi_grid.grid(row=1, column=0, sticky="ew")
    for col in range(3):
        kpi_grid.grid_columnconfigure(col, weight=1)

    _mk_kpi_card(
        kpi_grid,
        row=0,
        column=0,
        title="Registered Vehicles",
        value=str(dashboard_info.get("registered_count", 0)),
        bg="#e7f1ff",
        icon=_get_icon("jeep_715882.png", (24, 24)),
    )

    verification_sts = dashboard_info.get("verification_status", "pending").title()
    verification_bg = {
        "Approved": "#c4f5cb",
        "Rejected": "#fecaca",
        "Pending": "#fef08a",
    }.get(verification_sts, "#fef08a")

    _mk_kpi_card(
        kpi_grid,
        row=0,
        column=1,
        title="Verification Status",
        value=verification_sts,
        bg=verification_bg,
        icon=_get_icon("verified.png", (24, 24)),
    )

    _mk_kpi_card(
        kpi_grid,
        row=0,
        column=2,
        title="Current Status",
        value=dashboard_info.get("parking_status", "Not Parked"),
        bg="#e7f1ff",
        icon=_get_icon("clock.png", (24, 24)),
    )

    sts_grid = ctk.CTkFrame(body, fg_color="#ffffff")
    sts_grid.grid(row=2, column=0, sticky="ew", pady=(16, 12))
    for col in range(3):
        sts_grid.grid_columnconfigure(col, weight=1)

    _mk_kpi_card(
        sts_grid,
        row=0,
        column=0,
        title="Slot No",
        value=dashboard_info.get("slot_code") or "—",
        bg="#e7f1ff",
    )

    _mk_kpi_card(
        sts_grid,
        row=0,
        column=1,
        title="Vehicle Number",
        value=dashboard_info.get("vehicle_number") or "—",
        bg="#e7f1ff",
    )

    entry_time = dashboard_info.get("entry_time")
    entry_value = entry_time.strftime("%H:%M:%S") if entry_time else "—"
    _mk_kpi_card(
        sts_grid,
        row=0,
        column=2,
        title="Entry Time",
        value=entry_value,
        bg="#fef3c7",
    )

    vehicle_fm = ctk.CTkFrame(body, fg_color="#ffffff")
    vehicle_fm.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    vehicle_fm.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        vehicle_fm,
        text="Your Vehicles",
        font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
        text_color="#1f2937",
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))

    vehicles = dashboard_info.get("vehicles") or []
    if vehicles:
        for idx, plate in enumerate(vehicles, start=1):
            ctk.CTkLabel(
                vehicle_fm,
                text=f"• {plate}",
                font=ctk.CTkFont(family="Inter", size=14),
                text_color="#111827",
            ).grid(row=idx, column=0, sticky="w", pady=2)
    else:
        ctk.CTkLabel(
            vehicle_fm,
            text="No vehicles registered yet.",
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#6b7280",
        ).grid(row=1, column=0, sticky="w", pady=2)

    def upd_clock() -> None:
        now = datetime.now()
        date_lbl.configure(text=now.strftime("%d-%m-%Y"))
        time_lbl.configure(text=now.strftime("%H:%M:%S"))
        frame.after(1000, upd_clock)

    upd_clock()
    return frame


def _mk_kpi_card(
    parent,
    *,
    row: int,
    column: int,
    title: str,
    value: Any,
    bg: str,
    icon: ctk.CTkImage | None = None,
) -> ctk.CTkFrame:
    card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=20, width=220, height=174)
    card.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
    card.grid_propagate(False)

    title_frame = ctk.CTkFrame(card, fg_color="transparent")
    title_frame.pack(pady=(16, 6))

    if icon is not None:
        ctk.CTkLabel(title_frame, text="", image=icon).pack(side="left", padx=(0, 6))

    ctk.CTkLabel(
        title_frame,
        text=title,
        font=ctk.CTkFont(family="Inter", size=14),
        text_color="#1f2937",
    ).pack(side="left")

    ctk.CTkLabel(
        card,
        text=str(value),
        font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
        text_color="#111827",
    ).pack(pady=(0, 14))

    return card


def _mk_info_fill(parent, font: ctk.CTkFont, width: int = 120) -> ctk.CTkLabel:
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


def _mk_placeholder_vw(parent: ctk.CTkFrame, title: str) -> ctk.CTkFrame:
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


def _get_snapshot(user: dict | None) -> dict[str, Any]:
    user_id = (user or {}).get("id")
    if not user_id:
        return {}
    try:
        return mem_servc.get_dashboard_snapshot(int(user_id))
    except Exception:
        return {}


def _get_icon(filename: str, size: tuple[int, int]) -> ctk.CTkImage | None:
    key = (filename, size)
    if key in _icon_cache:
        return _icon_cache[key]

    image_path = assets_path / filename
    if not image_path.exists():
        return None

    image = Image.open(image_path).convert("RGBA")
    icon = ctk.CTkImage(light_image=image, dark_image=image, size=size)
    _icon_cache[key] = icon
    return icon

