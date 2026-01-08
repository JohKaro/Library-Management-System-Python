import csv


class Observer:
    """
    מחלקת Observer שמנהלת הודעות על החזרת ספרים ומטפלת במשתמשים שמחכים לספרים.
    """

    def __init__(self, users_file="users.csv", waiting_list_file="waiting_list.csv"):
        self.users_file = users_file
        self.waiting_list_file = waiting_list_file

    def notify(self, book_title):
        """
        בודקת אם הספר שהוחזר נמצא ברשימת ההמתנה ושולחת הודעה מתאימה.
        :param book_title: שם הספר שהוחזר
        """
        try:
            # קריאת המשתמשים שממתינים לספר
            waiting_users = self.get_waiting_users(book_title)

            if not waiting_users:
                print(f"No users waiting for '{book_title}'.")
                return

            # קריאת רשימת המשתמשים מקובץ users.csv
            users = self.load_users()

            # יצירת הודעות לכל המשתמשים ברשימה
            for user in users:
                if user in waiting_users:
                    self.log_notification(user, book_title)

        except Exception as e:
            print(f"An error occurred while notifying users: {e}")

    def get_waiting_users(self, book_title):
        """
        מחזירה רשימה של משתמשים שממתינים לספר מסוים מתוך waiting_list.csv.
        :param book_title: שם הספר
        :return: רשימת שמות משתמשים
        """
        try:
            with open(self.waiting_list_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                return [row["Name"].strip() for row in reader if row["Book Title"].strip().lower() == book_title.strip().lower()]
        except FileNotFoundError:
            print(f"Error: The file '{self.waiting_list_file}' does not exist.")
            return []
        except Exception as e:
            print(f"An error occurred while reading '{self.waiting_list_file}': {e}")
            return []

    def load_users(self):
        """
        טוען את רשימת המשתמשים מקובץ users.csv.
        :return: רשימת שמות משתמשים
        """
        try:
            with open(self.users_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                return [row["name"].strip() for row in reader]
        except FileNotFoundError:
            print(f"Error: The file '{self.users_file}' does not exist.")
            return []
        except Exception as e:
            print(f"An error occurred while reading '{self.users_file}': {e}")
            return []

    def log_notification(self, user_name, book_title):
        """
        רושם הודעה ביומן עבור משתמש.
        :param user_name: שם המשתמש
        :param book_title: שם הספר
        """
        log_message = f"Notification: The book '{book_title}' is now available. User '{user_name}' was notified."
        print(log_message)  # ניתן להחליף זאת בכתיבה ללוג

    def get_notification(self, username):
        """
        מחזירה הודעה עבור הספרים שהמשתמשים מחכים להם, ורק אם הם זמינים להשאלה.
        :param username: שם המשתמש שמבקש את ההודעה
        :return: הודעה אם יש ספרים זמינים ברשימת ההמתנה, או None אם אין הודעות
        """
        try:
            notifications = []

            # קריאת רשימת ההמתנה מקובץ waiting_list.csv
            with open(self.waiting_list_file, mode="r", encoding="utf-8") as waiting_file:
                waiting_reader = csv.DictReader(waiting_file)
                waiting_list = list(waiting_reader)

            # קריאת רשימת הספרים מקובץ books.csv
            with open("books.csv", mode="r", encoding="utf-8") as books_file:
                books_reader = csv.DictReader(books_file)
                books_list = {row["title"].strip().lower(): row for row in books_reader}

            # חיפוש ספרים זמינים ברשימת ההמתנה
            for row in waiting_list:
                book_title = row["Book Title"].strip().lower()

                # בדיקה אם הספר ברשימת הספרים וניתן להשאלה
                if book_title in books_list and books_list[book_title]["is_loaned"].strip().lower() == "no":
                    notifications.append(
                        f"User '{row['Name']}' is waiting for the book '{row['Book Title']}', which is now available."
                    )

            # אם יש הודעות, מחזירים אותן
            if notifications:
                return "\n".join(notifications)

            # אם אין הודעות, מחזירים None
            return None

        except FileNotFoundError as e:
            return f"Error: {e.filename} file not found."
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def remove_book_from_waiting_list(self, username):
        """
        מסיר רשומות עבור משתמש מקובץ waiting_list.csv לאחר שליחת הודעה.
        :param username: שם המשתמש להסרה מהרשימה
        """
        try:
            with open(self.waiting_list_file, mode="r", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            # שמירה רק על רשומות שלא קשורות למשתמש
            updated_rows = [
                row for row in rows
                if row.get("Name", "").strip().lower() != username.strip().lower()
            ]

            with open(self.waiting_list_file, mode="w", encoding="utf-8", newline="") as file:
                fieldnames = ["Book Title", "Name", "Email"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_rows)

        except FileNotFoundError:
            print(f"Error: The file '{self.waiting_list_file}' does not exist.")
        except Exception as e:
            print(f"An error occurred while updating the waiting list: {e}")