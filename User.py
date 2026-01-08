import csv
import hashlib

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def encrypt_password(self, password):
        # הצפנת סיסמה באמצעות SHA-256
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return hashed_password

    def create_user(self):
        try:
            # הצפנת הסיסמה לפני שמירה
            encrypted_password = self.encrypt_password(self.password)

            # יצירת או פתיחת הקובץ users.csv
            with open("users.csv", mode="a", encoding="utf-8", newline="") as file:
                fieldnames = ["username", "password"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                # כתיבת כותרת אם הקובץ ריק
                file.seek(0, 2)  # הולך לסוף הקובץ
                if file.tell() == 0:  # בודק אם הקובץ ריק
                    writer.writeheader()

                # הוספת המשתמש החדש עם סיסמה מוצפנת
                writer.writerow({"username": self.username, "password": encrypted_password})
                print(f"User '{self.username}' created successfully!")

        except FileNotFoundError:
            # טיפול במקרה שבו אין גישה לקובץ או התיקייה חסרה
            print("Error: Could not create or access the file 'users.csv'.")
        except Exception as e:
            # טיפול בשגיאה כללית
            print(f"An error occurred: {e}")