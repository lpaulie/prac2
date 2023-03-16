#import modules
from multiprocessing import Event
import tkinter as tk
from turtle import width
from webbrowser import get
import sqlite3








# Create and configure GUI window.
w = tk.Tk()
w.configure(height = 350, width = 600, background = "white")
w.title("Student Login")
global font_size
font_size = 14
label_settings = {'font' : ("MS Serif", font_size, "bold"), 'foreground' : "#0c0c46", 'background' : "white"}
label_settings_2 = {'font' : ("Times New Roman", 10), "foreground" : "black", 'background' : "white"}
entry_settings = {"relief" : "raised", "bd" : 2}



# The following function is called when the "submit" button is pressed on the w window.
def submit():

  # Uses the .get() function to retrieve the inputs from each field prompted in w.
  year = year_entry.get()
  day = selected_day.get()
  month = selected_month.get()
  grade_level = grades.get()
  sport_attending = events.get()
  student_name = name.get()
  login_num = 1

  # The try/except statement is intended to expect errors and use them as a condition. The specific error this is meant to account for is a duplicate entry in the table.
  # The reason a duplicate input would prompt an error is due to the UNIQUE addition in the creation of the table. This requires deviation in each input into the table to
  # prevent cheating from the students.
  try:
    # Create a connection to the SQLite database
    conn = sqlite3.connect("C:\\fbla competition - luke paulus\\databases\\students.db")
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Create a table to record each input and to also assure a unique entry each time.
    # The following has been commented out because the table has already been created and is perpetually stored, but the code is below

    #cursor.execute("CREATE TABLE students (name TEXT, grade INTEGER, sport TEXT, day INTEGER, month INTEGER, year INTEGER, logincount INTEGER, UNIQUE (name, grade, sport, day, month, year))")

    # Insert variables initiated by get() function at the beginning of submit()
    cursor.execute("INSERT INTO students (name, grade, sport, day, month, year, logincount) VALUES (?, ?, ?, ?, ?, ?, ?)", (student_name, grade_level, sport_attending, day, month, year, login_num))
    

    # Save the changes
    conn.commit()

    # Query the data
    cursor.execute("SELECT * FROM students")

    # Fetch the results
    results = cursor.fetchall()


    # Close the cursor
    cursor.close()

    # Close the connection
    conn.close()

  # Except handles all identical entries by terminating the submission and creating a Tkinter window to notify of the error.
  except sqlite3.IntegrityError:
    error_window = tk.Tk()
    error_window.title("Duplicate Entry")
    error_window.configure(height = 100, width = 200, background = "white")
    error_label = tk.Label(error_window, text = "Duplicate entries are not permitted.", **label_settings_2).place(x = 5, y = 30)

  # Exception handles all other errors for troubleshooting purposes.
  except Exception as e:
    print(f"Error: {e}")


  # Submit_notice is a window that notifies the user of a successful submission or execution of submit()
  submit_notice = tk.Tk()
  submit_notice.title("Submission Status")
  submit_notice.configure(height = 100, width = 300, background = "white")
  tk.Label(submit_notice, text = "Successful Submission.", **label_settings_2).place(x = 80, y = 30)


# deletes all data from the database but keeps its rows/collumns so a new set of information can be input (quarter reset)
def delete_tab_content():
  # Connect to the database
  conn = sqlite3.connect('C:\\fbla competition - luke paulus\\databases\\students.db')

  # Create a cursor object
  cursor = conn.cursor()

  # Execute the delete statement
  cursor.execute('DELETE FROM students')

  # Commit the changes to the database
  conn.commit()

  # Close the database connection
  conn.close()

  # Creates window to notify of the table reset
  deleted_table_window = tk.Tk()
  deleted_table_window.title("Reset Database")
  deleted_table_window.configure(height = 100, width = 200, background = "white")
  tk.Label(deleted_table_window, text = "Database has been reset.", **label_settings_2).place(x = 35, y = 30)

# Produces a "leaderboard": the leader in logincount (total number of attendences) per student for each of the 4 grades
def leaderboard():
  # Connect to the database
  conn = sqlite3.connect('C:\\fbla competition - luke paulus\\databases\\students.db')
  # Create cursor object
  c = conn.cursor()

  # This query first groups the students by their grade and name and calculates the total number of logins for each group. 
  # It then assigns a row number (rn) to each student within their grade, based on their login count in descending order.
  # the outer query selects only the rows with a row number of 1, which correspond to the student(s) with the highest login count in each grade. 
  # The results are ordered by grade. 
  c.execute('''
      SELECT grade, name, total_logins
      FROM (
          SELECT grade, name, SUM(logincount) AS total_logins,
                ROW_NUMBER() OVER (PARTITION BY grade ORDER BY SUM(logincount) DESC) AS rn
          FROM students
          WHERE grade BETWEEN 9 AND 12
          GROUP BY grade, name
      ) subq
      WHERE rn = 1
      ORDER BY grade
  ''')

  results = c.fetchall()

  # Creates Tkinter window to display the output of the query

  winners_frame = tk.Tk()
  winners_frame.title("Grade Winners")
  winners_frame.configure(height = 150, width = 200, background = "white")

  # The for statement iterates through each row (which corresponds to a grade) and displays its output on the label which is on winners_frame
  for row_num, row in enumerate(results):
    grade, name, total_logins = row
    label_text = f"{name} has the highest login count in grade {grade} with {total_logins} logins."
    grade_label = tk.Label(winners_frame, text=f"Grade {grade}:", **label_settings_2)
    winners_label = tk.Label(winners_frame, text=label_text, **label_settings_2)
    grade_label.grid(row=row_num, column=0, sticky="w", padx=10, pady=5)
    winners_label.grid(row=row_num, column=1, sticky="w", padx=10, pady=5)
  conn.close()

  

# random_winner uses a query to select a random name from students (random winner)
def random_winner():
  # Connect to the database
  conn = sqlite3.connect('C:\\fbla competition - luke paulus\\databases\\students.db')

  # Create a cursor object
  cursor = conn.cursor()

  # Execute the SELECT statement with ORDER BY RANDOM() and LIMIT 1 to choose a random name
  cursor.execute('SELECT name FROM students ORDER BY RANDOM() LIMIT 1')

  # Fetch the result and store it in a variable
  result = cursor.fetchone()

  # Close the database connection
  conn.close()

  # Access the result (tuple with one element)
  global random_name
  random_name = result[0]

  # Creates Tkinter window to display output of query using f string
  random_name_window = tk.Tk()
  random_name_window.title("Random Winner")
  random_name_window.configure(height = 100, width = 300, background = "white")
  tk.Label(random_name_window, text = f"The random winner is {random_name}", **label_settings_2).place(x = 50, y = 30)
  
# Query for grades in student_grades (sample set of students)
def grade_checker():
  #each of the following is a fake name/gpa to be a placeholder for a list of actual student transcript data
  example_students = [('Katerina Woods', '2.67'),('Yasu Yang', '4.12'),('Joseph Brooks', '3.14'),('Lucy Zimmerman', '4.23'),('Verona Milon', '3.10')]

  # Create a connection to the database
  conn = sqlite3.connect('C:\\fbla competition - luke paulus\\databases\\student_grades.db')

  # Create a cursor object to execute SQL commands
  cursor = conn.cursor()

  # Define the SQL command to create a new table called "grades"
  #cursor.execute("CREATE TABLE student_grades (student TEXT, grades TEXT)")
  #insert_record_sql = '''INSERT INTO student_grades (student, grades) VALUES (?, ?)'''

# Iterate over the list of tuples and insert each one

  #for record in example_students:
  #  cursor.execute(insert_record_sql, record)

  cursor.execute("SELECT * FROM student_grades")
  all_student_grades = cursor.fetchall()
  

  # Commit the changes to the database
  conn.commit()

  
  #close database connection
  conn.close()
  
  # Creates and configures Tk window to hold the entry fields for the grade_checker() function.
  grade_checker_frame = tk.Tk()
  grade_checker_frame.title("Grade Checker")
  grade_checker_frame.configure(height = 100, width = 400, background = "white")
  grade_check_name_label = tk.Label(grade_checker_frame, text = "Enter Student First + Last Name:", **label_settings_2).place(x = 20, y = 20)
  global grade_check_entry
  grade_check_entry = tk.Entry(grade_checker_frame, **entry_settings, width=25)
  grade_check_entry.place(x = 210, y = 20)

  # This is executed when the "submit" button is pressed.
  def grade_check_submit():
    conn = sqlite3.connect('C:\\fbla competition - luke paulus\\databases\\student_grades.db')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    #uses get() to initialize entry input as a variable 
    student_name = grade_check_entry.get()

    # Selects the grade for a student
    select_grades_sql = '''SELECT grades FROM student_grades WHERE student = ?'''

    # Inserts the name inputted into the entry fiels
    cursor.execute(select_grades_sql, (student_name,))
    grades = cursor.fetchone()

    # Grade_window shows output of the SQL query - grades for the student 

    global grade_window
    grade_window = tk.Tk()
    grade_window.title("Grade Checker")
    grade_window.configure(height = 100, width = 400, background = "white")

    # Output if grades are found for student_name
    if grades:
      
      grade_result = tk.Label(grade_window, text = f"Grades for {student_name}: {grades[0]}", **label_settings_2).place(x = 50, y = 30)
    # Output if grades are not found for student_name
    else:

      grade_result = tk.Label(grade_window, text = f"Grades for {student_name} not found.", **label_settings_2).place(x = 50, y = 30)
    
    # Commit the changes to the database
    conn.commit()

    
    #close database connection
    conn.close()
    
  



    

  # Submit button on grade_checker_frame: calls grade_check_submit
  global grade_submit_button
  grade_submit_button = tk.Button(grade_checker_frame, label_settings_2, text="Search", bg = "#0c0c46", fg = "white", command=grade_check_submit).place(x = 170, y = 50)

# login_search retrieves the logincount from students for a prompted name
def login_search():

  # Search window with another entry/get() method
  login_search_window = tk.Tk()
  login_search_window.title("Search Student Logins")
  login_search_window.configure(height = 100, width = 400, background = "white")
  tk.Label(login_search_window, text = "Enter Student First + Last Name:", **label_settings_2).place(x = 20, y = 20)
  
  login_search_entry = tk.Entry(login_search_window, **entry_settings, width=25)
  login_search_entry.place(x = 210, y = 20)
  
  def login_search_submit():
    global student_login_name
    student_login_name = login_search_entry.get()
    
      # Create a connection to the database
    conn = sqlite3.connect('C:\\fbla competition - luke paulus\\databases\\students.db')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Selects logincount for each name in students

    select_student_sql = '''SELECT logincount FROM students WHERE name = ?'''
    cursor.execute(select_student_sql, (student_login_name,))
    login_count = cursor.fetchone()

    # Tkinter window to display output of query
    global login_count_window
    login_count_window = tk.Tk()
    login_count_window.title("Login Count")
    login_count_window.configure(height = 100, width = 300, background = "white")

    # Uses if/else to make a label depending on if login count is foound
    if login_count is not None:
      
      tk.Label(login_count_window, text = f"Logins for {student_login_name}: {login_count[0]}", **label_settings_2).place(x = 50, y = 30)
    else:

      tk.Label(login_count_window, text = f"Login count for {student_login_name} not found.", **label_settings_2).place(x = 50, y = 30)
  # Calls login_search_submit
  login_submit_button = tk.Button(login_search_window, label_settings_2, text="Search", bg = "#0c0c46", fg = "white", command=login_search_submit).place(x = 170, y = 50)

# Creates window that outlines reward information
def view_prize_info():
  prize_window = tk.Tk()
  prize_window.title("Prize Information")
  prize_window.configure(height = 150, width = 300, background = "white")

  tk.Label(prize_window, text = "School Reward - 1 to 3 logins", **label_settings_2).place(x = 50, y = 30)
  tk.Label(prize_window, text = "Food Reward - 4 to 5 logins", **label_settings_2).place(x = 50, y = 60)
  tk.Label(prize_window, text = "Spirit Wear item - 5< logins", **label_settings_2).place(x = 50, y = 90)

def admin_log():
  # Create a new Tkinter window named "admin".
  global admin
  admin = tk.Tk()

  # Set the window title and size.
  admin.title('Admin Login')
  admin.geometry('400x150')

  # Add labels.
  tk.Label(admin, text = "First and Last Name:", **label_settings_2).place(x = 50, y = 20)
  global admin_name_entry
  admin_name_entry = tk.Entry(admin, **entry_settings, width=25)
  admin_name_entry.place(x = 190, y = 20)

  tk.Label(admin, text = "Password:", **label_settings_2).place(x = 65, y = 60)
  global password_entry
  password_entry = tk.Entry(admin, **entry_settings, width=25)
  password_entry.place(x = 190, y = 60)

  # Creates admin panel with all control and access to the databases.

  def admin_submit():
    admin_name = admin_name_entry.get()
    admin_password = password_entry.get()
    # Requires placeholder username and password. In application the boolean expression could be from a list of admin names and corresponding passwords. 
    if (admin_name == "admin" and admin_password == "password"):

      # Creating admin panel
      admin_window = tk.Tk()
      admin_window.title('Admin Panel')
      admin_window.configure(height = 400, width = 600, background = "white")
      tk.Label(admin_window, text = "FHC Admin Panel", **label_settings).place(x = 200, y = 0)
      tk.Label(admin_window, text = "Go Spartans!", **label_settings).place(x = 230, y = 20)

      # Buttons to call each of the above administrative functions placed on admin_window
      end_quarter_report = tk.Button(admin_window, label_settings_2, text="View Leaderboard", bg = "#0c0c46", fg = "white", command=leaderboard).place(x = 225, y = 80)
      delete_table = tk.Button(admin_window, label_settings_2, text="Reset Leaderboard", bg = "#0c0c46", fg = "white", command=delete_tab_content).place(x = 225, y = 280)
      random_winner_button = tk.Button(admin_window, label_settings_2, text="Select Random Winner", bg = "#0c0c46", fg = "white", command=random_winner).place(x = 215, y = 130)
      grade_checker_button = tk.Button(admin_window, label_settings_2, text="Check Student Grades", bg = "#0c0c46", fg = "white", command=grade_checker).place(x = 215, y = 180)
      login_search_button = tk.Button(admin_window, label_settings_2, text="Search Student Logins", bg = "#0c0c46", fg = "white", command= login_search).place(x = 215, y = 230)
      login_search_button = tk.Button(admin_window, label_settings_2, text="View Prize Info", bg = "#0c0c46", fg = "white", command= view_prize_info).place(x = 235, y = 330)
    # Handles an incorrect name or password by notifying with a label on pw_error
    else:
      pw_error = tk.Tk()
      pw_error.title("Wrong Name/PW")
      pw_error.configure(height = 100, width = 200, background = "white")
      wrong_password = tk.Label(pw_error, text = "Wrong Username or Password.", **label_settings_2).place(x = 15, y = 30)

  # Submit button which calls admin_submit to create the new panel     
  global admin_submit_button
  admin_submit_button = tk.Button(admin, label_settings_2, text="Login", bg = "#0c0c46", fg = "white", command=admin_submit).place(x = 190, y = 110)
 


  
# Title labels

tk.Label(w, text = "FHC Student Login", **label_settings).place(x = 200, y = 0)
font_size = font_size - 4 
tk.Label(w, text = "Go Spartans!", **label_settings).place(x = 230, y = 20)

#Images in the upper left hand corners

image1 = tk.PhotoImage(file = "C:\\fbla competition - luke paulus\\pictures\\fhclogo.png")
tk.Label(image=image1).place(x = 0, y = 0)

image2 = tk.PhotoImage(file = "C:\\fbla competition - luke paulus\\pictures\\spartan.png")
tk.Label(image=image2).place(x = 450, y = 0)

# Name entry field
tk.Label(w, text = "First and Last Name:", **label_settings_2).place(x = 150, y = 80)
name = tk.Entry(w, **entry_settings, width=25)
name.place(x = 275, y = 80)

# Creates dropdown menu from event_list
tk.Label(w, text = "Event Attending:", **label_settings_2).place(x = 165, y = 130)

# Create a StringVar object to hold the events
event_list = ["Basketball", "Wrestling", "Football", "Volleyball", "Soccer", "Band", "Choir", "Theatre Production", "Speech/Debate", "Robotics"]
events = tk.StringVar()

# Inserts the StringVar into the OptionMenu
sport = tk.OptionMenu(w, events, *event_list).place(x=300, y = 125)

admin_button = tk.Button(w, label_settings_2, text="Admin Login", bg = "#0c0c46", fg = "white", command=admin_log).place(x = 5, y = 300)

# Creating another dropdown menu for each grade 9-12
grades = tk.StringVar()

tk.Label(w, text = "Grade:", **label_settings_2).place(x = 220, y = 175)
grade = tk.OptionMenu(w, grades, "9","10","11","12").place(x=300, y = 175)

# Create a StringVar object to hold the selected date
selected_month = tk.StringVar()
selected_day = tk.StringVar()


# Create a label and dropdown menu for the month
month_label = tk.Label(w, text="Month:")
month_label.place(x=100, y=225)
month_menu = tk.OptionMenu(w, selected_month, "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
month_menu.place(x=150, y=225)

# Create a label and dropdown menu for the day
day_label = tk.Label(w, text="Day:")
day_label.place(x=255, y=225)
day_menu = tk.OptionMenu(w, selected_day, "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31")
day_menu.place(x=305, y=225 )

# Create a label and entry field for the year
year_label = tk.Label(w, text="Year:")
year_label.place(x=410,y=225)
year_entry = tk.Entry(w, entry_settings)
year_entry.place(x=460,y=225)


# Submission for all fields on w
submit_button = tk.Button(w, label_settings_2, bg = "#0c0c46", fg = "white", text="Submit!", command=submit).place(x = 280, y = 300)


tk.mainloop()