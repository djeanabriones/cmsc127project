import os
import platform
import sys
import mysql.connector
from datetime import datetime
from tabulate import tabulate
from admin_dashboard import admin_menu
from utility import clear_console, validate_input, get_next_id, db, cursor
from admin_report import admin_reports
from president import president_menu
from member import member_menu

# Database connection
def connect_db():
	return mysql.connector.connect(
		host="localhost",
		user="root",
		password="ilove127",
		database="org_management",
		auth_plugin="mysql_native_password"
	)

db = connect_db()
cursor = db.cursor()


# Authentication
def signup():
	clear_console()
	print("SIGN UP")
	first_name = validate_input("First name: ")
	last_name = validate_input("Last name: ")
	batch = validate_input("Batch: ", int)
	gender = validate_input("Gender: ")
	degree_program = validate_input("Degree Program: ")
	
	member_id = get_next_id("member", "memberid")
	
	try:
		cursor.execute("""
			INSERT INTO member (memberid, firstname, lastname, batch, gender, degreeprogram)
			VALUES (%s, %s, %s, %s, %s, %s)
		""", (member_id, first_name, last_name, batch, gender, degree_program))
		
		join_now = input("Would you like to join an organization now? (y/n): ").lower()
		if join_now == 'y':
			organization_id = validate_input("Organization ID to join: ", int)
			cursor.execute("SELECT 1 FROM organization WHERE organizationid = %s", (organization_id,))
			if not cursor.fetchone():
				print("Error: Organization does not exist")
				db.rollback()
				input("Press Enter to return to main menu")
				return
			
			role = "Member"
			status = "active"
			committee = validate_input("Committee: ")
			semester = validate_input("Semester (1/2): ", int)
			year = validate_input("Academic Year (e.g., 2024-2025): ")
			
			cursor.execute("""
				INSERT INTO serves (memberid, organizationid, role, status, committee, semester, academicyear)
				VALUES (%s, %s, %s, %s, %s, %s, %s)
			""", (member_id, organization_id, role, status, committee, semester, year))
		
		db.commit()
		print(f"\nAccount created! Your member ID is {member_id}.")
	except mysql.connector.Error as err:
		print(f"Error: {err}")
		db.rollback()
	
	input("Press Enter to return to main menu")

def get_user_role(member_id):
	cursor.execute("""
		SELECT role FROM serves
		WHERE memberid = %s
		ORDER BY academicyear DESC, semester DESC
		LIMIT 1
	""", (member_id,))
	result = cursor.fetchone()
	return result[0].lower() if result else "member"

def get_user_org(member_id):
	cursor.execute("""
		SELECT organizationid FROM serves
		WHERE memberid = %s
		ORDER BY academicyear DESC, semester DESC
		LIMIT 1
	""", (member_id,))
	result = cursor.fetchone()
	return result[0] if result else None

def signin():
	clear_console()
	print("SIGN IN")
	member_id = validate_input("Enter your member ID: ")
	
	if member_id.lower() == "admin":
		admin_menu()
		return None
	
	cursor.execute("SELECT * FROM member WHERE memberid = %s", (member_id,))
	user = cursor.fetchone()
	
	if not user:
		print("Error: Member not found")
		input("Press Enter to return")
		return None
	
	role = get_user_role(member_id)
	print(f"\nWelcome back, {user[1]} {user[2]} (Role: {role})")
	input("Press Enter to continue")
	
	if "president" in role.lower():
		president_menu(member_id)
	else:
		member_menu(member_id)
	
	return None


# Landing Page
def landing_page():
	while True:
		clear_console()
		print("STUDENT ORGANIZATION MANAGEMENT SYSTEM")
		print("[1] Sign In")
		print("[2] Sign Up")
		print("[0] Exit")
		
		choice = input("Enter choice: ")
		
		if choice == '1':
			signin()
		elif choice == '2':
			signup()
		elif choice == '0':
			print("Goodbye! Thank you for using this Student Organization Management System!")
			db.close()
			sys.exit()
		else:
			print("Invalid choice")
			input("Press Enter to continue")

if __name__ == "__main__":
	landing_page()