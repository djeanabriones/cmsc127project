
# # utility functions
# def clear_console():
#     os.system('cls' if platform.system() == 'Windows' else 'clear')

# def get_next_id(table, id_column):
#     cursor.execute(f"SELECT MAX({id_column}) FROM {table}")
#     result = cursor.fetchone()[0]
#     return (result or 0) + 1

# # # authentication
# # def signup():
# #     clear_console()
# #     print("=== SIGN UP ===")
# #     first = input("First name: ")
# #     last = input("Last name: ")
# #     batch = int(input("Batch: "))
# #     gender = input("Gender: ")
# #     degree = input("Degree Program: ")

# #     member_id = get_next_id("member", "memberid")
# #     cursor.execute("""
# #         INSERT INTO member (memberid, firstname, lastname, batch, gender, degreeprogram)
# #         VALUES (%s, %s, %s, %s, %s, %s)
# #     """, (member_id, first, last, batch, gender, degree))
# #     db.commit()

# #     print(f"\nAccount created! Your member ID is {member_id}.")
# #     input("Press Enter to return to main menu...")

# def signup(first, last, batch, gender, degree):
#     try:
#         member_id = get_next_id("member", "memberid")

#         cursor.execute("""
#             INSERT INTO member (memberid, firstname, lastname, batch, gender, degreeprogram)
#             VALUES (%s, %s, %s, %s, %s, %s)
#         """, (member_id, first, last, batch, gender, degree))
#         db.commit()

#         return {
#             "success": True,
#             "member_id": member_id,
#             "message": f"Account created! Your member ID is {member_id}."
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "message": f"Error creating account: {str(e)}"
#         }


# # def signin():
# #     clear_console()
# #     print("=== SIGN IN ===")
# #     member_id = input("Enter your member ID: ")
# #     cursor.execute("SELECT * FROM member WHERE memberid = %s", (member_id,))
# #     user = cursor.fetchone()
# #     if user:
# #         print(f"\nWelcome back, {user[1]} {user[2]}!")
# #         input("Press Enter to continue...")
# #         return user
# #     else:
# #         print("Member not found.")
# #         input("Press Enter to return...")
# #         return None

# def signin(member_id):
#     try:
#         cursor.execute("SELECT * FROM member WHERE memberid = %s", (member_id,))
#         user = cursor.fetchone()

#         if user:
#             return {
#                 "success": True,
#                 "user": {
#                     "memberid": user[0],
#                     "firstname": user[1],
#                     "lastname": user[2],
#                     "batch": user[3],
#                     "gender": user[4],
#                     "degreeprogram": user[5]
#                 }
#             }
#         else:
#             return {
#                 "success": False,
#                 "message": "Member not found."
#             }
#     except Exception as e:
#         return {
#             "success": False,
#             "message": f"Sign in failed: {str(e)}"
#         }


# # Main Menu
# def landing_page():
#     while True:
#         clear_console()
#         print("== STUDENT ORGANIZATION MANAGEMENT SYSTEM ==")
#         print("[1] Sign In")
#         print("[2] Sign Up")
#         print("[3] Quit")
#         choice = input("Enter choice: ")
#         if choice == '1':
#             user = signin()
#             if user:
#                 home_menu(user)
#         elif choice == '2':
#             signup()
#         elif choice == '3':
#             print("Goodbye!")
#             sys.exit()
#         else:
#             print("Invalid choice. Try again.")
#             input("Press Enter to continue...")

# # Member Functions
# def home_menu(user):
#     while True:
#         clear_console()
#         print(f"== Welcome, {user[1]} ==")
#         print("[1] View My Unpaid Dues")
#         print("[2] View Members with Unpaid Dues (Org)")
#         print("[3] Update My Info")
#         print("[4] Delete My Account")
#         print("[5] Add Membership Fee")
#         print("[6] Join an Organization")
#         print("[7] Sign Out")
#         choice = input("Enter choice: ")
#         if choice == '1':
#             view_member_unpaid_dues(user[0])
#         elif choice == '2':
#             org_id = input("Enter organization ID: ")
#             semester = input("Semester: ")
#             year = input("Academic Year: ")
#             view_unpaid_members(org_id, semester, year)
#         elif choice == '3':
#             update_member_info(user[0])
#         elif choice == '4':
#             delete_member(user[0])
#             return
#         elif choice == '5':
#             add_fee(user[0])
#         elif choice == '6':
#             join_organization(user[0])
#         elif choice == '7':
#             return
#         else:
#             print("Invalid input.")
#             input("Press Enter to continue...")

# # Member Management
# def update_member_info(member_id):
#     clear_console()
#     print("== Update Member Info ==")
#     new_batch = int(input("New batch: "))
#     new_degree = input("New degree program: ")

#     cursor.execute("""
#         UPDATE member
#         SET batch = %s, degreeprogram = %s
#         WHERE memberid = %s
#     """, (new_batch, new_degree, member_id))
#     db.commit()
#     print("Member information updated.")
#     input("Press Enter to continue...")

# def delete_member(member_id):
#     clear_console()
#     confirm = input("Are you sure you want to delete your account? (y/n): ").lower()
#     if confirm == 'y':
#         cursor.execute("DELETE FROM member WHERE memberid = %s", (member_id,))
#         db.commit()
#         print("Account deleted.")
#     else:
#         print(" Deletion canceled.")
#     input("Press Enter to continue...")

# # Fee Management
# def add_fee(member_id):
#     clear_console()
#     print("== Add Membership Fee ==")
#     org_id = int(input("Organization ID: "))
#     semester = int(input("Semester (1/2): "))
#     year = int(input("Academic Year: "))
#     total_due = int(input("Total Due: "))
#     total_paid = int(input("Total Paid: "))
#     balance = total_due - total_paid
#     status = "paid" if balance == 0 else "unpaid"
#     due_date = input("Payment Due Date (YYYY-MM-DD): ")
#     date_paid = input("Date Paid (YYYY-MM-DD or leave blank if unpaid): ")

#     fee_id = get_next_id("fee", "feeid")
#     date_paid_value = date_paid if date_paid.strip() else None

#     cursor.execute("""
#         INSERT INTO fee (feeid, semester, academicyear, totaldue, totalpaid, balancedue,
#                          paymentstatus, paymentduedate, datepaid, memberid, organizationid)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """, (
#         fee_id, semester, year, total_due, total_paid, balance,
#         status, due_date, date_paid_value, member_id, org_id
#     ))
#     db.commit()
#     print("Fee recorded.")
#     input("Press Enter to continue...")

# # Org Membership
# def join_organization(member_id):
#     clear_console()
#     print("== Join an Organization ==")
#     org_id = int(input("Organization ID: "))
#     role = input("Role (e.g. Member, President): ")
#     status = input("Status (e.g. active, inactive): ")
#     committee = input("Committee: ")
#     semester = int(input("Semester (1/2): "))
#     year = int(input("Academic Year: "))

#     cursor.execute("""
#         INSERT INTO serves (memberid, organizationid, role, status, committee, semester, academicyear)
#         VALUES (%s, %s, %s, %s, %s, %s, %s)
#     """, (member_id, org_id, role, status, committee, semester, year))
#     db.commit()
#     print("✅ Joined organization.")
#     input("Press Enter to continue...")

# # Reports
# def view_member_unpaid_dues(memberid):
#     clear_console()
#     print("== Unpaid Dues ==")
#     cursor.execute("""
#         SELECT o.organizationname, f.semester, f.academicyear, f.balancedue
#         FROM organization o
#         JOIN fee f ON o.organizationid = f.organizationid
#         WHERE f.memberid = %s AND f.paymentstatus = 'unpaid'
#     """, (memberid,))
#     rows = cursor.fetchall()
#     if rows:
#         for row in rows:
#             print(f"Org: {row[0]} | Sem: {row[1]} | AY: {row[2]} | Balance: {row[3]}")
#     else:
#         print("No unpaid dues found.")
#     input("Press Enter to continue...")

# def view_unpaid_members(org_id, semester, year):
#     clear_console()
#     print("== Unpaid Members ==")
#     cursor.execute("""
#         SELECT m.firstname, m.lastname
#         FROM member m
#         JOIN fee f ON m.memberid = f.memberid
#         WHERE f.organizationid = %s AND f.semester = %s AND f.academicyear = %s
#               AND f.paymentstatus = 'unpaid'
#     """, (org_id, semester, year))
#     rows = cursor.fetchall()
#     if rows:
#         for row in rows:
#             print(f"{row[0]} {row[1]}")
#     else:
#         print("No unpaid members found.")
#     input("Press Enter to continue...")

# # Entry Point
# if __name__ == "__main__":
#     create_tables()
#     landing_page()
