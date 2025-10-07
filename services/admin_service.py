from __future__ import annotations

from typing import Optional

from db.connection import get_connection


class AdminService:
    def __init__(self):
        self.conn = get_connection()

    # Dashboard metrics
    def count_users(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        (n,) = cur.fetchone() or (0,)
        cur.close()
        return int(n or 0)

    def count_guards(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE role='guard'")
        (n,) = cur.fetchone() or (0,)
        cur.close()
        return int(n or 0)

    def count_vehicles(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM vehicles")
        (n,) = cur.fetchone() or (0,)
        cur.close()
        return int(n or 0)

    def count_open_flags(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM flags WHERE status='open'")
        (n,) = cur.fetchone() or (0,)
        cur.close()
        return int(n or 0)

    # Verification queue
    def list_pending_verifications(self) -> list[dict]:
        cur = self.conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT v.id, u.id AS user_id, u.full_name, u.email, v.id_image_url, v.profile_image_url, v.status
            FROM verifications v JOIN users u ON u.id=v.user_id
            WHERE v.status='pending' ORDER BY v.id DESC
            """,
        )
        rows = cur.fetchall() or []
        cur.close()
        return rows

    def set_verification_status(self, verification_id: int, reviewer_id: int, status: str, notes: Optional[str] = None) -> None:
        if status not in ("approved", "rejected"):
            raise ValueError("Invalid status")
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                UPDATE verifications SET status=%s, reviewer_id=%s, reviewed_at=NOW(), notes=%s
                WHERE id=%s
                """,
                (status, reviewer_id, notes, verification_id),
            )
            # Reflect on user profile verified if approved
            if status == "approved":
                cur.execute(
                    """
                    UPDATE users SET is_profile_verified=TRUE
                    WHERE id=(SELECT user_id FROM verifications WHERE id=%s)
                    """,
                    (verification_id,),
                )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    # Flags
    def list_open_flags(self) -> list[dict]:
        cur = self.conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT f.id, f.reason, f.created_at, u.full_name AS raised_by
            FROM flags f JOIN users u ON u.id=f.raised_by_guard_id
            WHERE f.status='open' ORDER BY f.created_at DESC
            """,
        )
        rows = cur.fetchall() or []
        cur.close()
        return rows

    def close_flag(self, flag_id: int, admin_user_id: int, note: str | None = None) -> None:
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                UPDATE flags
                SET status='closed', closed_by_admin_id=%s, resolution_note=%s, closed_at=NOW()
                WHERE id=%s AND status='open'
                """,
                (admin_user_id, note, flag_id),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()


