import json
import hashlib
import os
import re
import random
from datetime import datetime

# File where all user data will be stored
DATA_FILE = "users.json"

# Max login attempts before lockout
MAX_ATTEMPTS = 3

#  Helper: Load & Save JSON

def load_users():
#Load users from JSON file. Return empty dict if file doesn't exist.
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_users(users):
#Save the users dictionary back to JSON file.
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

#  Helper: Password Hashing

def hash_password(password):
#Hash a password using SHA-256. Never store plain text passwords!
    return hashlib.sha256(password.encode()).hexdigest()

#  Validation Functions

def is_valid_email(email):
#Check if email format is correct using regex.
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(pattern, email) is not None


def is_strong_password(password):

   # Password must be:
   # - At least 8 characters
   # - Contain at least one uppercase letter
   # - Contain at least one digit
   # - Contain at least one special character

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit (0-9)."
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$ etc)."
    return True, "You are good to go!"

#  Core Features

def register_user():
#Handle new user registration.
    print("\n" + "="*45)
    print("         USER REGISTRATION")
    print("="*45)

    users = load_users()

    # Get username
    username = input("Enter username: ").strip()
    if not username:
        print("[!] Username cannot be empty.")
        return

    if username in users:
        print("[!] This username is already taken. Please try another.")
        return

    # Get email
    email = input("Enter email: ").strip().lower()
    if not email:
        print("[!] Email cannot be empty.")
        return
    if not is_valid_email(email):
        print("[!] Invalid email format. Please enter a valid email like user@example.com")
        return

    # Check if email already used
    for user in users.values():
        if user["email"] == email:
            print("[!] An account with this email already exists.")
            return

    # Get password
    password = input("Enter password: ").strip()
    is_strong, msg = is_strong_password(password)
    if not is_strong:
        print(f"[!] Weak password: {msg}")
        return

    confirm = input("Confirm password: ").strip()
    if password != confirm:
        print("[!] Passwords do not match. Please try again.")
        return

    # Choose role (basic role-based feature)
    print("\nSelect role:")
    print("  1. User")
    print("  2. Admin")
    role_choice = input("Enter choice (1/2): ").strip()
    if role_choice == "1":
        role = "User"
    elif role_choice == "2":
        role = "Admin"
    else:
        print("[!] Invalid choice. Setting role as User by default.")
    # Save user data
    users[username] = {
        "email": email,
        "password": hash_password(password),
        "role": role,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "login_attempts": 0,
        "is_locked": False
    }

    save_users(users)
    print(f"\n[✓] Account created successfully! Welcome, {username}.")
    print(f"    Role: {role.capitalize()}")


def login_user():
#Handle user login with attempt limiting.
    print("\n" + "="*45)
    print("              USER LOGIN")
    print("="*45)

    users = load_users()

    # Accept username or email
    identifier = input("Enter username or email: ").strip()
    if not identifier:
        print("[!] Input cannot be empty.")
        return

    # Find user by username or email
    matched_username = None
    for uname, data in users.items():
        if uname == identifier or data["email"] == identifier.lower():
            matched_username = uname
            break

    if not matched_username:
        print("[!] No account found with that username or email.")
        return

    user = users[matched_username]

    # Check if account is locked
    if user.get("is_locked"):
        print("[!] This account is locked due to too many failed login attempts.")
        print("    Use the 'Reset Password' option to unlock your account.")
        return

    # Get password
    password = input("Enter password: ").strip()
    hashed_input = hash_password(password)

    if hashed_input == user["password"]:
        # Successful login - reset attempts
        users[matched_username]["login_attempts"] = 0
        save_users(users)
        print(f"\n[✓] Login successful! Welcome back, {matched_username}.")
        print(f"    Role: {user['role'].capitalize()}")
        print(f"    Account created on: {user['created_at']}")

        # Show admin panel if admin
        if user["role"] == "admin":
            admin_panel(matched_username, users)
    else:
        # Wrong password - increment attempts
        users[matched_username]["login_attempts"] += 1
        attempts_left = MAX_ATTEMPTS - users[matched_username]["login_attempts"]

        if attempts_left <= 0:
            users[matched_username]["is_locked"] = True
            save_users(users)
            print("[!] Too many wrong attempts. Your account has been LOCKED.")
            print("    Use 'Reset Password' to unlock.")
        else:
            save_users(users)
            print(f"[!] Incorrect password. {attempts_left} attempt(s) remaining.")


def reset_password():
#Allow user to reset their password using email verification.
    print("\n" + "="*45)
    print("          PASSWORD RESET")
    print("="*45)

    users = load_users()

    username = input("Enter your username: ").strip()
    if username not in users:
        print("[!] Username not found.")
        return

    # Simple verification via email
    email = input("Enter your registered email: ").strip().lower()
    if users[username]["email"] != email:
        print("[!] Email does not match. Cannot reset password.")
        return

    # NOTE: In a real system, this OTP would be sent to the user's registered email.
    # This ensures that only the actual account owner can reset the password.
    # Previously this was a security vulnerability — anyone with a username and email
    # could reset the password and unlock the account without OTP verification.
    # OTP adds an extra layer of security to prevent unauthorized account access.

# Generate 6 digit OTP
    otp = random.randint(100000, 999999)
    print(f"\n[OTP Simulation] Your OTP is: {otp}")
    print("In a real system this OTP would be sent to your registered email\n")

    otp_attempts = 0
    while otp_attempts < 3:
        entered_otp = input("Enter OTP: ").strip()
        if not entered_otp.isdigit():
            print("[!]OTP must contains numbers only.")
            otp_attempts += 1
            continue
        if int(entered_otp) == otp:
            print("[✓] OTP verified successfully!")
            break
        else:
            otp_attempts += 1
            remaining = 3 - otp_attempts
            if remaining > 0:
                print(f"[!] Wrong OTP. {remaining} attempt(s) remaining..")
            else:
                print("[!] Too many attempts. Password reset cancelled.")
                return

    # Take new password and check the strength

    new_password = input("Enter new password: ").strip()
    is_strong, msg = is_strong_password(new_password)
    if not is_strong:
        print(f"[!] Weak password: {msg}")
        return

    confirm = input("Confirm new password: ").strip()
    if new_password != confirm:
        print("[!] Passwords do not match.")
        return

    users[username]["password"] = hash_password(new_password)
    users[username]["login_attempts"] = 0
    users[username]["is_locked"] = False
    save_users(users)

    print("[✓] Password reset successfully! You can now login with your new password.")


def delete_account():
#Let a user permanently delete their account.
    print("\n" + "="*45)
    print("          DELETE ACCOUNT")
    print("="*45)

    users = load_users()

    username = input("Enter your username: ").strip()
    if username not in users:
        print("[!] Username not found.")
        return

    password = input("Enter your password to confirm: ").strip()
    if hash_password(password) != users[username]["password"]:
        print("[!] Incorrect password. Account deletion cancelled.")
        return

    confirm = input(f"Are you sure you want to delete '{username}'? This cannot be undone. (yes/no): ").strip().lower()
    if confirm != "yes":
        print("[!] Account deletion cancelled.")
        return

    del users[username]
    save_users(users)
    print(f"[✓] Account '{username}' has been permanently deleted.")


def admin_panel(admin_username, users):
#A simple admin panel to view all users (only for admins).
    print("\n" + "="*45)
    print("           ADMIN PANEL")
    print("="*45)
    print(f"Logged in as: {admin_username} (Admin)\n")
    print(f"{'Username':<15} {'Email':<25} {'Role':<8} {'Status':<10} {'Created'}")
    print("-" * 85)
    for uname, info in users.items():
        status = "Locked" if info.get("is_locked") else "Active"
        print(f"{uname:<15} {info['email']:<25} {info['role']:<8} {status:<10} {info['created_at']}")
    print()


# ──────────────────────────────────────────────
#  Main Menu
# ──────────────────────────────────────────────

def show_banner():
    print("\n" + "*"*45)
    print("*   Multi-User Authentication System      *")
    print("*   Built with Python + JSON Storage      *")
    print("*"*45)


def main():
#Main function - entry point of the program.
    show_banner()

    while True:
        print("\n" + "-"*45)
        print("              MAIN MENU")
        print("-"*45)
        print("  1. Register")
        print("  2. Login")
        print("  3. Reset Password")
        print("  4. Delete Account")
        print("  5. Exit")
        print("-"*45)

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            login_user()
        elif choice == "3":
            reset_password()
        elif choice == "4":
            delete_account()
        elif choice == "5":
            print("\n[✓] Thanks for using the Auth System. Goodbye!\n")
            break
        else:
            print("[!] Invalid option. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()