from __future__ import annotations

from typing import Optional

from db.connection import get_connection


class MemberService:
    def __init__(self):
        self.conn = get_connection()

    def submit_verification(self, user_id: int, id_image_url: str, profile_image_url: str) -> None:
        cur = self.conn.cursor()
        try:
            # Upsert-like behavior: if a row exists, set to pending with new paths
            cur.execute(
                "SELECT id FROM verifications WHERE user_id=%s",
                (user_id,),
            )
            existing = cur.fetchone()
            if existing:
                cur.execute(
                    """
                    UPDATE verifications
                    SET id_image_url=%s, profile_image_url=%s, status='pending', reviewer_id=NULL, reviewed_at=NULL, notes=NULL
                    WHERE user_id=%s
                    """,
                    (id_image_url, profile_image_url, user_id),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO verifications (user_id, id_image_url, profile_image_url, status)
                    VALUES (%s,%s,%s,'pending')
                    """,
                    (user_id, id_image_url, profile_image_url),
                )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def get_verification_status(self, user_id: int) -> str:
        cur = self.conn.cursor()
        cur.execute("SELECT status FROM verifications WHERE user_id=%s", (user_id,))
        row = cur.fetchone()
        cur.close()
        return (row[0] if row else None) or 'pending'

    def get_assigned_slot(self, user_id: int) -> Optional[dict]:
        cur = self.conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT s.code, pe.entry_time
            FROM parking_events pe
            JOIN vehicles v ON v.id = pe.vehicle_id
            JOIN slots s ON s.id = pe.slot_id
            WHERE v.user_id=%s AND pe.status='active'
            ORDER BY pe.entry_time DESC LIMIT 1
            """,
            (user_id,),
        )
        row = cur.fetchone()
        cur.close()
        return row

    def list_vehicles(self, user_id: int) -> list[dict]:
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT id, plate_number, is_active FROM vehicles WHERE user_id=%s", (user_id,))
        rows = cur.fetchall() or []
        cur.close()
        return rows

    def add_vehicle(self, user_id: int, plate_number: str) -> None:
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO vehicles (user_id, plate_number, is_active) VALUES (%s,%s,1)",
                (user_id, plate_number.upper()),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def set_vehicle_active(self, vehicle_id: int, active: bool) -> None:
        cur = self.conn.cursor()
        try:
            cur.execute(
                "UPDATE vehicles SET is_active=%s WHERE id=%s",
                (1 if active else 0, vehicle_id),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def get_profile_data(self, user_id: int) -> dict:
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT full_name, college_id, email FROM users WHERE id=%s", (user_id,))
        user_data = cur.fetchone() or {}
        cur.close()
        return user_data

    def update_profile_data(self, user_id: int, full_name: str, college_id: str, email: str) -> None:
        cur = self.conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET full_name=%s, college_id=%s, email=%s WHERE id=%s",
                (full_name, college_id, email, user_id),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def upload_profile_image(self, user_id: int, image_path: str) -> None:
        cur = self.conn.cursor()
        try:
            # Check if verification record exists
            cur.execute("SELECT id FROM verifications WHERE user_id=%s", (user_id,))
            existing = cur.fetchone()
            
            if existing:
                cur.execute(
                    "UPDATE verifications SET profile_image_url=%s WHERE user_id=%s",
                    (image_path, user_id),
                )
            else:
                cur.execute(
                    "INSERT INTO verifications (user_id, profile_image_url, status) VALUES (%s, %s, 'pending')",
                    (user_id, image_path),
                )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def upload_college_id_image(self, user_id: int, image_path: str) -> None:
        cur = self.conn.cursor()
        try:
            # Check if verification record exists
            cur.execute("SELECT id FROM verifications WHERE user_id=%s", (user_id,))
            existing = cur.fetchone()
            
            if existing:
                cur.execute(
                    "UPDATE verifications SET id_image_url=%s WHERE user_id=%s",
                    (image_path, user_id),
                )
            else:
                cur.execute(
                    "INSERT INTO verifications (user_id, id_image_url, status) VALUES (%s, %s, 'pending')",
                    (user_id, image_path),
                )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def submit_for_verification(self, user_id: int) -> None:
        cur = self.conn.cursor()
        try:
            # Update verification status to pending
            cur.execute(
                "UPDATE verifications SET status='pending' WHERE user_id=%s",
                (user_id,),
            )
            # Ensure user profile is marked as not verified
            cur.execute(
                "UPDATE users SET is_profile_verified=FALSE WHERE id=%s",
                (user_id,),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def get_verification_images(self, user_id: int) -> dict:
        cur = self.conn.cursor(dictionary=True)
        cur.execute(
            "SELECT profile_image_url, id_image_url FROM verifications WHERE user_id=%s",
            (user_id,),
        )
        result = cur.fetchone() or {}
        cur.close()
        return result


