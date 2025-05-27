# import tkinter as tk
# from tkinter import messagebox
# import mysql.connector

# # --- Database Connection ---
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="tiger",
#     database="org_management"
# )
# cursor = db.cursor()

# # --- Utility Functions ---
# def get_next_id(table, id_column):
#     cursor.execute(f"SELECT MAX({id_column}) FROM {table}")
#     result = cursor.fetchone()[0]
#     return (result or 0) + 1

# # --- GUI Setup ---
# root = tk.Tk()
# root.title("Student Org Management System")
# root.geometry("400x500")

# # --- Sign In Frame ---
# def show_signin():
#     clear_frame()

#     tk.Label(root, text="Sign In", font=('Arial', 16)).pack(pady=10)

#     tk.Label(root, text="Member ID:").pack()
#     member_id_entry = tk.Entry(root)
#     member_id_entry.pack()

#     def signin():
#         member_id = member_id_entry.get()
#         cursor.execute("SELECT * FROM member WHERE memberid = %s", (member_id,))
#         user = cursor.fetchone()
#         if user:
#             messagebox.showinfo("Welcome", f"Welcome {user[1]} {user[2]}")
#             show_home(user)
#         else:
#             messagebox.showerror("Error", "Member not found")

#     tk.Button(root, text="Sign In", command=signin).pack(pady=10)
#     tk.Button(root, text="Back", command=show_main_menu).pack()

# # --- Sign Up Frame ---
# def show_signup():
#     clear_frame()

#     tk.Label(root, text="Sign Up", font=('Arial', 16)).pack(pady=10)

#     entries = {}
#     for label in ["First Name", "Last Name", "Batch", "Gender", "Degree Program"]:
#         tk.Label(root, text=label).pack()
#         entry = tk.Entry(root)
#         entry.pack()
#         entries[label.lower()] = entry

#     def signup():
#         member_id = get_next_id("member", "memberid")
#         try:
#             cursor.execute("""
#                 INSERT INTO member (memberid, firstname, lastname, batch, gender, degreeprogram)
#                 VALUES (%s, %s, %s, %s, %s, %s)
#             """, (
#                 member_id,
#                 entries["first name"].get(),
#                 entries["last name"].get(),
#                 int(entries["batch"].get()),
#                 entries["gender"].get(),
#                 entries["degree program"].get()
#             ))
#             db.commit()
#             messagebox.showinfo("Success", f"Account created! Your ID: {member_id}")
#             show_main_menu()
#         except Exception as e:
#             messagebox.showerror("Error", str(e))

#     tk.Button(root, text="Sign Up", command=signup).pack(pady=10)
#     tk.Button(root, text="Back", command=show_main_menu).pack()

# # --- Home Menu After Login ---
# def show_home(user):
#     clear_frame()

#     tk.Label(root, text=f"Welcome, {user[1]}", font=('Arial', 14)).pack(pady=10)

#     def view_dues():
#         clear_frame()
#         tk.Label(root, text="== Unpaid Dues ==", font=('Arial', 14)).pack(pady=10)
#         cursor.execute("""
#             SELECT o.organizationname, f.semester, f.academicyear, f.balancedue
#             FROM organization o
#             JOIN fee f ON o.organizationid = f.organizationid
#             WHERE f.memberid = %s AND f.paymentstatus = 'unpaid'
#         """, (user[0],))
#         rows = cursor.fetchall()
#         if rows:
#             for row in rows:
#                 tk.Label(root, text=f"Org: {row[0]} | Sem: {row[1]} | AY: {row[2]} | Balance: {row[3]}").pack()
#         else:
#             tk.Label(root, text="No unpaid dues found.").pack()

#         tk.Button(root, text="Back", command=lambda: show_home(user)).pack(pady=10)

#     tk.Button(root, text="View My Unpaid Dues", command=view_dues).pack(pady=5)
#     tk.Button(root, text="Sign Out", command=show_main_menu).pack(pady=20)

# # --- Main Menu ---
# def show_main_menu():
#     clear_frame()

#     tk.Label(root, text="Student Org Management", font=('Arial', 18)).pack(pady=20)

#     tk.Button(root, text="Sign In", command=show_signin).pack(pady=10)
#     tk.Button(root, text="Sign Up", command=show_signup).pack(pady=10)
#     tk.Button(root, text="Quit", command=root.quit).pack(pady=10)

# # --- Frame Clearer ---
# def clear_frame():
#     for widget in root.winfo_children():
#         widget.destroy()

# # --- Start ---
# show_main_menu()
# root.mainloop()

import mysql.connector
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="tiger",
    database="org_management"
)
cursor = db.cursor()

# Utility
def get_next_id(table, id_column):
    cursor.execute(f"SELECT MAX({id_column}) FROM {table}")
    result = cursor.fetchone()[0]
    return (result or 0) + 1

# Signup Logic
def signup():
    def register_user():
        first = first_entry.get()
        last = last_entry.get()
        batch = batch_entry.get()
        gender = gender_entry.get()
        degree = degree_entry.get()

        if not all([first, last, batch, gender, degree]):
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            batch_int = int(batch)
        except ValueError:
            messagebox.showerror("Error", "Batch must be a number.")
            return

        member_id = get_next_id("member", "memberid")
        cursor.execute("""
            INSERT INTO member (memberid, firstname, lastname, batch, gender, degreeprogram)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (member_id, first, last, batch_int, gender, degree))
        db.commit()
        messagebox.showinfo("Success", f"Account created! Your Member ID is {member_id}")
        signup_window.destroy()

    signup_window = tb.Toplevel(root)
    signup_window.title("Sign Up")
    signup_window.geometry("350x350")
    tb.Label(signup_window, text="First Name:").pack(pady=5)
    first_entry = tb.Entry(signup_window)
    first_entry.pack()

    tb.Label(signup_window, text="Last Name:").pack(pady=5)
    last_entry = tb.Entry(signup_window)
    last_entry.pack()

    tb.Label(signup_window, text="Batch:").pack(pady=5)
    batch_entry = tb.Entry(signup_window)
    batch_entry.pack()

    tb.Label(signup_window, text="Gender:").pack(pady=5)
    gender_entry = tb.Entry(signup_window)
    gender_entry.pack()

    tb.Label(signup_window, text="Degree Program:").pack(pady=5)
    degree_entry = tb.Entry(signup_window)
    degree_entry.pack()

    tb.Button(signup_window, text="Register", bootstyle="success", command=register_user).pack(pady=10)

# Sign In Logic
def signin():
    def login_user():
        member_id = id_entry.get()
        cursor.execute("SELECT * FROM member WHERE memberid = %s", (member_id,))
        user = cursor.fetchone()
        if user:
            messagebox.showinfo("Welcome", f"Hello, {user[1]} {user[2]}!")
            signin_window.destroy()
        else:
            messagebox.showerror("Error", "Member not found.")

    signin_window = tb.Toplevel(root)
    signin_window.title("Sign In")
    signin_window.geometry("300x200")
    tb.Label(signin_window, text="Enter your Member ID:").pack(pady=10)
    id_entry = tb.Entry(signin_window)
    id_entry.pack()
    tb.Button(signin_window, text="Sign In", bootstyle="primary", command=login_user).pack(pady=20)

# Main Window
root = tb.Window(themename="flatly")  # Try 'darkly', 'superhero', etc.
root.title("Student Org Management")
root.geometry("400x300")

tb.Label(root, text="Student Org Management", font=("Segoe UI", 20, "bold")).pack(pady=30)

tb.Button(root, text="Sign In", bootstyle="primary", width=20, command=signin).pack(pady=10)
tb.Button(root, text="Sign Up", bootstyle="success", width=20, command=signup).pack(pady=10)
tb.Button(root, text="Quit", bootstyle="danger", width=20, command=root.quit).pack(pady=10)

root.mainloop()

