# utility.py
from datetime import datetime
import os
import platform
import mysql.connector
from tabulate import tabulate

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

def clear_console():
	os.system('cls' if platform.system() == 'Windows' else 'clear')

def get_next_id(table, id_column):
	cursor.execute(f"SELECT MAX({id_column}) FROM {table}")
	result = cursor.fetchone()[0]
	return (result or 0) + 1

def show_table(query, params=None):
	cursor.execute(query, params or ())
	results = cursor.fetchall()
	if cursor.description:
		headers = [i[0] for i in cursor.description]
		print(tabulate(results, headers=headers, tablefmt="grid"))
	else:
		print("No results found")

def validate_input(prompt, input_type=str, allow_empty=False):
	while True:
		try:
			value = input(prompt)
			if not value and not allow_empty:
				print("Error: Input cannot be empty")
				continue
			if input_type == int:
				return int(value)
			elif input_type == float:
				return float(value)
			return value
		except ValueError:
			print(f"Error: Please enter a valid {input_type.__name__}")

#NEW ADDITION

def get_user_org(member_id):
	cursor.execute("""
		SELECT organizationid FROM serves
		WHERE memberid = %s
		ORDER BY academicyear DESC, semester DESC
		LIMIT 1
	""", (member_id,))
	result = cursor.fetchone()
	return result[0] if result else None

def validate_batch():
    current_year = datetime.now().year
    while True:
        # validate_input might accept min_val and max_val; if not, remove them
        batch = validate_input("Batch (4-digit year): ", int, False)
        
        # Check if it's exactly 4 digits
        if len(str(batch)) == 4 and 1900 <= batch <= current_year:
            return batch
        else:
            print("Invalid input: Batch must current {current_year}")
