import datetime

def write_to_log(action, status, details=""):
    """
    כותבת פעולה לקובץ log
    :param action: הפעולה שבוצעה (לדוגמה: "Add Book", "Search Book")
    :param status: המצב של הפעולה ("success" או "fail")
    :param details: פרטים נוספים על הפעולה (לדוגמה: שם הספר או הודעת שגיאה)
    """
    log_entry = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ACTION: {action}, STATUS: {status}, DETAILS: {details}\n"
    with open("log.txt", mode="a", encoding="utf-8") as log_file:
        log_file.write(log_entry)
