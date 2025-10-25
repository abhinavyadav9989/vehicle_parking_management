from __future__ import annotations
from typing import Optional
from db.connection import get_connection

class GuardService:
    def __init__(self):
        self.conn = get_connection()

    def get_profile_data(self, user_id: int) -> dict:
        """Get guard profile data"""
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT full_name, college_id, email, is_profile_verified
                FROM users WHERE id=%s
            """, (user_id,))
            result = cur.fetchone() or {}
            return result
        finally:
            cur.close()

    def update_profile_data(self, user_id: int, full_name: str, college_id: str, email: str) -> None:
        """Update guard profile data"""
        cur = self.conn.cursor()
        try:
            cur.execute("""
                UPDATE users 
                SET full_name=%s, college_id=%s, email=%s
                WHERE id=%s
            """, (full_name, college_id, email, user_id))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def upload_profile_image(self, user_id: int, image_path: str) -> None:
        """Upload profile image for guard"""
        cur = self.conn.cursor()
        try:
            # Check if verification record exists
            cur.execute("SELECT id FROM verifications WHERE user_id=%s", (user_id,))
            existing = cur.fetchone()
            
            if existing:
                # Update existing record
                cur.execute("""
                    UPDATE verifications 
                    SET profile_image_url=%s, status='pending'
                    WHERE user_id=%s
                """, (image_path, user_id))
            else:
                # Create new record
                cur.execute("""
                    INSERT INTO verifications (user_id, profile_image_url, status)
                    VALUES (%s, %s, 'pending')
                """, (user_id, image_path))
            
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def upload_college_id_image(self, user_id: int, image_path: str) -> None:
        """Upload college ID image for guard"""
        cur = self.conn.cursor()
        try:
            # Check if verification record exists
            cur.execute("SELECT id FROM verifications WHERE user_id=%s", (user_id,))
            existing = cur.fetchone()
            
            if existing:
                # Update existing record
                cur.execute("""
                    UPDATE verifications 
                    SET id_image_url=%s, status='pending'
                    WHERE user_id=%s
                """, (image_path, user_id))
            else:
                # Create new record
                cur.execute("""
                    INSERT INTO verifications (user_id, id_image_url, status)
                    VALUES (%s, %s, 'pending')
                """, (user_id, image_path))
            
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def submit_for_verification(self, user_id: int) -> None:
        """Submit guard profile for verification"""
        cur = self.conn.cursor()
        try:
            # Update verification status to pending
            cur.execute("""
                UPDATE verifications 
                SET status='pending', reviewer_id=NULL, reviewed_at=NULL, notes=NULL
                WHERE user_id=%s
            """, (user_id,))
            
            # Set user verification status to false
            cur.execute("""
                UPDATE users 
                SET is_profile_verified=FALSE
                WHERE id=%s
            """, (user_id,))
            
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def get_verification_images(self, user_id: int) -> dict:
        """Get verification images for guard"""
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT profile_image_url, id_image_url, status
                FROM verifications WHERE user_id=%s
            """, (user_id,))
            result = cur.fetchone() or {}
            return result
        finally:
            cur.close()

    def get_verification_status(self, user_id: int) -> str:
        """Get verification status for guard"""
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT status FROM verifications WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
            return (row[0] if row else None) or 'pending'
        finally:
            cur.close()

    def can_edit_profile(self, user_id: int) -> bool:
        """Check if guard can edit profile (not under pending verification)"""
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT status FROM verifications WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
            status = (row[0] if row else None) or 'pending'
            # Can edit if status is not 'pending'
            return status != 'pending'
        finally:
            cur.close()

    def get_complete_profile_data(self, user_id: int) -> dict:
        """Get complete profile data including verification status"""
        cur = self.conn.cursor(dictionary=True)
        try:
            # Get user basic info
            cur.execute("""
                SELECT full_name, college_id, email, is_profile_verified
                FROM users WHERE id=%s
            """, (user_id,))
            user_data = cur.fetchone() or {}
            
            # Get verification info
            cur.execute("""
                SELECT profile_image_url, id_image_url, status
                FROM verifications WHERE user_id=%s
            """, (user_id,))
            verification_data = cur.fetchone() or {}
            
            # Combine data
            result = {
                **user_data,
                **verification_data,
                'can_edit': self.can_edit_profile(user_id)
            }
            return result
        finally:
            cur.close()
