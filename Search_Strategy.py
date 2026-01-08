import csv


class SearchStrategy:
    def __init__(self, filepath):
        self.filepath = filepath

    def _load_books(self):
        """מתודה פרטית לטעינת הספרים כגenerator"""
        try:
            with open(self.filepath, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    yield row
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{self.filepath}' was not found.")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

    def search_books(self, search_term, search_field):
        """
        חיפוש ספרים לפי מונח שדה
        :param search_term: מונח החיפוש
        :param search_field: השדה בו מתבצע החיפוש (title, genre, author, year)
        :return: רשימה של תוצאות תואמות
        """
        field_map = {"Title": "title", "Genre": "genre", "Author": "author", "Year": "year"}
        search_field = field_map.get(search_field, "title")  # ברירת מחדל: חיפוש לפי שם
        search_term = search_term.lower()

        # חיפוש עם איטרטור
        results = (
            f"{row['title']} by {row['author']} ({row['year']}) - {row['genre']}"
            for row in self._load_books()
            if search_term in row[search_field].lower()
        )
        return list(results)

    def search_by_multiple_fields(self, search_criteria):
        """
        חיפוש חכם במספר שדות בו זמנית
        :param search_criteria: מילון של {שדה: ערך לחיפוש}
        :return: רשימה של תוצאות תואמות
        """
        search_criteria = {k.lower(): v.lower() for k, v in search_criteria.items()}  # נורמליזציה של קלט
        results = []

        for row in self._load_books():
            match = all(search_criteria[key] in row[key].lower() for key in search_criteria if key in row)
            if match:
                results.append(
                    f"{row['title']} by {row['author']} ({row['year']}) - {row['genre']}"
                )

        return results