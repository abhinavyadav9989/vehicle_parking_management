from __future__ import annotations

from datetime import datetime
from typing import Optional

from db.connection import get_connection


class ParkingService:
    def __init__(self):
        self.conn = get_connection()

    # KPIs
    def count_active_inside(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM parking_events WHERE status='active'")
        (n,) = cur.fetchone() or (0,)
        cur.close()
        return int(n or 0)

    def count_free_slots(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM slots WHERE status='available'")
        (n,) = cur.fetchone() or (0,)
        cur.close()
        return int(n or 0)

    def count_today_entries(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM parking_events WHERE DATE(entry_time)=CURRENT_DATE")
        (n,) = cur.fetchone() or (0,)
        cur.close()
        return int(n or 0)

    def count_open_flags(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM flags WHERE status='open'")
        (n,) = cur.fetchone() or (0,)
        cur.close()
        return int(n or 0)

    def list_active_parking_events(self) -> list[dict]:
        """Get all active parking events with user and slot details"""
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT 
                    pe.id as parking_id,
                    v.plate_number,
                    u.full_name as user_name,
                    s.code as slot_code,
                    pe.entry_time,
                    pe.exit_time
                FROM parking_events pe
                JOIN vehicles v ON v.id = pe.vehicle_id
                JOIN users u ON u.id = v.user_id
                JOIN slots s ON s.id = pe.slot_id
                WHERE pe.status = 'active'
                ORDER BY pe.entry_time DESC
            """)
            rows = cur.fetchall() or []
            return rows
        finally:
            cur.close()

    # Vehicle lookup
    def find_vehicle(self, plate: str) -> Optional[dict]:
        cur = self.conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT v.id AS vehicle_id, v.plate_number, u.id AS user_id, u.full_name, u.is_profile_verified
            FROM vehicles v JOIN users u ON u.id=v.user_id
            WHERE v.plate_number=%s AND v.is_active=1
            """,
            (plate,),
        )
        row = cur.fetchone()
        cur.close()
        return row

    def get_available_slots(self) -> list[dict]:
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT id, code FROM slots WHERE status='available' ORDER BY code")
        rows = cur.fetchall() or []
        cur.close()
        return rows

    def allocate(self, vehicle_id: int, slot_id: int, guard_user_id: int,
                 ocr_plate_text: Optional[str] = None, ocr_conf: Optional[float] = None) -> None:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT status FROM slots WHERE id=%s FOR UPDATE", (slot_id,))
            row = cur.fetchone()
            if not row or row[0] != 'available':
                self.conn.rollback()
                raise ValueError("Slot not available")
            cur.execute(
                """
                INSERT INTO parking_events (vehicle_id, slot_id, guard_user_id, ocr_plate_text, ocr_confidence)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (vehicle_id, slot_id, guard_user_id, ocr_plate_text, ocr_conf),
            )
            cur.execute("UPDATE slots SET status='occupied' WHERE id=%s", (slot_id,))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def process_exit(self, plate: str) -> bool:
        cur = self.conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT pe.id, pe.slot_id
            FROM parking_events pe
            JOIN vehicles v ON v.id = pe.vehicle_id
            WHERE v.plate_number=%s AND pe.status='active'
            ORDER BY pe.entry_time DESC LIMIT 1
            """,
            (plate,),
        )
        ev = cur.fetchone()
        cur.close()
        if not ev:
            return False
        cur2 = self.conn.cursor()
        try:
            cur2.execute(
                "UPDATE parking_events SET status='exited', exit_time=%s WHERE id=%s",
                (datetime.now(), ev['id']),
            )
            cur2.execute("UPDATE slots SET status='available' WHERE id=%s", (ev['slot_id'],))
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur2.close()

    def raise_flag(self, raised_by_guard_id: int, reason: str, vehicle_id: Optional[int] = None) -> None:
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO flags (vehicle_id, raised_by_guard_id, reason) VALUES (%s,%s,%s)",
                (vehicle_id, raised_by_guard_id, reason),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()


