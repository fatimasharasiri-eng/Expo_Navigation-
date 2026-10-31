import random
import time


class Authentication:

    def __init__(self):
        self.users = {}
        self.reset_codes = {}

    # Register a new user
    def sign_up(self, email, username, password):

        if "@" not in email or not email.endswith(".com"):
            return False, "Invalid email"

        if not username:
            return False, "Please enter a username"

        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if username in self.users:
            return False, "Username already exists"

        for user in self.users.values():
            if user["email"] == email:
                return False, "Email already registered"

        self.users[username] = {
            "email": email,
            "username": username,
            "password": password
        }

        return True, "Registration successful!"

    # Login
    def login(self, username, password):

        if username not in self.users:
            return False

        if self.users[username]["password"] == password:
            return True

        return False

    # Generate password reset code
    def generate_reset_code(self, email):

        for username, user in self.users.items():

            if user["email"] == email:

                code = str(random.randint(100000, 999999))

                self.reset_codes[email] = {
                    "code": code,
                    "expiry": time.time() + 300
                }

                return True, code

        return False, None

    # Reset password
    def reset_password(self, email, code, new_password):

        if email not in self.reset_codes:
            return False, "No reset request found"

        saved_code = self.reset_codes[email]

        if time.time() > saved_code["expiry"]:
            del self.reset_codes[email]
            return False, "Verification code expired"

        if saved_code["code"] != code:
            return False, "Invalid verification code"

        if len(new_password) < 8:
            return False, "Password must be at least 8 characters"

        for user in self.users.values():

            if user["email"] == email:
                user["password"] = new_password
                del self.reset_codes[email]

                return True, "Password changed successfully!"

        return False, "User not found"