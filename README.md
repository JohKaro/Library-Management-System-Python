# Library Management System (Python)

##  Overview
A robust digital library management system developed in Python. The application provides a comprehensive solution for managing book inventories, tracking loans, and user registrations through an intuitive Graphical User Interface (GUI).

##  Key Features
- **Inventory Management:** Add, update, and remove books from the library database.
- **Loan Tracking:** Streamlined process for borrowing and returning books with automated status updates.
- **Smart Search:** Advanced search functionality using various criteria (Title, Author, Genre).
- **User Authentication:** Secure Login/Register system for librarians and users.
- **Waitlist Management:** Automated notifications for users on waiting lists when books become available.

##  Architecture & Design Patterns
This project emphasizes clean code and scalable architecture:
- **Design Patterns:** - **Strategy Pattern:** Implemented for the search engine to allow flexible search algorithms.
    - **Observer Pattern:** Used to notify users when a book's availability changes.
- **Data Persistence:** Managed via a custom `CSVManager` class that ensures data is saved and retrieved efficiently from CSV files.
- **GUI:** Built with Python's **Tkinter** library for a lightweight and responsive interface.

##  Technologies Used
- **Language:** Python
- **GUI Library:** Tkinter
- **Data Storage:** CSV (File-based database)
- **Concepts:** Object-Oriented Programming (OOP), Design Patterns, Exception Handling.

##  How to Run
1. Clone the repository:
   ```bash
   git clone [https://github.com/JohKaro/Library-Management-System-Python.git](https://github.com/JohKaro/Library-Management-System-Python.git)
