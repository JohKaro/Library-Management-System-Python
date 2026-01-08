import unittest
import os
import csv
from Librarian import Librarian
from CSVManager import CSVManager


class TestLibrarian(unittest.TestCase):
    def setUp(self):
        """
        המתודה setUp רצה לפני כל טסט.
        כאן ניצור קובץ CSV זמני לספרים לצורך הטסטים.
        """
        self.test_file = "test_books.csv"

        # נוודא שהקובץ לא קיים לפני יצירה (למקרה שנשאר מקודם)
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        # יוצרים קובץ CSV ריק עם כותרות מתאימות
        with open(self.test_file, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["title", "author", "is_loaned", "copies", "genre", "year"])

        # יצירת CSVManager עם הקובץ הזמני
        self.csv_manager = CSVManager(self.test_file)

        # יצירת אובייקט Librarian
        self.librarian = Librarian(self.csv_manager)

    def tearDown(self):
        """
        המתודה tearDown רצה אחרי כל טסט.
        כאן נמחק את קובץ ה-CSV הזמני כדי שהטסטים יהיו אטומיים.
        """
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_or_update_book(self):
        """טסט שבודק הוספה של ספר חדש"""
        new_book = {
            "title": "Test Book",
            "author": "Test Author",
            "is_loaned": "No",
            "copies": "1",
            "genre": "Fiction",
            "year": "2022"
        }

        # פעולה: הוספה/עדכון של הספר
        self.librarian.add_or_update_book(new_book)

        # קריאת הקובץ מחדש כדי לוודא שהספר נוסף
        with open(self.test_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            books_in_csv = list(reader)

        # בדיקה: מוודאים שהספר שהוספנו אכן נמצא בקובץ
        self.assertEqual(len(books_in_csv), 1, "אמור להיות ספר אחד בקובץ לאחר הוספה.")
        self.assertEqual(books_in_csv[0]["title"], "Test Book", "שם הספר בקובץ לא תואם לשם הספר שנוסף.")

        # בנוסף, אפשר לבדוק את המידע המלא
        self.assertEqual(books_in_csv[0]["author"], "Test Author")
        self.assertEqual(books_in_csv[0]["copies"], "1")
        self.assertEqual(books_in_csv[0]["is_loaned"], "No")
        self.assertEqual(books_in_csv[0]["genre"], "Fiction")
        self.assertEqual(books_in_csv[0]["year"], "2022")

    def test_loan_book_successful(self):
        """Test successful book loan when book is available"""
        # Add a book to the CSV first
        new_book = {
            "title": "Loan Test Book",
            "author": "Test Author",
            "is_loaned": "No",
            "copies": "3",
            "genre": "Fiction",
            "year": "2022"
        }
        self.librarian.add_or_update_book(new_book)

        # Attempt to loan the book
        try:
            self.librarian.loan_book_logic("Loan Test Book", "John Doe", "john@example.com")
        except Exception as e:
            self.fail(f"loan_book_logic raised an unexpected exception: {e}")

        # Verify book status in CSV
        with open(self.test_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            books = list(reader)
            loaned_book = next(book for book in books if book["title"] == "Loan Test Book")

            # Check that the copies are still correct
            self.assertEqual(loaned_book["copies"], "3", "Total number of copies should remain unchanged")

        # Verify loaned_books.csv was updated
        with open("loaned_books.csv", mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            loaned_books = list(reader)
            self.assertTrue(any(book["title"] == "Loan Test Book" for book in loaned_books),
                            "Book should be in loaned_books.csv")

    def test_loan_book_fully_loaned(self):
        """Test loaning a book when all copies are already loaned"""
        # Add a book with one copy and mark it as loaned
        new_book = {
            "title": "Fully Loaned Book",
            "author": "Test Author",
            "is_loaned": "Yes",
            "copies": "1",
            "genre": "Fiction",
            "year": "2022"
        }
        self.librarian.add_or_update_book(new_book)

        # Simulate that the book is already loaned
        with open("loaned_books.csv", mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["title", "copies_loaned"])
            writer.writerow(["Fully Loaned Book", "1"])

        # Attempt to loan the book should raise a ValueError
        with self.assertRaises(ValueError, msg="Should raise ValueError for fully loaned book"):
            self.librarian.loan_book_logic("Fully Loaned Book", "Jane Doe", "jane@example.com")

        # Verify waiting list was updated
        with open("waiting_list.csv", mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            waiting_entries = list(reader)
            self.assertTrue(
                any(entry[0] == "Fully Loaned Book" and entry[1] == "Jane Doe" for entry in waiting_entries),
                "User should be added to waiting list")

    def test_loan_book_nonexistent(self):
        """Test attempting to loan a book that doesn't exist"""
        with self.assertRaises(ValueError, msg="Should raise ValueError for non-existent book"):
            self.librarian.loan_book_logic("Nonexistent Book", "John Doe", "john@example.com")

    def test_multiple_book_loans(self):
        """Test loaning multiple copies of a book"""
        # Add a book with multiple copies
        new_book = {
            "title": "Multiple Copies Book",
            "author": "Test Author",
            "is_loaned": "No",
            "copies": "5",
            "genre": "Fiction",
            "year": "2022"
        }
        self.librarian.add_or_update_book(new_book)

        # Loan multiple copies
        for i in range(5):
            name = f"User {i + 1}"
            email = f"user{i + 1}@example.com"
            self.librarian.loan_book_logic("Multiple Copies Book", name, email)

        # Verify book status in CSV
        with open(self.test_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            books = list(reader)
            loaned_book = next(book for book in books if book["title"] == "Multiple Copies Book")

            # Check that the book is marked as fully loaned
            self.assertEqual(loaned_book["is_loaned"], "Yes", "Book should be marked as fully loaned")

        # Verify loaned_books.csv
        with open("loaned_books.csv", mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            loaned_books = list(reader)

            loaned_book_entry = next(book for book in loaned_books if book["title"] == "Multiple Copies Book")
            self.assertEqual(loaned_book_entry["copies_loaned"], "5", "All copies should be loaned")

    def test_loan_book_near_capacity(self):
        """
        Test loaning a book when it's close to being fully loaned
        Verify the is_loaned status changes correctly when almost all copies are borrowed
        """
        # Add a book with multiple copies
        new_book = {
            "title": "Near Capacity Book",
            "author": "Test Author",
            "is_loaned": "No",
            "copies": "3",
            "genre": "Fiction",
            "year": "2022"
        }
        self.librarian.add_or_update_book(new_book)

        # Loan two copies first
        self.librarian.loan_book_logic("Near Capacity Book", "User 1", "user1@example.com")
        self.librarian.loan_book_logic("Near Capacity Book", "User 2", "user2@example.com")

        # Verify book status before final loan
        with open(self.test_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            books = list(reader)
            near_capacity_book = next(book for book in books if book["title"] == "Near Capacity Book")

            self.assertEqual(near_capacity_book["is_loaned"], "No", "Book should not be fully loaned yet")

        # Loan the final copy
        self.librarian.loan_book_logic("Near Capacity Book", "User 3", "user3@example.com")

        # Verify final book status
        with open(self.test_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            books = list(reader)
            near_capacity_book = next(book for book in books if book["title"] == "Near Capacity Book")

            # Check that the book is now marked as fully loaned
            self.assertEqual(near_capacity_book["is_loaned"], "Yes", "Book should be marked as fully loaned")

        # Verify loaned_books.csv
        with open("loaned_books.csv", mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            loaned_books = list(reader)

            loaned_book_entry = next(book for book in loaned_books if book["title"] == "Near Capacity Book")
            self.assertEqual(loaned_book_entry["copies_loaned"], "3", "All copies should be loaned")

if __name__ == '__main__':
   unittest.main()