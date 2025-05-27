import os
import platform
import sys
import mysql.connector
from datetime import datetime
from tabulate import tabulate
from admin_dashboard import admin_menu
from db_connection import db, cursor
from president import president_menu
from utility import clear_console, validate_input, get_next_id, db, cursor


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
# cursor = db.cursor()

# # connect database
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="ilove127",
#     database="org_management"
# )

cursor = db.cursor()

def create_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS member(
            memberid INT PRIMARY KEY,
            firstname VARCHAR(50),
            lastname VARCHAR(50),
            batch INT,
            gender VARCHAR(6),
            degreeprogram VARCHAR(50)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organization(
            organizationid INT PRIMARY KEY,
            organizationname VARCHAR(50)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fee(
            feeid INT PRIMARY KEY,
            semester INT,
            academicyear INT,
            totaldue INT,
            totalpaid INT,
            balancedue INT,
            paymentstatus VARCHAR(6),
            paymentduedate DATE,
            datepaid DATE,
            memberid INT,
            organizationid INT,
            FOREIGN KEY (memberid) REFERENCES member(memberid),
            FOREIGN KEY (organizationid) REFERENCES organization(organizationid)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS serves(
            memberid INT,
            organizationid INT,
            role VARCHAR(50),
            status VARCHAR(20),
            committee VARCHAR(50),
            semester INT,
            academicyear INT,
            FOREIGN KEY (memberid) REFERENCES member(memberid),
            FOREIGN KEY (organizationid) REFERENCES organization(organizationid)
        )
    """)

    db.commit()

def signup(first_name, last_name, batch, gender, degree_program,
           join_organization=False, organization_id=None, committee=None,
           semester=None, academic_year=None):
    member_id = get_next_id("member", "memberid")
    
    try:
        cursor.execute("""
            INSERT INTO member (memberid, firstname, lastname, batch, gender, degreeprogram)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (member_id, first_name, last_name, batch, gender, degree_program))
        
        if join_organization:
            cursor.execute("SELECT 1 FROM organization WHERE organizationid = %s", (organization_id,))
            if not cursor.fetchone():
                db.rollback()
                return {"success": False, "error": "Organization does not exist"}
            
            role = "Member"
            status = "active"
            cursor.execute("""
                INSERT INTO serves (memberid, organizationid, role, status, committee, semester, academicyear)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (member_id, organization_id, role, status, committee, semester, academic_year))
        
        db.commit()
        return {"success": True, "member_id": member_id}
    
    except mysql.connector.Error as err:
        db.rollback()
        return {"success": False, "error": str(err)}


def get_user_role(member_id):
    cursor.execute("""
        SELECT role FROM serves
        WHERE memberid = %s
        ORDER BY academicyear DESC, semester DESC
        LIMIT 1
    """, (member_id,))
    result = cursor.fetchone()
    return result[0].lower() if result else "member"

#to set mem 1 as admin lang 
def set_role(role, memberid):
    query = "UPDATE serves SET role = %s WHERE memberid = %s"
    cursor.execute(query, (role, memberid))
    db.commit()

def get_user_organizations(member_id):
	cursor.execute("""
		SELECT o.organizationid, o.organizationname
		FROM serves s
		JOIN organization o ON s.organizationid = o.organizationid
		WHERE s.memberid = %s
		GROUP BY o.organizationid, o.organizationname
		ORDER BY MAX(s.academicyear) DESC, MAX(s.semester) DESC
	""", (member_id,))
	return cursor.fetchall()

def get_unpaid_dues(member_id, organization_id):
    query = """
        SELECT totaldue, paymentduedate
        FROM fee
        WHERE memberid = %s AND organizationid = %s AND paymentstatus = "unpaid"
    """
    cursor.execute(query, (member_id, organization_id))
    return cursor.fetchall()

def signin(member_id):
    cursor.execute("SELECT * FROM member WHERE memberid = %s", (member_id,))
    user = cursor.fetchone()

    if not user:
        return {"success": False, "error": "Member not found"}

    role = get_user_role(member_id)

    return {
        "success": True,
        "member_id": member_id,
        "firstname": user[1],
        "lastname": user[2],
        "role": role
    }

def get_all_members():
    query = """
        SELECT memberid, 
               CONCAT(firstname, ' ', lastname) AS name
        FROM member
    """
    cursor.execute(query)
    raw_members = cursor.fetchall()

    # Add dummy role/status
    members = [(m[0], m[1], "Member", "Active") for m in raw_members]
    return members

def delete_member(memberid):
    cursor.execute("DELETE FROM member WHERE memberid = %s", (memberid,))
    db.commit()

def get_members_by_org(org_id):
    try:
        query = """
            SELECT m.memberid,
                   CONCAT(m.firstname, ' ', m.lastname) AS name,
                   s.role,
                   s.status,
                   m.gender,
                   m.degreeprogram,
                   m.batch,
                   s.academicyear,
                   s.committee
            FROM member m
            JOIN serves s ON m.memberid = s.memberid
            WHERE s.organizationid = %s
        """
        cursor.execute(query, (org_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error in get_members_by_org:", e)
        return []
    
def update_member_full(memberid, org_id, firstname, lastname, batch, gender, degreeprogram, role, status):
    try:
        # Step 1: Fetch the previous status
        cursor.execute("""
            SELECT status FROM serves 
            WHERE memberid = %s AND organizationid = %s
        """, (memberid, org_id))
        prev_status_row = cursor.fetchone()
        prev_status = prev_status_row[0] if prev_status_row else None

        # Step 2: Update the member table
        cursor.execute("""
            UPDATE member SET firstname=%s, lastname=%s, batch=%s, gender=%s, degreeprogram=%s
            WHERE memberid=%s
        """, (firstname, lastname, batch, gender, degreeprogram, memberid))

        # Step 3: Update the serves table
        if status.lower() == 'alumni' and prev_status != 'alumni':
            # Set alumni_date if becoming alumni now
            cursor.execute("""
                UPDATE serves SET role=%s, status=%s, alumni_date=CURDATE()
                WHERE memberid=%s AND organizationid=%s
            """, (role, status, memberid, org_id))
        else:
            # Don't touch alumni_date if not becoming alumni
            cursor.execute("""
                UPDATE serves SET role=%s, status=%s
                WHERE memberid=%s AND organizationid=%s
            """, (role, status, memberid, org_id))

        db.commit()
        return {"success": True}

    except mysql.connector.Error as err:
        db.rollback()
        return {"success": False, "error": str(err)}

    
def get_members_by_org_filtered(self, organization_id, status=None, as_of_date=None):
    query = """
    SELECT m.memberid, 
           CONCAT(m.firstname, ' ', m.lastname) AS name, 
           s.role, s.status, m.gender, m.degree, m.batch, s.academicyear, s.committee
    FROM member m
    JOIN serves s ON m.memberid = s.memberid
    WHERE s.organizationid = %s
    """
    params = [organization_id]

    if status:
        query += " AND s.status = %s"
        params.append(status)

    if as_of_date:
        query += """
        AND STR_TO_DATE(CASE s.semester
            WHEN 1 THEN CONCAT(SUBSTRING(s.academicyear, 1, 4), '-08-01')
            WHEN 2 THEN CONCAT(SUBSTRING(s.academicyear, 6, 4), '-01-01')
            END, '%Y-%m-%d') <= %s
        """
        params.append(as_of_date)

    self.cursor.execute(query, tuple(params))
    return self.cursor.fetchall()



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