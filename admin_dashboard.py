from utility import clear_console, validate_input, get_next_id, db, cursor, validate_batch, show_table
import re
import mysql.connector


# Admin Dashboard
def admin_menu():
    while True:
        clear_console()
        print("ADMIN DASHBOARD")
        print("[1] Add New Organization")
        print("[2] Show All Organizations")
        print("[3] Membership Management")       
        print("[4] Fees Management")
        print("[5] View Reports")
        print("[0] Sign Out")
        
        choice = validate_input("Enter choice: ")
        
        if choice == '1':
            add_organization()
        elif choice == '2':
            show_organizations()
        elif choice == '3':
            admin_membership_management()
        elif choice == '4':
            admin_fees_management()
        elif choice == '5':
            admin_reports()
        elif choice == '0':
            return
        else:
            print("Error: Invalid choice")
            input("Press Enter to continue")


def add_organization():
    clear_console()
    print("ADD NEW ORGANIZATION")
    
    org_id_input = input("Organization ID (leave blank to auto-generate): ").strip()
    
    if org_id_input: 
        try:
            org_id = int(org_id_input)
            cursor.execute("SELECT 1 FROM organization WHERE organizationid = %s", (org_id,))
            if cursor.fetchone():
                print(f"Error: Organization ID {org_id} already exists")
                input("Press Enter to continue")
                return
        except ValueError:
            print("Error: Organization ID must be a number")
            input("Press Enter to continue")
            return
    else:
        org_id = get_next_id("organization", "organizationid")
    
    org_name = validate_input("Organization Name: ")
    
    try:
        cursor.execute("""
            INSERT INTO organization (organizationid, organizationname)
            VALUES (%s, %s)
        """, (org_id, org_name))
        db.commit()
        print(f"Organization '{org_name}' added with ID: {org_id}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()
    
    input("Press Enter to continue")


def show_organizations():
    clear_console()
    print("ALL ORGANIZATIONS")

    cursor.execute("SELECT organizationid, organizationname FROM organization")
    orgs = cursor.fetchall()
        
    if not orgs:
        print("No organizations found.")
        input("Press Enter to return to Admin Menu")
        return

    print("\nOrganizations:")
    for i, org in enumerate(orgs, 1):
        print(f"[{i}] {org[1]} (ID: {org[0]})")

    print("\nPress Enter to return to Admin Menu")
    input() 


def admin_membership_management():
    while True:
        clear_console()
        print("MEMBERSHIP MANAGEMENT")
        print("[1] Add Member to Organization")
        print("[2] Update Member Info")
        print("[3] Delete Member from Organization")
        print("[4] Search Members")
        print("[5] Assign Role/Committee")
        print("[0] Back to Admin Menu")
        
        choice = validate_input("Enter choice: ")
        
        if choice == '1':
            admin_add_member()
        elif choice == '2':
            admin_update_member()
        elif choice == '3':
            admin_delete_member()
        elif choice == '4':
            admin_search_members()
        elif choice == '5':
            admin_assign_role()
        elif choice == '0':
            return
        else:
            print("Error: Invalid choice")
            input("Press Enter to continue")


def admin_add_member():
    clear_console()
    print("ADD MEMBER TO ORGANIZATION")
    
    org_id_input = input("Organization ID (leave blank to list organizations): ").strip()
    
    if not org_id_input:
        cursor.execute("SELECT organizationid, organizationname FROM organization")
        orgs = cursor.fetchall()
        if not orgs:
            print("No organizations found.")
            input("Press Enter to continue")
            return
        
        print("\nAvailable Organizations:")
        for org in orgs:
            print(f"{org[0]} - {org[1]}")
        print()
        org_id_input = input("Enter Organization ID from list above: ").strip()
    
    try:
        org_id = int(org_id_input)
    except ValueError:
        print("Error: Organization ID must be a number")
        input("Press Enter to continue")
        return
    
    cursor.execute("SELECT organizationname FROM organization WHERE organizationid = %s", (org_id,))
    org_result = cursor.fetchone()
    if not org_result:
        print("Error: Organization not found")
        input("Press Enter to continue")
        return
    org_name = org_result[0]
    print(f"\nAdding to organization: {org_name}")

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
        batch = validate_batch()
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
    
    # Return if semester is not 1 or 2
    try:
        semester = int(validate_input("Semester (1/2): "))
        if semester not in [1, 2]:
            print("Invalid semester. Returning to menu...")
            input("Press Enter to continue")
            return
    except ValueError:
        print("Error: Semester must be 1 or 2")
        input("Press Enter to continue")
        return

    year = validate_input("Academic Year (YYYY-YYYY): ").strip()
    if not re.match(r'^\d{4}-\d{4}$', year):
        print(f"DEBUG: '{year}' (length: {len(year)})")

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

def admin_update_member():
	clear_console()
	print("UPDATE MEMBER INFO")
	
	org_id = validate_input("Organization ID: ", int)
	member_id = validate_input("Member ID: ", int)
	
	cursor.execute("SELECT 1 FROM serves WHERE memberid = %s AND organizationid = %s", 
				  (member_id, org_id))
	if not cursor.fetchone():
		print("Error: Member not found in this organization")
		input("Press Enter to continue")
		return
	
	cursor.execute("""
		SELECT role, status, committee
		FROM serves
		WHERE memberid = %s AND organizationid = %s
	""", (member_id, org_id))
	current_info = cursor.fetchone()
	if not current_info:
		print("Error: Member information not found")
		input("Press Enter to continue")
		return
	
	current_role, current_status, current_committee = current_info
	
	print(f"\nCurrent Info:")
	print(f"Role: {current_role}")
	print(f"Status: {current_status}")
	print(f"Committee: {current_committee}\n")
	
	role = input(f"New role (leave blank to keep '{current_role}'): ") or current_role
	status = input(f"New status (leave blank to keep '{current_status}'): ") or current_status
	committee = input(f"New committee (leave blank to keep '{current_committee}'): ") or current_committee
	
	try:
		cursor.execute("""
			UPDATE serves
			SET role = %s, status = %s, committee = %s
			WHERE memberid = %s AND organizationid = %s
		""", (role, status, committee, member_id, org_id))
		db.commit()
		print("Member information updated")
	except mysql.connector.Error as err:
		print(f"Error: {err}")
		db.rollback()
	
	input("Press Enter to continue")

def admin_delete_member():
	clear_console()
	print("DELETE MEMBER")
	
	org_id = validate_input("Organization ID: ", int)
	member_id = validate_input("Member ID to delete: ", int)
	
	confirm = input(f"Are you sure you want to remove member {member_id} from organization {org_id}? (y/n): ").lower()
	if confirm != 'y':
		print("Deletion canceled")
		input("Press Enter to continue")
		return
	
	try:
		cursor.execute("""
			DELETE FROM serves
			WHERE memberid = %s AND organizationid = %s
		""", (member_id, org_id))
		
		cursor.execute("""
			DELETE FROM fee
			WHERE memberid = %s AND organizationid = %s
		""", (member_id, org_id))
		
		db.commit()
		print("Member removed from organization")
	except mysql.connector.Error as err:
		print(f"Error: {err}")
		db.rollback()
	
	input("Press Enter to continue")

def admin_search_members():
	clear_console()
	print("SEARCH MEMBERS")
	
	org_id = validate_input("Organization ID: ", int)
	search_term = validate_input("Search term (name, ID, role, etc.): ")
	
	query = """
		SELECT m.memberid AS "ID", 
			   m.firstname AS "First Name", 
			   m.lastname AS "Last Name",
			   m.batch AS "Batch",
			   s.role AS "Role",
			   s.status AS "Status",
			   s.committee AS "Committee"
		FROM member m
		JOIN serves s ON m.memberid = s.memberid
		WHERE s.organizationid = %s AND (m.memberid LIKE %s OR m.firstname LIKE %s OR m.lastname LIKE %s 
			 OR s.role LIKE %s OR s.status LIKE %s OR s.committee LIKE %s)
	"""
	search_param = f"%{search_term}%"
	params = (org_id, search_param, search_param, search_param, search_param, search_param, search_param)
	show_table(query, params)
	input("Press Enter to continue")

def admin_assign_role():
	clear_console()
	print("ASSIGN ROLE/COMMITTEE")
	
	org_id = validate_input("Organization ID: ", int)
	member_id = validate_input("Member ID: ", int)
	
	cursor.execute("SELECT 1 FROM serves WHERE memberid = %s AND organizationid = %s", 
				  (member_id, org_id))
	if not cursor.fetchone():
		print("Error: Member not found in this organization")
		input("Press Enter to continue")
		return
	
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

def admin_fees_management():
	while True:
		clear_console()
		print("FEES MANAGEMENT")
		print("[1] Assign Membership Fees")
		print("[2] Record Payment")
		print("[3] View Fee Records")
		print("[0] Back to Admin Dashboard")
		
		choice = validate_input("Enter choice: ")
		
		if choice == '1':
			admin_assign_fees()
		elif choice == '2':
			admin_record_payment()
		elif choice == '3':
			admin_view_fee_records()
		elif choice == '0':
			return
		else:
			print("Error: Invalid choice")
			input("Press Enter to continue")

def admin_assign_fees():
	clear_console()
	print("ASSIGN MEMBERSHIP FEES")
	
	org_id = validate_input("Organization ID: ", int)
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
			cursor.execute("""
				SELECT 1 FROM fee 
				WHERE memberid = %s AND organizationid = %s 
				AND semester = %s AND academicyear = %s
			""", (member[0], org_id, semester, year))
			
			if cursor.fetchone():
				print(f"Fee already exists for member {member[0]}, skipping...")
				continue
			
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

def admin_record_payment():
	clear_console()
	print("RECORD PAYMENT")
	
	org_id = validate_input("Organization ID: ", int)
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

def admin_view_fee_records():
	clear_console()
	print("FEE RECORDS")
	
	org_id = validate_input("Organization ID: ", int)
	semester = input("Semester (1/2, leave blank for all): ") or None
	year = input("Academic Year (leave blank for all): ") or None
	status = input("Payment status (paid/unpaid, leave blank for all): ") or None
	
	query = """
		SELECT m.memberid AS "ID", 
			   m.firstname AS "First Name", 
			   m.lastname AS "Last Name",
			   f.semester AS "Semester",
			   f.academicyear AS "Academic Year",
			   f.totaldue AS "Total Due",
			   f.totalpaid AS "Total Paid",
			   (f.totaldue - f.totalpaid) AS "Balance Due",
			   f.paymentstatus AS "Status",
			   f.paymentduedate AS "Due Date",
			   f.datepaid AS "Date Paid"
		FROM fee f
		JOIN member m ON f.memberid = m.memberid
		WHERE f.organizationid = %s
	"""
	params = [org_id]
	
	if semester:
		query += " AND f.semester = %s"
		params.append(semester)
	if year:
		query += " AND f.academicyear = %s"
		params.append(year)
	if status:
		query += " AND f.paymentstatus = %s"
		params.append(status)
	
	query += " ORDER BY f.academicyear DESC, f.semester DESC"
	
	show_table(query, params)
	input("Press Enter to continue")
