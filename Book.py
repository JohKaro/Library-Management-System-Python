class Book:
    def __init__(self, title, author, is_loaned, copies, genre, year):
        self.title = title
        self.author = author
        self.is_loaned = is_loaned
        self.copies = int(copies)
        self.genre = genre
        self.year = int(year)
        self.loaned_copies = int()
