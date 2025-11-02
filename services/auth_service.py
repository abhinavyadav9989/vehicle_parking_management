# Authentication services for registration and login.

import bcrypt
from db.connection import get_connection

class AuthService:
    #  Getting the database connection
    def __init__(self):
        self.conn = get_connection()
        
    # Registering the new user
    # Hashing the password using bcrypt before storing pasword in database
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
        # Committing the transaction to save the user
        self.conn.commit()
        cur.close()

    # Authenticating the user by email and password
    def login(self, email, password):
        cur = self.conn.cursor(dictionary=True)
        # Finding the user by email
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        if not user:
            return None
        if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            return None
        return user


