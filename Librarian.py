import csv
import datetime
import os
from observer import Observer


class Librarian:
    def __init__(self, csv_manager):
        self.csv_manager = csv_manager
        self.books = self.csv_manager.load_books()
        self.observer = Observer()  # אתחול מחלקת Observer

    def list_books(self):
        """מחזירה את רשימת הספרים בפורמט טקסטואלי"""
        if not self.books:
            return "No books available."
        return "\n".join([str(book) for book in self.books])

    def search_by_title(self, title):
        return [book for book in self.books if title.lower() in book.title.lower()]

    def add_or_update_book(self, new_book):
        try:
            # קריאה של הספרים מקובץ CSV
            books = []
            book_found = False
            with open(self.csv_manager.filepath, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                books = list(reader)

            # בדיקה אם הספר קיים
            for book in books:
                if book["title"].lower() == new_book["title"].lower() and book["author"].lower() == new_book[
                    "author"].lower():
                    # עדכון כמות העותקים
                    book["copies"] = str(int(book["copies"]) + int(new_book["copies"]))
                    book_found = True
                    break

            # אם הספר לא נמצא, מוסיפים אותו
            if not book_found:
                books.append(new_book)

            # שמירת הרשימה המעודכנת
            with open(self.csv_manager.filepath, mode="w", encoding="utf-8", newline="") as file:
                fieldnames = ["title", "author", "is_loaned", "copies", "genre", "year"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(books)

        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{self.csv_manager.filepath}' was not found.")
        except Exception as e:
            raise Exception(f"An error occurred while updating the book: {e}")

    def remove_book_copy(self, title):
        try:
            # קריאה של הספרים מקובץ CSV
            books = []
            book_found = False
            with open(self.csv_manager.filepath, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                books = list(reader)

            # רשימה מעודכנת של ספרים (לכתיבה חזרה)
            updated_books = []

            for book in books:
                if book["title"].lower() == title.lower():
                    copies = int(book["copies"])
                    if copies > 1:
                        # הפחתת כמות העותקים
                        book["copies"] = str(copies - 1)
                        updated_books.append(book)
                    else:
                        # אם יש רק עותק אחד, הספר יימחק מהרשימה
                        book_found = True
                else:
                    # ספרים אחרים נשארים ברשימה
                    updated_books.append(book)

            # שמירת הרשימה המעודכנת
            with open(self.csv_manager.filepath, mode="w", encoding="utf-8", newline="") as file:
                fieldnames = ["title", "author", "is_loaned", "copies", "genre", "year"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_books)

            return book_found

        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{self.csv_manager.filepath}' was not found.")
        except Exception as e:
            raise Exception(f"An error occurred while removing a book copy: {e}")

    def save_changes(self):
        self.csv_manager.save_books(self.books)

    def return_book_logic(self, book_title):
        try:
            # קריאה מקובץ loaned_books.csv
            with open("loaned_books.csv", mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                loaned_books = list(reader)

            # חיפוש ועדכון כמות ההשאלות של הספר
            book_found = False
            for book in loaned_books:
                if book["title"].lower() == book_title.lower():
                    book_found = True
                    current_loans = int(book["copies_loaned"])
                    if current_loans > 1:
                        book["copies_loaned"] = str(current_loans - 1)
                        self.observer.notify(book_title)
                    elif current_loans == 1:
                        loaned_books.remove(book)  # הסרת הספר אם אין עותקים מושאלים יותר

            if not book_found:
                raise ValueError(f"Book '{book_title}' is not currently loaned.")

            # כתיבה מחדש של loaned_books.csv
            with open("loaned_books.csv", mode="w", encoding="utf-8", newline="") as file:
                fieldnames = ["title", "copies_loaned"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(loaned_books)

            # עדכון קובץ books.csv
            with open(self.csv_manager.filepath, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                books = list(reader)

            for book in books:
                if book["title"].lower() == book_title.lower():
                    book["is_loaned"] = "No"

            with open(self.csv_manager.filepath, mode="w", encoding="utf-8", newline="") as file:
                fieldnames = ["title", "author", "is_loaned", "copies", "genre", "year"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(books)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"File error: {e}")
        except ValueError as e:
            raise ValueError(e)
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

    def loan_book_logic(self, book_title, name, email):
        """
        השאלת ספר:
        - חובה שהערך של copies גדול ממספר הספרים המושאלים.
        - חובה שהערך של is_loaned הוא "No".
        """
        try:
            # קריאה של כל הספרים מקובץ books.csv
            with open(self.csv_manager.filepath, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                books = list(reader)

            # בדיקה אם הספר קיים
            book_found = False
            for book in books:
                if book["title"].strip().lower() == book_title.strip().lower():
                    book_found = True

                    # בדיקת תנאי ההשאלה
                    loaned_copies = self.get_loaned_copies(book_title)
                    total_copies = int(book["copies"])

                    if loaned_copies == total_copies:
                        book["is_loaned"] = "Yes"
                        self.add_one_to_popularBooks(book_title)
                        self.add_to_waiting_list(book_title, name, email)
                        raise ValueError(f"The book '{book_title}' is fully loaned and cannot be borrowed.")


                    if book["is_loaned"].strip().lower() == "yes":
                        self.add_to_waiting_list(book_title, name, email)
                        self.add_one_to_popularBooks(book_title)
                        raise ValueError(f"The book '{book_title}' is marked as fully loaned.")


                    # עדכון במסמך loaned_books.csv
                    self.update_loaned_books(book_title)
                    self.add_one_to_popularBooks(book_title)

                    # עדכון הערך של is_loaned ב-books.csv אם כל העותקים הושאלו
                    if loaned_copies + 1 >= total_copies:
                        book["is_loaned"] = "Yes"

                    break

            if not book_found:
                raise ValueError(f"Book '{book_title}' not found in the library.")

            # כתיבה מחדש של books.csv עם הערך המעודכן של is_loaned
            with open(self.csv_manager.filepath, mode="w", encoding="utf-8", newline="") as file:
                fieldnames = ["title", "author", "is_loaned", "copies", "genre", "year"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(books)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"File error: {e}")
        except ValueError as e:
            raise ValueError(e)
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

    def add_one_to_popularBooks(self, book_title):
        """
        מוסיף נקודה לפופולריות של ספר בקובץ popular_books.csv.
        אם הקובץ לא קיים, הוא ייווצר עם הספר.
        אם הספר לא קיים בקובץ, הוא יתווסף עם פופולריות ראשונית של 1.
        """
        popular_books_file = "popular_books.csv"

        # יצירת קובץ אם הוא לא קיים
        if not os.path.exists(popular_books_file):
            with open(popular_books_file, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["title", "popularity"])  # כותרות הקובץ

        # קריאת הקובץ אם קיים
        popular_books = []
        book_found = False
        if os.path.exists(popular_books_file):
            with open(popular_books_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                popular_books = list(reader)

            # עדכון פופולריות אם הספר כבר קיים
            for book in popular_books:
                if book["title"].strip().lower() == book_title.strip().lower():
                    book["popularity"] = str(int(book["popularity"]) + 1)
                    book_found = True
                    break

        # אם הספר לא נמצא, הוספה לרשימה
        if not book_found:
            popular_books.append({"title": book_title, "popularity": "1"})

        # כתיבה מחדש של הקובץ
        with open(popular_books_file, mode="w", newline="", encoding="utf-8") as file:
            fieldnames = ["title", "popularity"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(popular_books)

    def get_popular_books(self):
        """
        מחזירה את עשרת הספרים הפופולריים ביותר מתוך popular_books.csv.
        """
        popular_books_file = "popular_books.csv"

        try:
            # קריאה מקובץ popular_books.csv
            if not os.path.exists(popular_books_file):
                raise FileNotFoundError(f"The file '{popular_books_file}' does not exist.")

            with open(popular_books_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                books = list(reader)

            # מיון הספרים לפי הפופולריות בסדר יורד
            sorted_books = sorted(books, key=lambda x: int(x["popularity"]), reverse=True)

            # החזרת עשרת הספרים הראשונים
            return sorted_books[:10]

        except FileNotFoundError as e:
            print(f"Error: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []

    def add_to_waiting_list(self, book_title, name, email):
        """
        מוסיף משתמש לרשימת ההמתנה בקובץ waiting_list.csv.
        אם הקובץ לא קיים, ייווצר עם השדות המתאימים.
        אם המשתמש כבר רשום לרשימת המתנה עבור אותו הספר, הרשומה לא תתווסף.
        """
        waiting_list_file = "waiting_list.csv"

        # יצירת קובץ אם הוא לא קיים
        if not os.path.exists(waiting_list_file):
            with open(waiting_list_file, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Book Title", "Name", "Email"])  # כותרות הקובץ

        # בדיקת כפילויות
        already_in_list = False
        if os.path.exists(waiting_list_file):
            with open(waiting_list_file, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)  # דילוג על כותרות
                for row in reader:
                    if row[0].strip().lower() == book_title.strip().lower() and \
                            row[1].strip().lower() == name.strip().lower() and \
                            row[2].strip().lower() == email.strip().lower():
                        already_in_list = True
                        break

        # הוספת המשתמש אם הוא לא ברשימה
        if not already_in_list:
            with open(waiting_list_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([book_title, name, email])

    def get_loaned_copies(self, book_title):
        """בודקת כמה עותקים כבר מושאלים מתוך loaned_books.csv"""
        try:
            with open("loaned_books.csv", mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["title"].lower() == book_title.lower():
                        return int(row["copies_loaned"])
        except FileNotFoundError:
            return 0  # אם אין קובץ, אף עותק לא הושאל עדיין
        return 0

    def update_is_loaned_status(self, book_title):
        """
        משנה את הערך של is_loaned ל-"Yes" עבור ספר מסוים אם מספר העותקים הכולל שווה למספר העותקים המושאלים.
        """
        books_file = self.csv_manager.filepath  # הנתיב לקובץ books.csv
        loaned_books_file = "loaned_books.csv"  # הנתיב לקובץ loaned_books.csv

        # קריאת הספרים מקובץ books.csv
        with open(books_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            books = list(reader)

        # קריאת הספרים המושאלים מקובץ loaned_books.csv
        if not os.path.exists(loaned_books_file):
            loaned_books = []
        else:
            with open(loaned_books_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                loaned_books = list(reader)

        # חיפוש הספרים בשני הקבצים
        for book in books:
            if book["title"].strip().lower() == book_title.strip().lower():
                total_copies = int(book["copies"])
                loaned_copies = sum(
                    int(loaned_book["copies_loaned"])
                    for loaned_book in loaned_books
                    if loaned_book["title"].strip().lower() == book_title.strip().lower()
                )

                # אם כל העותקים הושאלו, עדכן את הערך של is_loaned ל-"Yes"
                if loaned_copies >= total_copies:
                    book["is_loaned"] = "Yes"
                break

        # כתיבה חזרה לקובץ books.csv
        with open(books_file, mode="w", encoding="utf-8", newline="") as file:
            fieldnames = ["title", "author", "is_loaned", "copies", "genre", "year"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(books)

    def update_loaned_books(self, book_title):
        """
        מעדכנת את מספר העותקים המושאלים עבור ספר מסוים בקובץ loaned_books.csv.
        """
        loaned_books_file = "loaned_books.csv"
        loaned_books = []

        try:
            # קריאה מקובץ loaned_books.csv אם הוא קיים
            if os.path.exists(loaned_books_file):
                with open(loaned_books_file, mode="r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    loaned_books = list(reader)

            # חיפוש הספר ברשימת המושאלים
            book_found = False
            for book in loaned_books:
                if book["title"].strip().lower() == book_title.strip().lower():
                    book_found = True
                    book["copies_loaned"] = str(int(book["copies_loaned"]) + 1)
                    break

            if not book_found:
                # אם הספר לא קיים, נוסיף רשומה חדשה
                loaned_books.append({
                    "title": book_title,
                    "copies_loaned": "1",
                })

            # כתיבה מחדש של loaned_books.csv
            with open(loaned_books_file, mode="w", encoding="utf-8", newline="") as file:
                fieldnames = ["title", "copies_loaned"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(loaned_books)

        except Exception as e:
            raise Exception(f"An error occurred while updating loaned books: {e}")


    def write_to_log(self, action, status, details=""):
        """כותבת פעולה לקובץ log"""
        log_entry = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ACTION: {action}, STATUS: {status}, DETAILS: {details}\n"
        with open("log.txt", mode="a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
