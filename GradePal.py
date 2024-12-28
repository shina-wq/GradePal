import sqlite3
from datetime import datetime, timedelta

# Database setup
def initialize_database():
    connection = sqlite3.connect("grade_tracker.db")
    cursor = connection.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS classes (
                        class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        class_name TEXT NOT NULL,
                        goal REAL DEFAULT 85.0,
                        current_avg REAL DEFAULT 0.0)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS grades (
                        grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        class_id INTEGER,
                        assignment_name TEXT,
                        grade REAL,
                        weight REAL,
                        FOREIGN KEY (class_id) REFERENCES classes(class_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS assignments (
                        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        class_id INTEGER,
                        title TEXT,
                        due_date TEXT,
                        status TEXT CHECK(status IN ('pending', 'completed')) DEFAULT 'pending',
                        FOREIGN KEY (class_id) REFERENCES classes(class_id))''')

    connection.commit()
    connection.close()

# Add a class with year and term
def add_class(class_name, year, term):
    connection = sqlite3.connect("grade_tracker.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO classes (class_name, year, term) VALUES (?, ?, ?)", (class_name, year, term))
    connection.commit()
    connection.close()

# Add a grade
def add_grade(class_id, assignment_name, grade, weight):
    connection = sqlite3.connect("grade_tracker.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO grades (class_id, assignment_name, grade, weight) VALUES (?, ?, ?, ?)",
                   (class_id, assignment_name, grade, weight))
    connection.commit()
    connection.close()

# Add an assignment
def add_assignment(class_id, title, due_date):
    connection = sqlite3.connect("grade_tracker.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO assignments (class_id, title, due_date) VALUES (?, ?, ?)",
                   (class_id, title, due_date))
    connection.commit()
    connection.close()

# Calculate weighted average for a class
def calculate_weighted_average(class_id):
    connection = sqlite3.connect("grade_tracker.db")
    cursor = connection.cursor()
    cursor.execute("SELECT grade, weight FROM grades WHERE class_id = ?", (class_id,))
    grades = cursor.fetchall()

    total_weighted_score = sum(grade * weight / 100 for grade, weight in grades)
    total_weight = sum(weight for _, weight in grades)

    if total_weight == 0:
        average = 0
    else:
        average = total_weighted_score / total_weight * 100

    cursor.execute("UPDATE classes SET current_avg = ? WHERE class_id = ?", (average, class_id))
    connection.commit()
    connection.close()
    return average

# Calculate GPA for a term (average of all classes in the term)
def calculate_term_gpa(year, term):
    connection = sqlite3.connect("grade_tracker.db")
    cursor = connection.cursor()
    cursor.execute("SELECT class_id FROM classes WHERE year = ? AND term = ?", (year, term))
    class_ids = cursor.fetchall()

    total_gpa = 0
    total_classes = len(class_ids)

    for class_id_tuple in class_ids:
        class_id = class_id_tuple[0]
        average = calculate_weighted_average(class_id)
        total_gpa += average

    if total_classes == 0:
        term_gpa = 0
    else:
        term_gpa = total_gpa / total_classes

    connection.close()
    return term_gpa

# Calculate overall GPA for all years and terms
def calculate_program_gpa():
    connection = sqlite3.connect("grade_tracker.db")
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT year, term FROM classes")
    years_terms = cursor.fetchall()

    total_gpa = 0
    total_terms = 0

    for year, term in years_terms:
        term_gpa = calculate_term_gpa(year, term)
        total_gpa += term_gpa
        total_terms += 1

    if total_terms == 0:
        program_gpa = 0
    else:
        program_gpa = total_gpa / total_terms

    connection.close()
    return program_gpa

# Get assignments due soon
def get_upcoming_assignments():
    connection = sqlite3.connect("grade_tracker.db")
    cursor = connection.cursor()
    cursor.execute("SELECT title, due_date FROM assignments WHERE status = 'pending'")
    assignments = cursor.fetchall()
    connection.close()

    today = datetime.now()
    upcoming = [(title, due_date) for title, due_date in assignments if datetime.strptime(due_date, "%Y-%m-%d") <= today + timedelta(days=7)]
    return upcoming

# Display GPA by year and term
def display_gpa_by_year_and_term():
    connection = sqlite3.connect("grade_tracker.db")
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT year, term FROM classes")
    years_terms = cursor.fetchall()

    for year, term in years_terms:
        term_gpa = calculate_term_gpa(year, term)
        print(f"Year {year}, Term {term} GPA: {term_gpa:.2f}")
    
    program_gpa = calculate_program_gpa()
    print(f"Overall GPA for the Program: {program_gpa:.2f}")

    connection.close()

# Main menu
def main():
    initialize_database()
    print("Welcome to the GradePal: Grade & Assignment Tracker!")

    while True:
        print("\nMenu:")
        print("1. Add a class")
        print("2. Add a grade")
        print("3. Add an assignment")
        print("4. Calculate class average")
        print("5. View upcoming assignments")
        print("6. View GPA by Year and Term")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            class_name = input("Enter class name: ")
            year = int(input("Enter year: "))
            term = int(input("Enter term (1, 2, or 3): "))
            add_class(class_name, year, term)
            print("\nClass added successfully.")

        elif choice == "2":
            class_id = int(input("Enter class ID: "))
            assignment_name = input("Enter assignment name: ")
            grade = float(input("Enter grade: "))
            weight = float(input("Enter weight: "))
            add_grade(class_id, assignment_name, grade, weight)
            print("\nGrade added successfully.")

        elif choice == "3":
            class_id = int(input("Enter class ID: "))
            title = input("Enter assignment title: ")
            due_date = input("Enter due date (YYYY-MM-DD): ")
            add_assignment(class_id, title, due_date)
            print("\nAssignment added successfully.")

        elif choice == "4":
            class_id = int(input("Enter class ID: "))
            average = calculate_weighted_average(class_id)
            print(f"\nCurrent average for class {class_id}: {average:.2f}%")

        elif choice == "5":
            upcoming = get_upcoming_assignments()
            print("Upcoming assignments:")
            for title, due_date in upcoming:
                print(f"\n{title} (Due: {due_date})")

        elif choice == "6":
            display_gpa_by_year_and_term()

        elif choice == "7":
            print("\nExiting the tracker. Goodbye!")
            break

        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()