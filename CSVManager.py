import csv
from Book import Book

class CSVManager:
    def __init__(self, filepath):
        self.filepath = filepath

    def load_books(self):
        books = []
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    books.append(Book(
                        title=row["title"],
                        author=row["author"],
                        is_loaned=row["is_loaned"],
                        copies=row["copies"],
                        genre=row["genre"],
                        year=row["year"]
                    ))
        except FileNotFoundError:
            print(f"Error: File '{self.filepath}' not found.")
        return books

    def save_books(self, books):
        with open(self.filepath, mode='w', encoding='utf-8', newline='') as file:
            fieldnames = ["title", "author", "is_loaned", "copies", "genre", "year"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for book in books:
                writer.writerow({
                    "title": book.title,
                    "author": book.author,
                    "is_loaned": "Yes" if book.is_loaned else "No",
                    "copies": book.copies,
                    "genre": book.genre,
                    "year": book.year
                })

    def delete_book(self, title_to_delete):
        books = self.load_books()  # טוען את כל הספרים מקובץ ה-CSV
        updated_books = [book for book in books if book.title.lower() != title_to_delete.lower()]

        if len(books) == len(updated_books):
            return False  # לא נמצא ספר למחיקה
        else:
            self.save_books(updated_books)  # שומר את הרשימה המעודכנת בחזרה לקובץ
            return True  # הספר נמחק בהצלחה
