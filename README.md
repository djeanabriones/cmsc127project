# Student Organization Management System

A database-driven application for managing student organizations, memberships, fees, and reports at the University of the Philippines Los Baños (UPLB).

## 📌 Features

### Core Functionality
- **Organization Management**
	- Add/update/delete organizations
	- Search for organizations
	- Show all organizations

- **Membership Management**
	- Add/update/delete members
	- Track roles (President, Treasurer, etc.)
	- Track status (active, inactive, alumni, etc.)
	- Support for multiple organization memberships

- **Fees Management**
	- Track membership fees and dues
	- Record payments
	- Generate financial reports


### User Roles
- **Admin**: Full system access
- **President**: Organization-specific management
- **Member**: View personal info and dues

## 🛠️ Technology Stack

- **Backend**: Python
- **Database**: MySQL/MariaDB
- **GUI**: CustomTkinter
- **Dependencies**:
	- `mysql-connector-python`
	- `tabulate`
	- `customtkinter`
	- `tkcalendar`

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL/MariaDB server
- Git (optional)

### Steps
1. **Clone the repository**:
	 ```bash
	 git clone [repository-url]
	 cd student-org-system
	 ```

2. **Set up database**:  
	 Run the SQL script to create tables and sample data:  
	 ```bash
	 mysql -u root -p < milestone02.sql
	 ```

3. **Install dependencies**:  
	 ```bash
	 pip install -r requirements.txt
	 ```

4. **Configure database connection**:  
	 Edit `db_connection.py` with your credentials:  
	 ```python
	 db = mysql.connector.connect(
			 host="localhost",
			 user="your_username",
			 password="your_password",
			 database="org_management"
	 )
	 ```

5. **Run the application**:  
	 Terminal version:  
	 ```bash
	 python org_management.py
	 ```  
	 GUI version:  
	 ```bash
	 python gui_main.py
	 ```

## 📂 Project Structure

```
student-org-system/
├── admin_dashboard.py     # Admin management functions
├── admin_report.py        # Reporting module
├── backend.py             # Core database operations
├── db_connection.py       # Database config
├── gui_main.py            # Modern GUI interface
├── member.py              # Member functions
├── milestone03.sql        # Database schema + sample data
├── org_management.py      # Main application entry
├── president.py           # President functions
└── utility.py             # Helper functions
```

## 👥 User Guide

### Signing In  
Launch `org_management.py`

Use these test accounts:

- Admin: ID 1  
- President: ID 1 (set as president in sample data)  
- Member: IDs 2-10  

### Key Features by Role

- **Admins** can:  
	- Manage all organizations  
	- Create reports  
	- Modify any member data  

- **Presidents** can:  
	- Manage their organization  
	- Assign roles  
	- Track dues  

- **Members** can:  
	- View their organizations  
	- Check unpaid fees  
	- Update personal info  

## 📊 Sample Reports

The system generates 10 standard reports including:

-- 1. View all members of the organization by role, status, gender, degree program, batch (year of membership), and committee. (Note: we assume one committee membership only per organization per semester)
-- 2. View members for a given organization with unpaid membership fees or dues for a given semester and academic year.
-- 3. View a member’s unpaid membership fees or dues for all their organizations (Member’s POV).
-- 4. View all executive committee members of a given organization for a given academic year.
-- 5. View all Presidents (or any other role) of a given organization for every academic year in reverse chronological order (current to past).
-- 6. View all late payments made by all members of a given organization for a given semester and academic year.
-- 7. View the percentage of active vs inactive members of a given organization for the last n semesters. (Note: n is a positive integer)
-- 8. View all alumni members of a given organization as of a given date.
-- 9. View the total amount of unpaid and paid fees or dues of a given organization as of a given date.
-- 10. View the member/s with the highest debt of a given organization for a given semester.

## 🙏 Credits

**Developed for**:
	- CMSC 127 - File Processing and Database Systems  
	- University of the Philippines Los Baños  
	- AY 2024-2025

**Developed by**:
	- Briones, Djeana Carel
	- Ferrer, Joremze
	- Rebugio, Robin Drey 

