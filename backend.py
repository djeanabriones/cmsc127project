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

def get_user_org(member_id):
	cursor.execute("""
		SELECT organizationid FROM serves
		WHERE memberid = %s
		ORDER BY academicyear DESC, semester DESC
		LIMIT 1
	""", (member_id,))
	result = cursor.fetchone()
	return result[0] if result else None

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