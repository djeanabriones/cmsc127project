from utility import clear_console, validate_input, get_next_id, db, cursor, validate_batch, show_table

# Member Dashboard
def member_menu(member_id):
	while True:
		clear_console()
		print("MEMBER DASHBOARD")
		print("[1] View My Organizations")
		print("[2] View My Dues")
		print("[0] Sign Out")
		
		choice = validate_input("Enter choice: ")
		
		if choice == '1':
			view_member_organizations(member_id)
		elif choice == '2':
			view_member_dues(member_id)
		elif choice == '0':
			return
		else:
			print("Error: Invalid choice")
			input("Press Enter to continue")

def view_member_organizations(member_id):
	clear_console()
	print("YOUR ORGANIZATIONS")
	query = """
		SELECT o.organizationname AS "Organization", 
			   s.role AS "Role", 
			   s.committee AS "Committee", 
			   s.status AS "Status",
			   s.semester AS "Semester",
			   s.academicyear AS "Academic Year"
		FROM serves s
		JOIN organization o ON s.organizationid = o.organizationid
		WHERE s.memberid = %s
	"""
	show_table(query, (member_id,))
	input("Press Enter to continue")

def view_member_dues(member_id):
	clear_console()
	print("YOUR DUES")
	query = """
		SELECT o.organizationname AS "Organization", 
			   f.semester AS "Semester", 
			   f.academicyear AS "Academic Year",
			   f.totaldue AS "Total Due",
			   f.totalpaid AS "Total Paid",
			   (f.totaldue - f.totalpaid) AS "Balance Due",
			   f.paymentstatus AS "Status",
			   f.paymentduedate AS "Due Date",
			   f.datepaid AS "Date Paid"
		FROM fee f
		JOIN organization o ON f.organizationid = o.organizationid
		WHERE f.memberid = %s
	"""
	show_table(query, (member_id,))
	input("Press Enter to continue")
