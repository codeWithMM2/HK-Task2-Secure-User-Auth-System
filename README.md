🔐 Task 2: Secure User Authentication system

Key Technical Features:
Password Hashing (SHA-256): Instead of storing passwords in plain text, I utilized the hashlib library to implement SHA-256 hashing. This ensures that even if the database is compromised, the actual passwords remain secure.

Secure Signup & Login: A robust flow that validates user credentials against stored hashes during the login process.

Data Persistence: User credentials and their corresponding hashes are securely managed within a JSON structure, demonstrating professional data handling.

Input Integrity: The system ensures that only authorized users can access the contact management feaatures by verifying their identity through a secure gateway.
🛠️ How to Run the Project
To run these tasks on your local machine, follow these simple steps:

Prerequisites: Ensure you have Python 3.x installed on your system.

Download Files: Download all the files from this repository into a single folder on your computer.

🛠️ How to Run (Bash Command)
Type this to run in terminal or CMD:

Bash
python "Auth system.py"
