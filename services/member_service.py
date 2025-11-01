"""Member data access helpers for the campus member dashboard."""

from __future__ import annotations

from typing import Any

from mysql.connector import MySQLConnection

from db.connection import get_connection


class MemberService:
    """Provide read helpers for member-facing dashboards."""

    def __init__(self) -> None:
        self.conn: MySQLConnection | None = None

    # region connection utilities
    def _get_conn(self) -> MySQLConnection:
        if self.conn is None or not self.conn.is_connected():
            self.conn = get_connection()
        return self.conn

    # endregion

    def get_dashboard_snapshot(self, user_id: int) -> dict[str, Any]:
        conn = self._get_conn()
        cur = conn.cursor(dictionary=True)
        snapshot: dict[str, Any] = {
            "registered_count": 0,
            "verification_status": "pending",
            "parking_status": "Not Parked",
            "slot_code": None,
            "vehicle_number": None,
            "entry_time": None,
            "vehicles": [],
        }
        try:
            # Registered vehicle count
            cur.execute("SELECT COUNT(*) AS count FROM vehicles WHERE user_id=%s", (user_id,))
            row = cur.fetchone() or {}
            snapshot["registered_count"] = int(row.get("count") or 0)

            # Verification status
            cur.execute(
                "SELECT status FROM verifications WHERE user_id=%s ORDER BY id DESC LIMIT 1",
                (user_id,),
            )
            row = cur.fetchone()
            if row and row.get("status"):
                snapshot["verification_status"] = str(row["status"]).lower()

            # Current parking event if exists
            cur.execute(
                """
                SELECT s.code AS slot_code, pe.entry_time, v.plate_number
                FROM parking_events pe
                JOIN slots s ON s.id = pe.slot_id
                JOIN vehicles v ON v.id = pe.vehicle_id
                WHERE v.user_id=%s AND pe.status='active'
                ORDER BY pe.entry_time DESC LIMIT 1
                """,
                (user_id,),
            )
            row = cur.fetchone()
            if row:
                snapshot["parking_status"] = "Parked"
                snapshot["slot_code"] = row.get("slot_code")
                snapshot["vehicle_number"] = row.get("plate_number")
                snapshot["entry_time"] = row.get("entry_time")

            # Vehicle list
            cur.execute(
                "SELECT plate_number FROM vehicles WHERE user_id=%s AND is_active=1 ORDER BY plate_number",
                (user_id,),
            )
            snapshot["vehicles"] = [r["plate_number"] for r in cur.fetchall() or []]

            return snapshot
        finally:
            cur.close()

