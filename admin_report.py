

import mysql.connector
from datetime import datetime
from utility import clear_console, validate_input, get_next_id, db, cursor, validate_batch, show_table


def admin_reports():
	while True:
		clear_console()
		print("VIEW REPORTS")
		print("[1] View all members with filters")
		print("[2] View members with unpaid fees")
		print("[3] View member's unpaid fees across all orgs")
		print("[4] View executive committee members")
		print("[5] View presidents history")
		print("[6] View late payments")
		print("[7] View active/inactive percentage")
		print("[8] View alumni members")
		print("[9] View financial summary")
		print("[10] View highest debt member")
		print("[0] Back to Admin Menu")
		
		choice = validate_input("Enter choice: ")
		
		if choice == '1':
			admin_report_members_by_filters()
		elif choice == '2':
			admin_report_unpaid_members()
		elif choice == '3':
			admin_report_member_unpaid_all_orgs()
		elif choice == '4':
			admin_report_exec_committee()
		elif choice == '5':
			admin_report_presidents_history()
		elif choice == '6':
			admin_report_late_payments()
		elif choice == '7':
			admin_report_active_inactive_percentage()
		elif choice == '8':
			admin_report_alumni_members()
		elif choice == '9':
			admin_report_financial_summary()
		elif choice == '10':
			admin_report_highest_debt_member()
		elif choice == '0':
			return
		else:
			print("Error: Invalid choice")
			input("Press Enter to continue")

# Check Individual report functions 
def admin_report_members_by_filters():
	clear_console()
	print("REPORT 1: MEMBERS BY FILTERS")
	org_id = input("Organization ID: ")
	
	cursor.execute("SELECT 1 FROM organization WHERE organizationid = %s", (org_id,))
	if not cursor.fetchone():
		print("Organization not found")
		input("Press Enter to continue")
		return
	
	role = input("Role (leave blank for all): ") or None
	status = input("Status (leave blank for all): ") or None
	gender = input("Gender (leave blank for all): ") or None
	degree = input("Degree Program (leave blank for all): ") or None
	batch = input("Batch (leave blank for all): ") or None

	query = """
		SELECT m.memberid AS "ID", 
			   m.firstname AS "First Name", 
			   m.lastname AS "Last Name",
			   m.gender AS "Gender",
			   m.degreeprogram AS "Degree Program",
			   m.batch AS "Batch",
			   s.role AS "Role",
			   s.status AS "Status",
			   s.committee AS "Committee",
			   s.semester AS "Semester",
			   s.academicyear AS "Academic Year"
		FROM member m
		JOIN serves s ON m.memberid = s.memberid
		WHERE s.organizationid = %s
	"""
	params = [org_id]
	
	if role:
		query += " AND s.role = %s"
		params.append(role)
	if status:
		query += " AND s.status = %s"
		params.append(status)
	if gender:
		query += " AND m.gender = %s"
		params.append(gender)
	if degree:
		query += " AND m.degreeprogram = %s"
		params.append(degree)
	if batch:
		query += " AND m.batch = %s"
		params.append(batch)
	
	show_table(query, params)
	input("Press Enter to continue")


def admin_report_unpaid_members():
	clear_console()
	print("REPORT 2: MEMBERS WITH UNPAID FEES")
	org_id = input("Organization ID: ")
	semester = input("Semester (1/2): ")
	year = input("Academic Year (e.g., 2024-2025): ")
	
	query = """
		SELECT m.memberid AS "ID", 
			   m.firstname AS "First Name", 
			   m.lastname AS "Last Name",
			   f.totaldue AS "Total Due",
			   f.totalpaid AS "Total Paid",
			   (f.totaldue - f.totalpaid) AS "Balance Due",
			   f.paymentduedate AS "Due Date"
		FROM member m
		JOIN fee f ON m.memberid = f.memberid
		WHERE f.organizationid = %s AND f.semester = %s AND f.academicyear = %s
		AND f.paymentstatus = 'unpaid'
		ORDER BY (f.totaldue - f.totalpaid) DESC
	"""
	show_table(query, (org_id, semester, year))
	input("Press Enter to continue")

def admin_report_member_unpaid_all_orgs():
	clear_console()
	print("REPORT 3: MEMBER'S UNPAID FEES ACROSS ALL ORGS")
	member_id = input("Member ID: ")
	
	query = """
		SELECT o.organizationname AS "Organization", 
			   f.semester AS "Semester", 
			   f.academicyear AS "Academic Year",
			   f.totaldue AS "Total Due",
			   f.totalpaid AS "Total Paid",
			   (f.totaldue - f.totalpaid) AS "Balance Due",
			   f.paymentduedate AS "Due Date"
		FROM fee f
		JOIN organization o ON f.organizationid = o.organizationid
		WHERE f.memberid = %s AND f.paymentstatus = 'unpaid'
		ORDER BY (f.totaldue - f.totalpaid) DESC
	"""
	show_table(query, (member_id,))
	input("Press Enter to continue")

def admin_report_exec_committee():
	clear_console()
	print("REPORT 4: EXECUTIVE COMMITTEE MEMBERS")
	org_id = input("Organization ID: ")
	year = input("Academic Year (e.g., 2024-2025): ")
	
	query = """
		SELECT m.memberid AS "ID", 
			   m.firstname AS "First Name", 
			   m.lastname AS "Last Name",
			   s.role AS "Role",
			   s.committee AS "Committee"
		FROM member m
		JOIN serves s ON m.memberid = s.memberid
		WHERE s.organizationid = %s AND s.academicyear = %s
		AND s.committee = 'Executive'
		ORDER BY s.role
	"""
	show_table(query, (org_id, year))
	input("Press Enter to continue")

def admin_report_presidents_history():
	clear_console()
	print("REPORT 5: PRESIDENTS HISTORY")
	org_id = input("Organization ID: ")
	
	query = """
		SELECT m.memberid AS "ID", 
			   m.firstname AS "First Name", 
			   m.lastname AS "Last Name",
			   s.academicyear AS "Academic Year"
		FROM member m
		JOIN serves s ON m.memberid = s.memberid
		WHERE s.organizationid = %s AND s.role = 'President'
		ORDER BY s.academicyear DESC
	"""
	show_table(query, (org_id,))
	input("Press Enter to continue")

def admin_report_late_payments():
	clear_console()
	print("REPORT 6: LATE PAYMENTS")
	org_id = input("Organization ID: ")
	semester = input("Semester (1/2): ")
	year = input("Academic Year (e.g., 2024-2025): ")
	
	query = """
		SELECT m.memberid AS "ID", 
			   m.firstname AS "First Name", 
			   m.lastname AS "Last Name",
			   f.totaldue AS "Total Due",
			   f.paymentduedate AS "Due Date",
			   f.datepaid AS "Date Paid",
			   DATEDIFF(f.datepaid, f.paymentduedate) AS "Days Late"
		FROM member m
		JOIN fee f ON m.memberid = f.memberid
		WHERE f.organizationid = %s AND f.semester = %s AND f.academicyear = %s
		AND f.datepaid > f.paymentduedate
		ORDER BY DATEDIFF(f.datepaid, f.paymentduedate) DESC
	"""
	show_table(query, (org_id, semester, year))
	input("Press Enter to continue")

def admin_report_active_inactive_percentage():
	clear_console()
	print("REPORT 7: ACTIVE/INACTIVE PERCENTAGE")
	org_id = input("Organization ID: ")
	n_semesters = int(input("Number of semesters to analyze: "))
	
	query = """
		WITH semester_dates AS (
		  SELECT DISTINCT
			semester,
			academicyear,
			STR_TO_DATE(
			  CASE semester
				WHEN 1 THEN CONCAT(LEFT(academicyear, 4), '-08-01')
				WHEN 2 THEN CONCAT(RIGHT(academicyear, 4), '-01-01')
			  END,
			  '%Y-%m-%d'
			) AS sort_date
		  FROM serves
		  WHERE organizationid = %s
		),
		last_n_semesters AS (
		  SELECT semester, academicyear
		  FROM semester_dates
		  ORDER BY sort_date DESC
		  LIMIT %s
		),
		status_counts AS (
		  SELECT 
			s.status,
			COUNT(*) AS count
		  FROM serves s
		  JOIN last_n_semesters lns
			ON s.semester = lns.semester AND s.academicyear = lns.academicyear
		  WHERE s.organizationid = %s 
			AND s.status IN ('Active', 'Inactive')
		  GROUP BY s.status
		),
		total_active_inactive AS (
		  SELECT SUM(count) AS total
		  FROM status_counts
		)
		SELECT 
		  sc.status AS "Status", 
		  sc.count AS "Count",
		  ROUND(100.0 * sc.count / t.total, 2) AS "Percentage"
		FROM status_counts sc
		CROSS JOIN total_active_inactive t
		ORDER BY sc.status DESC
	"""
	show_table(query, (org_id, n_semesters, org_id))
	input("Press Enter to continue")

def admin_report_alumni_members():
	clear_console()
	print("REPORT 8: ALUMNI MEMBERS")
	org_id = input("Organization ID: ")
	as_of_date = input("As of date (YYYY-MM-DD, leave blank for today): ") or datetime.now().strftime('%Y-%m-%d')
	
	query = """
		SELECT m.memberid AS "ID", 
			m.firstname AS "First Name", 
			m.lastname AS "Last Name", 
			m.batch AS "Batch", 
			s.alumni_date AS "Alumni Since"
		FROM member m 
		JOIN serves s ON m.memberid = s.memberid
		WHERE s.organizationid = %s
		AND s.status = 'alumni'
		AND s.alumni_date <= %s;
	"""
	show_table(query, (org_id, as_of_date))
	input("Press Enter to continue")

def admin_report_financial_summary():
	clear_console()
	print("REPORT 9: FINANCIAL SUMMARY")
	org_id = input("Organization ID: ")
	as_of_date = input("As of date (YYYY-MM-DD, leave blank for today): ") or datetime.now().strftime('%Y-%m-%d')
	
	query = """
		SELECT 
			SUM(totaldue) AS "Total Due",
			SUM(totalpaid) AS "Total Paid",
			SUM(totaldue - totalpaid) AS "Total Unpaid",
			ROUND(100.0 * SUM(totalpaid) / SUM(totaldue), 2) AS "Payment Percentage"
		FROM fee
		WHERE organizationid = %s AND (datepaid <= %s OR datepaid IS NULL)
	"""
	show_table(query, (org_id, as_of_date))
	input("Press Enter to continue")

def admin_report_highest_debt_member():
	clear_console()
	print("REPORT 10: HIGHEST DEBT MEMBER")
	org_id = input("Organization ID: ")
	semester = input("Semester (1/2): ")
	year = input("Academic Year (e.g., 2024-2025): ")
	
	query = """
		SELECT m.memberid AS "ID", 
			   m.firstname AS "First Name", 
			   m.lastname AS "Last Name",
			   (f.totaldue - f.totalpaid) AS "Balance Due"
		FROM member m
		JOIN fee f ON m.memberid = f.memberid
		WHERE f.organizationid = %s AND f.semester = %s AND f.academicyear = %s
		AND f.paymentstatus = 'unpaid'
		ORDER BY (f.totaldue - f.totalpaid) DESC
		LIMIT 1
	"""
	show_table(query, (org_id, semester, year))
	input("Press Enter to continue")