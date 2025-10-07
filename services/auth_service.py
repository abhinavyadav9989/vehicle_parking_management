import bcrypt
from db.connection import get_connection


class AuthService:
    def __init__(self):
        self.conn = get_connection()

    def register(self, college_id, full_name, email, password, role):
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO users (college_id, full_name, email, password_hash, role)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (college_id, full_name, email, password_hash, role),
        )
        self.conn.commit()

    def login(self, email, password):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        if not user:
            return None
        if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            return None
        return user


