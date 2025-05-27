from utility import clear_console, validate_input, get_next_id, db, cursor, validate_batch
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
