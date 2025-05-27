
# President Dashboard
from datetime import datetime
import mysql
from utility import get_next_id, get_user_org, show_table
from utility import clear_console, validate_input
from db_connection import db, cursor
import mysql.connector

def president_menu(member_id):
	org_id = get_user_org(member_id)
	if not org_id:
		print("Error: You are not associated with any organization")
		input("Press Enter to return")
		return
	
	while True:
		clear_console()
		print("PRESIDENT DASHBOARD")
		print("[1] Membership Management")
		print("[2] Fees Management")
		print("[0] Sign Out")
		
		choice = validate_input("Enter choice: ")
		
		if choice == '1':
			membership_management(org_id)
		elif choice == '2':
			fees_management(org_id)
		elif choice == '0':
			return
		else:
			print("Error: Invalid choice")
			input("Press Enter to continue")

def membership_management(org_id):
	while True:
		clear_console()
		print("MEMBERSHIP MANAGEMENT")
		print("[1] Add Member")
		print("[2] Update Member Info")
		print("[3] Search Members")
		print("[4] Assign Role/Committee")
		print("[0] Back to President Dashboard")
		
		choice = validate_input("Enter choice: ")
		
		if choice == '1':
			add_member_to_org(org_id)
		elif choice == '2':
			update_member_in_org(org_id)
		elif choice == '3':
			search_members_in_org(org_id)
		elif choice == '4':
			assign_role_in_org(org_id)
		elif choice == '0':
			return
		else:
			print("Error: Invalid choice")
			input("Press Enter to continue")

def add_member_to_org(org_id):
	clear_console()
	print("ADD MEMBER TO ORGANIZATION")
	
	cursor.execute("SELECT organizationname FROM organization WHERE organizationid = %s", (org_id,))
	org_name = cursor.fetchone()[0]
	print(f"Organization: {org_name} (ID: {org_id})")
	
	member_id_input = input("\nMember ID (leave blank to create new member): ").strip()
	
	if member_id_input: 
		try:
			member_id = int(member_id_input)
			cursor.execute("""
				SELECT m.memberid, m.firstname, m.lastname, m.batch 
				FROM member m WHERE m.memberid = %s
			""", (member_id,))
			member_data = cursor.fetchone()
			
			if not member_data:
				print("Error: Member not found")
				input("Press Enter to continue")
				return
			
			print(f"\nExisting member: {member_data[1]} {member_data[2]} (Batch {member_data[3]})")
			if input("Is this correct? (y/n): ").lower() != 'y':
				input("Press Enter to continue")
				return
		except ValueError:
			print("Error: Member ID must be a number")
			input("Press Enter to continue")
			return
	else:
		print("\nCREATE NEW MEMBER")
		first_name = validate_input("First name: ").title()
		last_name = validate_input("Last name: ").title()
		batch = validate_input("Batch (4-digit year): ", int, min_val=1900, max_val=datetime.now().year)
		gender = validate_input("Gender (Male/Female/Other): ").capitalize()
		degree_program = validate_input("Degree Program: ").title()
		
		cursor.execute("""
			SELECT memberid FROM member 
			WHERE firstname = %s AND lastname = %s AND batch = %s
		""", (first_name, last_name, batch))
		existing_member = cursor.fetchone()
		
		if existing_member:
			print(f"\nWarning: Member already exists with ID: {existing_member[0]}")
			if input("Use this member instead? (y/n): ").lower() == 'y':
				member_id = existing_member[0]
			else:
				input("Press Enter to continue")
				return
		else:
			member_id = get_next_id("member", "memberid")
			try:
				cursor.execute("""
					INSERT INTO member (memberid, firstname, lastname, batch, gender, degreeprogram)
					VALUES (%s, %s, %s, %s, %s, %s)
				""", (member_id, first_name, last_name, batch, gender, degree_program))
				db.commit()
				print(f"\nSuccess: New member created with ID: {member_id}")
			except mysql.connector.Error as err:
				print(f"\nError creating member: {err}")
				db.rollback()
				input("Press Enter to continue")
				return

	cursor.execute("""
		SELECT 1 FROM serves 
		WHERE memberid = %s AND organizationid = %s
		LIMIT 1
	""", (member_id, org_id))
	if cursor.fetchone():
		print("\nWarning: This member is already part of this organization")
		if input("Continue anyway? (y/n): ").lower() != 'y':
			input("Press Enter to continue")
			return

	print("\nENTER MEMBERSHIP DETAILS")
	role = validate_input("Role: ").title()
	status = validate_input("Status (Active/Inactive/Alumni/Expelled/Suspended): ").capitalize()
	committee = validate_input("Committee: ").title()
	semester = validate_input("Semester (1/2): ", int, min_val=1, max_val=2)
	year = validate_input("Academic Year (e.g., 2024-2025): ")
	
	if not re.match(r'^\d{4}-\d{4}$', year):
		print("Error: Academic year must be in format YYYY-YYYY")
		input("Press Enter to continue")
		return

	try:
		cursor.execute("""
			INSERT INTO serves (memberid, organizationid, role, status, committee, semester, academicyear)
			VALUES (%s, %s, %s, %s, %s, %s, %s)
		""", (member_id, org_id, role, status, committee, semester, year))
		db.commit()
		print("\nSuccess: Member added to organization")
	except mysql.connector.Error as err:
		print(f"\nError: {err}")
		db.rollback()
	
	input("Press Enter to continue")

def update_member_in_org(org_id):
	clear_console()
	print("UPDATE MEMBER INFO")
	member_id = validate_input("Member ID to update: ", int)
	
	cursor.execute("SELECT 1 FROM serves WHERE memberid = %s AND organizationid = %s", 
				  (member_id, org_id))
	if not cursor.fetchone():
		print("Error: Member not found in this organization")
		input("Press Enter to continue")
		return
	
	role = input(f"New role (leave blank to keep current): ")
	status = input(f"New status (leave blank to keep current): ")
	committee = input(f"New committee (leave blank to keep current): ")
	
	query = "UPDATE serves SET "
	params = []
	
	if role:
		query += "role = %s, "
		params.append(role)
	if status:
		query += "status = %s, "
		params.append(status)
	if committee:
		query += "committee = %s, "
		params.append(committee)
	
	if not params:
		print("No changes made")
		input("Press Enter to continue")
		return
	
	query = query.rstrip(", ") + " WHERE memberid = %s AND organizationid = %s"
	params.extend([member_id, org_id])
	
	try:
		cursor.execute(query, params)
		db.commit()
		print("Member information updated")
	except mysql.connector.Error as err:
		print(f"Error: {err}")
		db.rollback()
	
	input("Press Enter to continue")

def search_members_in_org(org_id):
	clear_console()
	print("SEARCH MEMBERS")
	search_term = validate_input("Search term (name or ID): ")
	
	query = """
		SELECT m.memberid AS "ID", 
			   m.firstname AS "First Name", 
			   m.lastname AS "Last Name",
			   s.role AS "Role",
			   s.committee AS "Committee",
			   s.status AS "Status"
		FROM member m
		JOIN serves s ON m.memberid = s.memberid
		WHERE s.organizationid = %s
		AND (m.memberid LIKE %s OR m.firstname LIKE %s OR m.lastname LIKE %s)
	"""
	params = (org_id, f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
	show_table(query, params)
	input("Press Enter to continue")

def assign_role_in_org(org_id):
	clear_console()
	print("ASSIGN ROLE/COMMITTEE")
	member_id = validate_input("Member ID: ", int)
	new_role = validate_input("New role: ")
	new_committee = validate_input("New committee: ")
	
	try:
		cursor.execute("""
			UPDATE serves
			SET role = %s, committee = %s
			WHERE memberid = %s AND organizationid = %s
		""", (new_role, new_committee, member_id, org_id))
		db.commit()
		print("Role/committee updated")
	except mysql.connector.Error as err:
		print(f"Error: {err}")
		db.rollback()
	
	input("Press Enter to continue")

def fees_management(org_id):
	while True:
		clear_console()
		print("FEES MANAGEMENT")
		print("[1] Assign Membership Fees")
		print("[2] Record Payment")
		print("[0] Back to President Dashboard")
		
		choice = validate_input("Enter choice: ")
		
		if choice == '1':
			assign_membership_fees(org_id)
		elif choice == '2':
			record_payment(org_id)
		elif choice == '0':
			return
		else:
			print("Error: Invalid choice")
			input("Press Enter to continue")

def assign_membership_fees(org_id):
	clear_console()
	print("ASSIGN MEMBERSHIP FEES")
	semester = validate_input("Semester (1/2): ", int)
	year = validate_input("Academic Year (e.g., 2024-2025): ")
	amount = validate_input("Amount due: ", float)
	due_date = validate_input("Payment due date (YYYY-MM-DD): ")
	
	cursor.execute("""
		SELECT memberid FROM serves
		WHERE organizationid = %s AND status = 'active'
	""", (org_id,))
	members = cursor.fetchall()
	
	try:
		for member in members:
			fee_id = get_next_id("fee", "feeid")
			cursor.execute("""
				INSERT INTO fee (feeid, semester, academicyear, totaldue, totalpaid, (totaldue - totalpaid),
								paymentstatus, paymentduedate, memberid, organizationid)
				VALUES (%s, %s, %s, %s, 0, %s, 'unpaid', %s, %s, %s)
			""", (fee_id, semester, year, amount, amount, due_date, member[0], org_id))
		
		db.commit()
		print(f"Fees assigned to {len(members)} members")
	except mysql.connector.Error as err:
		print(f"Error: {err}")
		db.rollback()
	
	input("Press Enter to continue")

def record_payment(org_id):
	clear_console()
	print("RECORD PAYMENT")
	member_id = validate_input("Member ID: ", int)
	semester = validate_input("Semester (1/2): ", int)
	year = validate_input("Academic Year (e.g., 2024-2025): ")
	amount = validate_input("Amount paid: ", float)
	payment_date = validate_input("Payment date (YYYY-MM-DD): ")
	
	try:
		cursor.execute("""
			SELECT feeid, totaldue, totalpaid
			FROM fee
			WHERE memberid = %s AND organizationid = %s AND semester = %s AND academicyear = %s
		""", (member_id, org_id, semester, year))
		fee = cursor.fetchone()
		
		if not fee:
			print("Error: No fee record found for this member")
			input("Press Enter to continue")
			return
		
		new_paid = fee[2] + amount
		new_balance = fee[1] - new_paid
		status = 'paid' if new_balance <= 0 else 'unpaid'
		
		cursor.execute("""
			UPDATE fee
			SET totalpaid = %s, balancedue = %s, paymentstatus = %s, datepaid = %s
			WHERE feeid = %s
		""", (new_paid, new_balance, status, payment_date, fee[0]))
		
		db.commit()
		print("Payment recorded")
	except mysql.connector.Error as err:
		print(f"Error: {err}")
		db.rollback()
	
	input("Press Enter to continue")