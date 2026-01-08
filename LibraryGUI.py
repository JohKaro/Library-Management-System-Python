import hashlib
import tkinter as tk
from tkinter import messagebox, ttk
import csv

from CSVManager import CSVManager
from Librarian import Librarian
from Search_Strategy import SearchStrategy
from User import User
from observer import Observer


class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # הסתרת החלון הראשי
        # אתחול של CSVManager
        self.csv_manager = CSVManager("books.csv")
        self.librarian = Librarian(self.csv_manager)  # אתחול של אובייקט Librarian
        self.observer = Observer()  # אתחול ה-Observer

        # קריאה למסך הכניסה
        self.show_login_screen()

    def show_library_screen(self):
        # כותרת ראשית
        title_label = tk.Label(self.root, text="Welcome to the Library Management System!", font=("Arial", 16))
        title_label.pack(pady=10)

        # כפתורים
        button_texts = [
            "Add Book", "Remove Book", "View Books",
            "Lend Book", "Return Book", "Popular Books", "Search Books"
        ]
        for text in button_texts:
            button = tk.Button(self.root, text=text, font=("Arial", 14),
                               command=lambda t=text: self.button_action(t))
            button.pack(pady=5)

        # כפתור יציאה
        logout_button = tk.Button(self.root, text="Logout", font=("Arial", 14), command=self.logout)
        logout_button.pack(pady=10)

#כל הכפתורים למעט כפתור התנתקות שנמצא למעלה - הוא יוצא למסך הבית
    def button_action(self, action):
        if action.lower() == "view books":
            self.show_books()
        elif action.lower() == "add book":
            self.add_book()
        elif action.lower() == "remove book":
            self.remove_book()
        elif action.lower() == "lend book":
            self.lend_book()
        elif action.lower() == "return book":
            self.return_book()
        elif action.lower() == "search books":
            self.search_book()
        elif action.lower() == "popular books":
            self.show_popular_book()
        else:
            messagebox.showinfo("Action", f"You clicked '{action}'")

    def search_book(self):
        # יצירת חלון חיפוש
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Book")
        search_window.geometry("400x250")

        tk.Label(search_window, text="Search for a Book", font=("Arial", 16)).pack(pady=10)

        # שדה הזנת הטקסט לחיפוש
        tk.Label(search_window, text="Enter search term:", font=("Arial", 12)).pack(pady=5)
        search_entry = tk.Entry(search_window, font=("Arial", 12))
        search_entry.pack(pady=10)

        # שדה לבחירת קריטריון החיפוש
        tk.Label(search_window, text="Search by:", font=("Arial", 12)).pack(pady=5)
        search_options = ["name", "Genre", "Author", "Year"]
        search_criteria = tk.StringVar(value="name")  # ברירת מחדל: "Title"
        criteria_menu = ttk.Combobox(search_window, textvariable=search_criteria, values=search_options,
                                     state="readonly", font=("Arial", 12))
        criteria_menu.pack(pady=10)

        # כפתור לחיפוש
        tk.Button(
            search_window,
            text="Search",
            font=("Arial", 14),
            command=lambda: self.perform_search(search_entry.get(), search_criteria.get(), search_window)
        ).pack(pady=10)

        # כפתור לסגירת החלון
        tk.Button(
            search_window,
            text="Cancel",
            font=("Arial", 14),
            command=search_window.destroy
        ).pack(pady=10)

    def perform_search(self, search_term, search_field, search_window):
        try:
            # יצירת אובייקט של SearchStrategy
            search_strategy = SearchStrategy("books.csv")

            # קריאה למתודת החיפוש
            results = search_strategy.search_books(search_term, search_field)

            # הצגת התוצאות
            if results:
                self.librarian.write_to_log("Search", "success", f"Search for '{search_term}' by {search_field}")
                # יצירת חלון חדש להצגת התוצאות
                result_window = tk.Toplevel(self.root)
                result_window.title("Search Results")
                result_window.geometry("500x400")

                # יצירת כותרת לחלון
                tk.Label(result_window, text="Search Results", font=("Arial", 16)).pack(pady=10)

                # יצירת אזור תצוגה לגלילה
                text_frame = tk.Frame(result_window)
                text_frame.pack(fill=tk.BOTH, expand=True)

                # יצירת Widget לתצוגת התוצאות
                text_widget = tk.Text(text_frame, wrap="word", font=("Arial", 12), state="normal")
                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                # פס גלילה
                scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                text_widget.configure(yscrollcommand=scrollbar.set)

                # הוספת התוצאות לתוך הטקסט
                for result in results:
                    text_widget.insert(tk.END, result + "\n")

                # הגדרת Widget לטקסט לקריאה בלבד
                text_widget.configure(state="disabled")

            else:
                self.librarian.write_to_log("Search", "fail", f"No results for '{search_term}' by {search_field}")
                tk.messagebox.showinfo("Search Results", "No matching books found.")

        except FileNotFoundError:
            tk.messagebox.showerror("Error", "The file 'books.csv' was not found.")
        except Exception as e:
            self.librarian.write_to_log("Search", "fail", str(e))
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

    def return_book(self):
        # קריאת הספרים מקובץ loaned_books.csv
        try:
            with open("loaned_books.csv", mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                loaned_books = [row["title"] for row in reader if int(row["copies_loaned"]) > 0]

            if not loaned_books:
                tk.messagebox.showerror("Error", "No books available to return.")
                return

        except FileNotFoundError:
            tk.messagebox.showerror("Error", "The file 'loaned_books.csv' was not found.")
            return
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {e}")
            return

        # יצירת חלון חדש
        return_window = tk.Toplevel(self.root)
        return_window.title("Return a Book")
        return_window.geometry("400x300")

        # כותרת
        tk.Label(return_window, text="Return a Book", font=("Arial", 16)).pack(pady=10)

        # יצירת ComboBox לבחירת ספר להחזרה
        tk.Label(return_window, text="Select a Book:", font=("Arial", 12)).pack(pady=5)
        book_combo = ttk.Combobox(return_window, values=loaned_books, font=("Arial", 12), state="readonly")
        book_combo.pack(pady=10)
        book_combo.set("Select a Book")

        # כפתור להחזרת הספר
        tk.Button(
            return_window,
            text="Return",
            font=("Arial", 14),
            command=lambda: self.confirm_return_book(book_combo.get(), return_window)
        ).pack(pady=10)

        # כפתור לסגירת החלון
        tk.Button(
            return_window,
            text="Cancel",
            font=("Arial", 14),
            command=return_window.destroy
        ).pack(pady=10)

    def confirm_return_book(self, book_title, window):
        if book_title == "Select a Book":
            tk.messagebox.showwarning("Warning", "Please select a book to return.")
            return

        try:
            # קריאה למתודת ההחזרה במחלקת Librarian
            self.librarian.return_book_logic(book_title)
            self.librarian.write_to_log("Return Book", "success", f"Book returned: {book_title}")

            # הודעת הצלחה
            tk.messagebox.showinfo("Success", f"The book '{book_title}' has been successfully returned.")
            window.destroy()

        except ValueError as e:
            # טיפול בשגיאות לוגיות (למשל, ניסיון להחזיר ספר שלא הושאל)
            tk.messagebox.showerror("Error", str(e))
        except FileNotFoundError as e:
            # טיפול במקרה שהקובץ לא נמצא
            tk.messagebox.showerror("Error", f"File error: {e}")
        except Exception as e:
            # טיפול בשגיאה כללית
            self.librarian.write_to_log("Return Book", "fail", str(e))
            tk.messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def lend_book(self):
        # קריאת הספרים מקובץ CSV
        try:
            with open("books.csv", mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                books = [row["title"] for row in reader]

            if not books:
                tk.messagebox.showerror("Error", "No books available to lend.")
                return

        except FileNotFoundError:
            tk.messagebox.showerror("Error", "The file 'books.csv' was not found.")
            return
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {e}")
            return

        # יצירת חלון חדש
        lend_window = tk.Toplevel(self.root)
        lend_window.title("Lend a Book")
        lend_window.geometry("400x300")

        # כותרת
        tk.Label(lend_window, text="Lend a Book", font=("Arial", 16)).pack(pady=10)

        # שדה לבחירת ספר
        tk.Label(lend_window, text="Select a Book:", font=("Arial", 12)).pack(pady=5)
        book_combo = ttk.Combobox(lend_window, values=books, font=("Arial", 12), state="readonly")
        book_combo.pack(pady=10)
        book_combo.set("Select a Book")

        # שדה להזנת שם
        tk.Label(lend_window, text="Name:", font=("Arial", 12)).pack(pady=5)
        name_entry = tk.Entry(lend_window, font=("Arial", 12))
        name_entry.pack(pady=10)

        # שדה להזנת דוא"ל
        tk.Label(lend_window, text="Email:", font=("Arial", 12)).pack(pady=5)
        email_entry = tk.Entry(lend_window, font=("Arial", 12))
        email_entry.pack(pady=10)

        # כפתור לשאילת הספר
        tk.Button(
            lend_window,
            text="Lend",
            font=("Arial", 14),
            command=lambda: self.confirm_lend_book(book_combo.get(), name_entry.get(), email_entry.get(), lend_window)
        ).pack(pady=10)

        # כפתור לסגירת החלון
        tk.Button(
            lend_window,
            text="Cancel",
            font=("Arial", 14),
            command=lend_window.destroy
        ).pack(pady=10)

    def confirm_lend_book(self, book_title, name, email, window):
        """
        מאשרת השאלת ספר, שולחת את המידע למחלקת Librarian.
        :param book_title: כותרת הספר שנבחר
        :param name: שם המשתמש ששואל את הספר
        :param email: כתובת הדוא"ל של המשתמש
        :param window: חלון ההשאלה לסגירה לאחר פעולה
        """
        # בדיקת שדות חובה
        if book_title == "Select a Book":
            tk.messagebox.showwarning("Warning", "Please select a book to lend.")
            return

        if not name.strip():
            tk.messagebox.showwarning("Warning", "Please enter your name.")
            return

        if not email.strip():
            tk.messagebox.showwarning("Warning", "Please enter your email.")
            return

        try:
            # קריאה למתודה loan_book_logic ב-Librarian
            self.librarian.loan_book_logic(book_title, name, email)

            # הוספת פעולה ללוג
            self.librarian.write_to_log(
                action="Lend Book",
                status="success",
                details=f"Book: {book_title}, Borrower: {name}, Email: {email}",
            )

            # הודעת הצלחה
            tk.messagebox.showinfo("Success", f"You have successfully lent the book: '{book_title}' to {name}.")
            window.destroy()

        except Exception as e:
            # אם אין עותקים זמינים או הספר לא נמצא
            # תיעוד כישלון בלוג
            self.librarian.write_to_log("Lend Book", "fail", str(e))

            tk.messagebox.showerror("Error", f"An error occurred: {e}")

        except FileNotFoundError as e:
            # אם הקובץ books.csv לא נמצא
            # תיעוד כישלון בלוג
            self.librarian.write_to_log(action="Lend Book", status="fail", details=str(e))
            tk.messagebox.showerror("Error", f"File error: {e}")

        except Exception as e:
            # שגיאה כללית
            # תיעוד כישלון בלוג
            self.librarian.write_to_log(action="Lend Book", status="fail", details=str(e))
            tk.messagebox.showerror("Error", f"An unexpected erroroccurred:{e}")

    def remove_book(self):
        # יצירת חלון חדש
        remove_window = tk.Toplevel(self.root)
        remove_window.title("Remove a Book")
        remove_window.geometry("300x200")

        # כותרת
        tk.Label(remove_window, text="Remove a Book", font=("Arial", 16)).pack(pady=10)

        # שדה להזנת שם הספר
        frame = tk.Frame(remove_window)
        frame.pack(pady=5)
        tk.Label(frame, text="Title:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        title_entry = tk.Entry(frame, font=("Arial", 12))
        title_entry.pack(side=tk.LEFT, padx=5)

        # כפתור למחיקה
        tk.Button(
            remove_window,
            text="Remove",
            font=("Arial", 14),
            command=lambda: self.confirm_remove_book(title_entry.get(), remove_window)
        ).pack(pady=20)

        # כפתור לסגירת החלון
        tk.Button(
            remove_window,
            text="Cancel",
            font=("Arial", 14),
            command=remove_window.destroy
        ).pack(pady=10)

    def confirm_remove_book(self, title, window):
        # אישור המחיקה
        result = messagebox.askyesno("Confirm", f"Are you sure you want to remove one copy of '{title}'?")
        if result:
            try:
                # קריאה למתודה ב-Librarian להסרת עותק אחד
                book_updated = self.librarian.remove_book_copy(title)
                if book_updated:
                    self.librarian.write_to_log("Remove Book", "success", f"Book: {title}")
                    messagebox.showinfo("Success", f"One copy of '{title}' has been removed.")
                    window.destroy()
                else:
                    self.librarian.write_to_log("Remove Book", "fail", f"Book: {title} not found")
                    messagebox.showwarning("Not Found", f"Book '{title}' was not found in the library.")
            except Exception as e:
                self.librarian.write_to_log("Remove Book", "fail", str(e))
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            self.librarian.write_to_log("Remove Book", "cancelled", f"Removal of '{title}' was cancelled.")

    def add_book(self):
        # יצירת חלון חדש
        add_window = tk.Toplevel(self.root)
        add_window.title("Add a New Book")
        add_window.geometry("400x400")

        # כותרת
        tk.Label(add_window, text="Add a New Book", font=("Arial", 16)).pack(pady=10)

        # יצירת שדות להזנה
        fields = ["Title", "Author", "Year"]
        entries = {}
        for field in fields:
            frame = tk.Frame(add_window)
            frame.pack(pady=5)
            tk.Label(frame, text=f"{field}:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(frame, font=("Arial", 12))
            entry.pack(side=tk.LEFT, padx=5)
            entries[field.lower()] = entry

        # יצירת Frame ו-ComboBox עבור הז'אנר
        frame = tk.Frame(add_window)
        frame.pack(pady=5)
        tk.Label(frame, text="Genre:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

        # רשימה ידנית של ז'אנרים
        genres = ["Fiction", "Adventure", "Dystopian", "Fantasy", "Classic", "Romance"]

        # יצירת ComboBox עם רשימת הז'אנרים
        genre_combo = ttk.Combobox(frame, values=genres, font=("Arial", 12), state="readonly")
        genre_combo.set("Select a Genre")  # ערך ברירת מחדל
        genre_combo.pack(side=tk.LEFT, padx=5)
        entries["genre"] = genre_combo  # מוסיפים את ה-ComboBox למילון השדות

        # כפתור לשמירה (הלוגיקה תתווסף מאוחר יותר)
        tk.Button(
            add_window,
            text="Save",
            font=("Arial", 14),
            command=lambda: self.save_book(entries)
        ).pack(pady=20)

        # כפתור לסגירת החלון
        tk.Button(
            add_window,
            text="Cancel",
            font=("Arial", 14),
            command=add_window.destroy
        ).pack(pady=10)

    # מתודת שמירה (תוסיף לוגיקה מאוחר יותר)
    def save_book(self, entries):
        # איסוף הנתונים מהשדות
        new_book = {
            "title": entries["title"].get(),
            "author": entries["author"].get(),
            "genre": entries["genre"].get(),
            "year": entries["year"].get(),
            "is_loaned": "No",  # ברירת מחדל: הספר אינו מושאל
            "copies": 1  # ברירת מחדל: עותק אחד
        }

        try:
            # שימוש במתודת Librarian כדי לשמור את הספר
            self.librarian.add_or_update_book(new_book)
            self.librarian.write_to_log("Add Book", "success", f"Book added: {new_book['title']}")
            messagebox.showinfo("Success", "Book added or updated successfully!")
        except Exception as e:
            self.librarian.write_to_log("Add Book", "fail", str(e))
            messagebox.showerror("Error", f"An error occurred while saving the book: {e}")

    def update_books_table(self, books_window, books):
        """מעדכן את תצוגת הספרים בטבלה"""
        # הסרת טבלה קיימת אם יש
        for widget in books_window.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()

        # יצירת מסגרת חדשה לטבלה
        container = tk.Frame(books_window)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # הוספת כותרות
        headers = ["Title", "Author", "Is Loaned", "Copies", "Genre", "Year"]
        for col_num, header in enumerate(headers):
            tk.Label(scrollable_frame, text=header, font=("Arial", 12, "bold"), borderwidth=1, relief="solid").grid(
                row=0, column=col_num, sticky="nsew", padx=2, pady=2)

        # הוספת נתונים לטבלה
        for row_num, book in enumerate(books, start=1):
            tk.Label(scrollable_frame, text=book["title"], font=("Arial", 10), borderwidth=1, relief="solid").grid(
                row=row_num, column=0, sticky="nsew", padx=2, pady=2)
            tk.Label(scrollable_frame, text=book["author"], font=("Arial", 10), borderwidth=1, relief="solid").grid(
                row=row_num, column=1, sticky="nsew", padx=2, pady=2)
            tk.Label(scrollable_frame, text=book["is_loaned"], font=("Arial", 10), borderwidth=1, relief="solid").grid(
                row=row_num, column=2, sticky="nsew", padx=2, pady=2)
            tk.Label(scrollable_frame, text=book["copies"], font=("Arial", 10), borderwidth=1, relief="solid").grid(
                row=row_num, column=3, sticky="nsew", padx=2, pady=2)
            tk.Label(scrollable_frame, text=book["genre"], font=("Arial", 10), borderwidth=1, relief="solid").grid(
                row=row_num, column=4, sticky="nsew", padx=2, pady=2)
            tk.Label(scrollable_frame, text=book["year"], font=("Arial", 10), borderwidth=1, relief="solid").grid(
                row=row_num, column=5, sticky="nsew", padx=2, pady=2)

    def show_books(self):
        try:
            # קריאה לקובץ ושמירת הספרים במשתנה מרכזי
            with open("books.csv", mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.all_books = list(reader)

            # יצירת חלון להצגת הספרים
            books_window = tk.Toplevel(self.root)
            books_window.title("Books List")
            books_window.geometry("1200x700")

            # יצירת טבלה
            self.table_frame = tk.Frame(books_window)
            self.table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # מסגרת לסינון
            filter_frame = tk.Frame(books_window, bg="lightgray", relief=tk.RAISED, bd=2)
            filter_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

            # רכיבי ממשק לסינון
            tk.Label(filter_frame, text="Filter Books", font=("Arial", 14, "bold"), bg="lightgray").pack(pady=10)

            # בחירת קטגוריה
            tk.Label(filter_frame, text="Select Filter Category:", font=("Arial", 12), bg="lightgray").pack(pady=5)
            categories = ["All Books", "Genre", "Author", "Year"]
            self.selected_category = tk.StringVar(value=categories[0])
            category_menu = ttk.Combobox(filter_frame, values=categories, textvariable=self.selected_category,
                                         state="readonly")
            category_menu.pack(pady=5)

            # בחירת ערכים מתוך הרשימה
            tk.Label(filter_frame, text="Select Options:", font=("Arial", 12), bg="lightgray").pack(pady=5)
            self.listbox = tk.Listbox(filter_frame, selectmode=tk.MULTIPLE, height=15, font=("Arial", 12),
                                      exportselection=0)
            self.listbox.pack(pady=5, fill=tk.BOTH)

            # Binding לעדכון הרשימה כשמשנים קטגוריה
            category_menu.bind("<<ComboboxSelected>>", self.update_listbox)

            # בחירת סינון מתקדם
            tk.Label(filter_frame, text="Select Filter Advanced:", font=("Arial", 12), bg="lightgray").pack(pady=5)
            filter_options = ["All Books", "Available Books", "Borrowed Books", "Popular Books"]
            self.selected_filter = tk.StringVar(value=filter_options[0])
            filter_menu = ttk.Combobox(filter_frame, values=filter_options, textvariable=self.selected_filter,
                                       state="readonly")
            filter_menu.pack(pady=5)

            # כפתור לסינון
            tk.Button(
                filter_frame,
                text="Apply Filter",
                font=("Arial", 12),
                command=self.apply_filters
            ).pack(pady=10)

            # כפתור לאיפוס הסינון
            tk.Button(
                filter_frame,
                text="Reset Filter",
                font=("Arial", 12),
                command=lambda: self.update_books_table(self.table_frame, self.all_books)
            ).pack(pady=10)

            # הצגת כל הספרים בטבלה
            self.update_books_table(self.table_frame, self.all_books)

        except FileNotFoundError:
            tk.messagebox.showerror("Error", "The file 'books.csv' was not found.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

    def update_listbox(self, event=None):
        """מעדכנת את תיבת הבחירה לפי הקטגוריה שנבחרה."""
        selected_category = self.selected_category.get().lower()
        options = list(set(book[selected_category] for book in self.all_books if selected_category in book))
        options.sort()
        self.listbox.delete(0, tk.END)
        for option in options:
            self.listbox.insert(tk.END, option)

    def apply_filters(self):
        """מבצעת את כל הסינונים ומעדכנת את הטבלה."""
        try:
            # התחלה עם כל הספרים
            filtered_books = self.all_books

            # כתיבת התחלת תהליך ללוג
            self.librarian.write_to_log("Apply Filters", "start", "Starting filter process.")

            # סינון לפי קטגוריה
            selected_indices = self.listbox.curselection()
            selected_options = [self.listbox.get(i) for i in selected_indices]
            if selected_options:
                category = self.selected_category.get().lower()
                filtered_books = [book for book in filtered_books if book[category] in selected_options]
                self.librarian.write_to_log("Apply Filters", "success", f"Filtered books by category: {category}.")

            # סינון לפי אפשרות מתקדמת
            advanced_filter = self.selected_filter.get()
            if advanced_filter == "Available Books":
                filtered_books = [book for book in filtered_books if book["is_loaned"].lower() == "no"]
            elif advanced_filter == "Borrowed Books":
                filtered_books = [book for book in filtered_books if book["is_loaned"].lower() == "yes"]
            elif advanced_filter == "Popular Books":
                filtered_books = sorted(filtered_books, key=lambda x: int(x.get("copies_loaned", 0)), reverse=True)[:10]
            elif advanced_filter == "All Books":
                self.librarian.write_to_log("Apply Filters", "info", "Displayed all books without advanced filter.")

            # עדכון הטבלה
            self.update_books_table(self.table_frame, filtered_books)
            self.librarian.write_to_log("Apply Filters", "success",
                                        f"Displayed {len(filtered_books)} books after filtering.")

        except Exception as e:
            self.librarian.write_to_log("Apply Filters", "fail", str(e))
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

    def filter_books_advanced(self, listbox, category, filter_advance, books_window, table_frame):
        """
        מסננת ספרים לפי קטגוריה ואפשרויות מתקדמות (זמינות/פופולריות/מושאלים).
        """
        try:
            with open("books.csv", mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                filtered_books = list(reader)

            # התחלת התהליך
            self.librarian.write_to_log("Advanced Filter", "start",
                                        f"Started advanced filtering with category: {category}, filter: {filter_advance}")

            # סינון לפי קטגוריה
            if category:
                selected_indices = self.listbox.curselection()
                selected_options = [self.listbox.get(i) for i in selected_indices]
                if selected_options:
                    filtered_books = [
                        book for book in filtered_books
                        if str(book[category.lower()]) in selected_options
                    ]
                    self.librarian.write_to_log("Advanced Filter", "success",
                                                f"Filtered books by category: {category}.")

            # סינון מתקדם
            if filter_advance:
                if filter_advance == "Available Books":
                    filtered_books = [book for book in filtered_books if book["is_loaned"].lower() == "no"]
                elif filter_advance == "Borrowed Books":
                    filtered_books = [book for book in filtered_books if book["is_loaned"].lower() == "yes"]
                elif filter_advance == "Popular Books":
                    filtered_books = sorted(filtered_books, key=lambda x: int(x.get("copies_loaned", 0) or "0"),
                                            reverse=True)[:10]
                elif filter_advance == "All Books":
                    self.librarian.write_to_log("Advanced Filter", "info",
                                                "Displayed all books without advanced filtering.")

            # עדכון טבלה עם התוצאות
            self.update_books_table(self.table_frame, filtered_books)

            # כתיבה ללוג
            self.librarian.write_to_log("Advanced Filter", "success",
                                        f"Displayed {len(filtered_books)} books after filtering.")

        except Exception as e:
            self.librarian.write_to_log("Advanced Filter", "fail", str(e))
            tk.messagebox.showerror("Error", f"An error occurred: {e}")


    def logout(self):
        # הצגת הודעת אישור
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if result:
            try:
                # ניקוי המסך הראשי
                for widget in self.root.winfo_children():
                    widget.destroy()

                # הסתרת המסך הראשי
                self.root.withdraw()
                self.librarian.write_to_log("Logout", "success", "User logged out successfully.")

                # פתיחת מסך ההתחברות מחדש
                self.show_login_screen()

            except Exception as e:
                self.librarian.write_to_log("Logout", "fail", str(e))

    #login screen
    def show_login_screen(self):
        # יצירת מסך כניסה
        login_window = tk.Toplevel(self.root)
        login_window.title("Log In")
        login_window.geometry("300x250")

        tk.Label(login_window, text="Log In", font=("Arial", 16)).pack(pady=10)

        # שדות הזנה לשם משתמש וסיסמה
        tk.Label(login_window, text="Username:", font=("Arial", 12)).pack(pady=5)
        username_entry = tk.Entry(login_window, font=("Arial", 12))
        username_entry.pack(pady=5)

        tk.Label(login_window, text="Password:", font=("Arial", 12)).pack(pady=5)
        password_entry = tk.Entry(login_window, font=("Arial", 12), show="*")
        password_entry.pack(pady=5)

        # כפתור התחברות
        tk.Button(
            login_window,
            text="Log In",
            font=("Arial", 12),
            command=lambda: self.login_user(username_entry.get(), password_entry.get(), login_window)
        ).pack(pady=10)

        # כפתור הרשמה
        tk.Button(
            login_window,
            text="Register",
            font=("Arial", 12),
            command=self.show_register_screen  # תיקון הקריאה
        ).pack(pady=5)

    def show_register_screen(self):
        # יצירת חלון הרשמה
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")
        register_window.geometry("300x250")

        tk.Label(register_window, text="Register", font=("Arial", 16)).pack(pady=10)

        # שדות הזנה לשם משתמש וסיסמה
        tk.Label(register_window, text="New Username:", font=("Arial", 12)).pack(pady=5)
        username_entry = tk.Entry(register_window, font=("Arial", 12))
        username_entry.pack(pady=5)

        tk.Label(register_window, text="New Password:", font=("Arial", 12)).pack(pady=5)
        password_entry = tk.Entry(register_window, font=("Arial", 12), show="*")
        password_entry.pack(pady=5)

        # כפתור הרשמה
        tk.Button(
            register_window,
            text="Register",
            font=("Arial", 12),
            command=lambda: self.register_user_logic(username_entry.get(), password_entry.get(), register_window)
        ).pack(pady=10)

        # כפתור לסגירת החלון
        tk.Button(
            register_window,
            text="Cancel",
            font=("Arial", 12),
            command=register_window.destroy
        ).pack(pady=5)

    def login_user(self, username, password, login_window):
        if not username or not password:
            tk.messagebox.showwarning("Warning", "Please enter both username and password.")
            return

        try:
            # קריאה מקובץ users.csv
            with open("users.csv", mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                user_found = False

                # בדיקת שם משתמש וסיסמה
                for row in reader:
                    if row["username"] == username:
                        hashed_password = hashlib.sha256(password.encode()).hexdigest()
                        if row["password"] == hashed_password:
                            user_found = True
                            break

            # בדיקת שם משתמש וסיסמה
            if user_found:
                self.librarian.write_to_log("Login", "success", f"User logged in: {username}")
                tk.messagebox.showinfo("Success", "Login successful!")
                login_window.destroy()  # סגירת חלון ההתחברות
                self.root.deiconify()  # הצגת החלון הראשי
                self.show_library_screen()  # פתיחת מסך הספרייה

                message = self.observer.get_notification(username)

                if message:
                    tk.messagebox.showinfo("Notification", message)
                    # הסרת ספרים מהרשימה עבור המשתמש
                    for line in message.split("\n"):
                        book_title = line.split("'")[1]  # חילוץ שם הספר מההודעה
                        self.observer.remove_book_from_waiting_list(book_title)
                else:
                    tk.messagebox.showinfo("Notification", "No new notifications.")  # השתמש ב-showinfo להודעה נעימה יותר

            else:

                self.librarian.write_to_log("Login", "fail", f"Invalid login attempt: {username}")
                tk.messagebox.showerror("Error", "Invalid username or password.")

        except FileNotFoundError:
            tk.messagebox.showerror("Error", "No users found. Please register first.")
        except Exception as e:
            self.librarian.write_to_log("Login", "fail", str(e))
            tk.messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def register_user_logic(self, username, password, register_window):
        if not username or not password:
            tk.messagebox.showwarning("Warning", "Please enter both username and password.")
            return

        try:
            # יצירת אובייקט משתמש חדש
            new_user = User(username, password)

            # קריאה למתודה create_user מתוך מחלקת User
            new_user.create_user()

            # הודעת הצלחה
            tk.messagebox.showinfo("Success", f"User '{username}' registered successfully!")
            register_window.destroy()  # סגירת חלון ההרשמה
            self.librarian.write_to_log("Register", "success", f"User registered: {username}")

        except Exception as e:
            self.librarian.write_to_log("Register", "fail", str(e))
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

    def show_popular_book(self):
        """
        פותחת חלון חדש ומציגה טבלה עם עשרת הספרים הכי פופולריים מתוך popular_books.csv.
        """
        try:
            # קריאה ל-get_popular_books לקבלת הספרים הפופולריים
            try:
                popular_books = self.librarian.get_popular_books()
            except Exception as e:
                self.librarian.write_to_log("Display Popular Books", "fail", f"Error retrieving popular books: {e}")
                tk.messagebox.showerror("Error", "Failed to retrieve popular books.")
                return

            # בדיקה אם אין נתונים להצגה
            if not popular_books:
                self.librarian.write_to_log("Display Popular Books", "fail", "No popular books to display.")
                tk.messagebox.showinfo("No Data", "There are no popular books to display.")
                return

            # יצירת חלון חדש
            window = tk.Toplevel(self.root)
            window.title("Top 10 Popular Books")
            window.geometry("600x400")

            # כותרת
            tk.Label(window, text="Top 10 Popular Books", font=("Arial", 16, "bold")).pack(pady=10)

            # יצירת טבלה להצגת הספרים
            tree = ttk.Treeview(window, columns=("Title", "Popularity"), show="headings", height=10)
            tree.heading("Title", text="Title")
            tree.heading("Popularity", text="Popularity")

            # הגדרת רוחב עמודות
            tree.column("Title", width=400)
            tree.column("Popularity", width=100)

            # הכנסת הנתונים לטבלה
            try:
                for book in popular_books:
                    # טיפול בנתונים חסרים
                    title = book.get("title", "Unknown")
                    popularity = book.get("popularity", "0")
                    tree.insert("", "end", values=(title, popularity))

                # הצגת הטבלה
                tree.pack(pady=10)

                # כתיבת הצלחה ללוג
                self.librarian.write_to_log("Display Popular Books", "success", "Displayed popular books successfully.")

            except Exception as e:
                self.librarian.write_to_log("Display Popular Books", "fail", f"Error inserting data into table: {e}")
                tk.messagebox.showerror("Error", f"An error occurred while displaying the books: {e}")
                return

            # כפתור לסגירת החלון
            tk.Button(window, text="Close", command=window.destroy, font=("Arial", 12)).pack(pady=10)

        except Exception as e:
            # כתיבת שגיאה ללוג
            self.librarian.write_to_log("Display Popular Books", "fail", f"An unexpected error occurred: {e}")
            tk.messagebox.showerror("Error", f"An unexpected error occurred: {e}")


# הפעלת התוכנית
if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryGUI(root)
    root.mainloop()