import customtkinter as ctk
from tkinter import messagebox
import backend as orgsystem  # Your backend module

# Initialize DB tables (creates them if not exist)
orgsystem.create_tables()

class OrgApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.selected_org = None
        self.title("Student Org Management")
        self.geometry("600x400")
        self.resizable(False, False)
        self.user = None
        self.current_user = None  # Track current signed in user

        self.frames = {}
        for F in (
            StartPage, SignUpPage, SignInPage, DashboardPage, FeePage, ReportPage,
            UserDashboardPage, JoinOrgPage, AdminDashboardPage, OrgSelectPage,
            AdminMemberPage, AdminFeePage, AdminReportPage, AdminOrgDashboardPage
        ):
            # Pass app instance only to SignUpPage, SignInPage
            if F in (SignUpPage, SignInPage):
                frame = F(self, self)
            else:
                frame = F(self)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(StartPage)

    def show_frame(self, frame_class, *args, **kwargs):
        if frame_class not in self.frames:
            frame = frame_class(self, *args, **kwargs)
            self.frames[frame_class] = frame
            frame.pack(fill="both", expand=True)
        else:
            frame = self.frames[frame_class]
            frame.tkraise()

    def show_home(self):
        # current_user assumed to be dict with 'role' and 'memberid'
        if self.current_user and self.current_user.get("role") == "admin":
            self.show_frame(AdminDashboardPage)
        else:
            self.user = self.current_user
            self.show_frame(UserDashboardPage)


# --- Pages ---

class StartPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Welcome to Student Org System", font=("Arial", 20)).pack(pady=40)
        ctk.CTkButton(self, text="Sign In", command=lambda: master.show_frame(SignInPage)).pack(pady=10)
        ctk.CTkButton(self, text="Sign Up", command=lambda: master.show_frame(SignUpPage)).pack(pady=10)


class SignUpPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(expand=True, fill="both", padx=20, pady=20)

        self.entries = {}
        fields = [
            ("First Name", "firstname"),
            ("Last Name", "lastname"),
            ("Batch", "batch"),
            ("Gender (Male/Female)", "gender"),
            ("Degree Program", "degreeprogram"),
        ]

        for label, key in fields:
            ctk.CTkLabel(scroll, text=label).pack(pady=5)
            entry = ctk.CTkEntry(scroll)
            entry.pack(pady=5)
            self.entries[key] = entry

        ctk.CTkButton(scroll, text="Sign Up", command=self.sign_up).pack(pady=20)

    def sign_up(self):
        data = {key: entry.get() for key, entry in self.entries.items()}

        # Basic validation
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return

        if not data["batch"].isdigit():
            messagebox.showerror("Error", "Batch must be a number.")
            return

        # Call signup function - simplified, no optional join_organization params here
        result = orgsystem.signup(
            first_name=data["firstname"],
            last_name=data["lastname"],
            batch=int(data["batch"]),
            gender=data["gender"],
            degree_program=data["degreeprogram"]
        )

        if result.get("success"):
            messagebox.showinfo("Success", f"Account created! Member ID: {result['member_id']}")
            self.app.show_frame(SignInPage)
        else:
            messagebox.showerror("Error", f"Signup failed: {result.get('error', 'Unknown error')}")


class SignInPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        ctk.CTkLabel(self, text="Member ID").pack(pady=10)
        self.member_id_entry = ctk.CTkEntry(self)
        self.member_id_entry.pack(pady=5)

        ctk.CTkButton(self, text="Sign In", command=self.sign_in).pack(pady=20)

    def sign_in(self):
        member_id_str = self.member_id_entry.get()
        if not member_id_str.isdigit():
            messagebox.showerror("Error", "Member ID must be a number")
            return

        member_id = int(member_id_str)
        result = orgsystem.signin(member_id)

        if not result.get("success"):
            messagebox.showerror("Sign In Failed", result.get("error", "Unknown error"))
        else:
            # Set current_user for the app
            self.app.current_user = result
            self.app.user = result

            messagebox.showinfo("Welcome", f"Welcome back, {result['firstname']} {result['lastname']} (Role: {result['role']})")

            # Role check to open dashboards
            if result["role"].lower() == "admin":
                self.app.show_frame(AdminDashboardPage)
            else:
                self.app.show_frame(UserDashboardPage)


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.label = ctk.CTkLabel(self, text="", font=("Arial", 18))
        self.label.pack(pady=30)
        ctk.CTkButton(self, text="Manage Fees", command=lambda: master.show_frame(FeePage)).pack(pady=10)
        ctk.CTkButton(self, text="Manage Members", command=lambda: master.show_frame(MemberPage, organization_id=self.master.selected_org)).pack(pady=10)
        ctk.CTkButton(self, text="Generate Report", command=lambda: master.show_frame(ReportPage)).pack(pady=10)
        ctk.CTkButton(self, text="Logout", command=self.logout).pack(pady=20)

    def tkraise(self, *args, **kwargs):
        user = self.master.user
        if user:
            self.label.configure(text=f"Welcome, {user['firstname']} {user['lastname']}")
        else:
            self.label.configure(text="Welcome!")
        super().tkraise(*args, **kwargs)

    def logout(self):
        self.master.user = None
        self.master.current_user = None
        self.master.show_frame(StartPage)


class FeePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.fees_text = ctk.CTkTextbox(self, height=150, width=400)
        self.fees_text.pack(pady=10)
        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Enter fee amount")
        self.amount_entry.pack(pady=5)
        ctk.CTkButton(self, text="Add Fee", command=self.add_fee).pack(pady=5)
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(DashboardPage)).pack(pady=10)

    def tkraise(self, *args, **kwargs):
        self.refresh_fees()
        super().tkraise(*args, **kwargs)

    def refresh_fees(self):
        self.fees_text.delete("1.0", "end")
        fees = orgsystem.get_fees(self.master.current_user["memberid"])
        for fee in fees:
            self.fees_text.insert("end", f"Amount: {fee[1]} | Date: {fee[2]}\n")  # Adjust indexes as per your fee table

    def add_fee(self):
        amount = self.amount_entry.get()
        try:
            amt = float(amount)
            orgsystem.add_fee(self.master.current_user["memberid"], amt)
            self.refresh_fees()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")


class MemberPage(ctk.CTkFrame):
    def __init__(self, master, organization_id):
        print("MemberPage loaded")
        super().__init__(master)
        self.master = master
        self.organization_id = organization_id  # Store it for use

        # Add Member Button
        self.add_member_btn = ctk.CTkButton(self, text="Add Member", command=self.open_add_member_dialog)
        self.add_member_btn.pack(pady=10)

        # Scrollable Frame for Table
        self.member_frame = ctk.CTkScrollableFrame(self)
        self.member_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_members()

    def refresh_members(self):
        for widget in self.member_frame.winfo_children():
            widget.destroy()

        headers = ["Mem ID", "Name", "Role", "Status", "Edit", "Delete"]
        for col, text in enumerate(headers):
            label = ctk.CTkLabel(self.member_frame, text=text, font=("Arial", 12, "bold"))
            label.grid(row=0, column=col, padx=5, pady=5)

        # Now only fetch members for the selected organization
        members = orgsystem.get_members_by_org(self.organization_id)

        for row, member in enumerate(members, start=1):
            mem_id, name, role, status = member

            ctk.CTkLabel(self.member_frame, text=str(mem_id)).grid(row=row, column=0, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=name).grid(row=row, column=1, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=role).grid(row=row, column=2, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=status).grid(row=row, column=3, padx=5, pady=2)

            edit_btn = ctk.CTkButton(self.member_frame, text="Edit", width=50, command=lambda m=member: self.edit_member(m))
            edit_btn.grid(row=row, column=4, padx=5)

            del_btn = ctk.CTkButton(self.member_frame, text="Delete", width=50, fg_color="red", command=lambda m=member: self.delete_member(m))
            del_btn.grid(row=row, column=5, padx=5)

    def open_add_member_dialog(self):
        # You can implement a popup dialog here for adding member
        messagebox.showinfo("Add", "Show add member form here")

    def edit_member(self, member):
        # Open dialog to edit member
        messagebox.showinfo("Edit", f"Edit Member {member[0]} - {member[1]}")

    def delete_member(self, member):
        confirm = messagebox.askyesno("Confirm Delete", f"Delete member {member[1]}?")
        if confirm:
            orgsystem.delete_member(member[0])
            self.refresh_members()


class ReportPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.report_text = ctk.CTkTextbox(self, height=250, width=450)
        self.report_text.pack(pady=10)
        ctk.CTkButton(self, text="Generate Report", command=self.generate_report).pack(pady=5)
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(DashboardPage)).pack(pady=10)

    def generate_report(self):
        self.report_text.delete("1.0", "end")
        report = orgsystem.generate_report(self.master.current_user["memberid"])
        self.report_text.insert("end", report)

class UserDashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        ctk.CTkLabel(self, text="User Home", font=("Arial", 18)).pack(pady=20)
        self.welcome_label = ctk.CTkLabel(self, text="")
        self.welcome_label.pack(pady=5)

        ctk.CTkButton(self, text="View My Orgs", command=self.show_orgs).pack(pady=5)
        ctk.CTkButton(self, text="Join an Organization", command=lambda: master.show_frame(JoinOrgPage)).pack(pady=5)
        ctk.CTkButton(self, text="Sign Out", command=self.logout).pack(pady=20)

    def tkraise(self, *args, **kwargs):
        user = self.master.user
        self.welcome_label.configure(text=f"Welcome, {user['firstname']} {user['lastname']}")
        super().tkraise(*args, **kwargs)

    def show_orgs(self):
        orgs = orgsystem.get_user_organizations(self.master.user["member_id"])

        if not orgs:
            messagebox.showinfo("Organizations", "You have not joined any organizations.")
            return

        # Create a popup or a new window to list orgs
        org_window = ctk.CTkToplevel(self)
        org_window.title("My Organizations")
        org_window.geometry("400x400")

        ctk.CTkLabel(org_window, text="Your Organizations", font=("Arial", 16)).pack(pady=10)

        for org_id, org_name in orgs:
            btn = ctk.CTkButton(
                org_window,
                text=f"{org_id} - {org_name}",
                command=lambda oid=org_id, oname=org_name: self.show_dues(oid, oname)
            )
            btn.pack(pady=5)

    def show_dues(self, org_id, org_name):
        dues = orgsystem.get_unpaid_dues(self.master.user["member_id"], org_id)

        dues_window = ctk.CTkToplevel(self)
        dues_window.title(f"Dues - {org_name}")
        dues_window.geometry("400x300")

        ctk.CTkLabel(dues_window, text=f"Unpaid Dues for {org_name}", font=("Arial", 14)).pack(pady=10)

        if not dues:
            ctk.CTkLabel(dues_window, text="No unpaid dues!").pack(pady=5)
        else:
            for amount, duedate in dues:
                ctk.CTkLabel(dues_window, text=f"Amount: ₱{amount:.2f} | Due: {duedate}").pack(pady=3)

    def logout(self):
        self.master.user = None
        self.master.show_frame(StartPage)

class JoinOrgPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Join an Organization", font=("Arial", 16)).pack(pady=20)

        # Placeholder fields
        self.org_entry = ctk.CTkEntry(self, placeholder_text="Organization ID")
        self.org_entry.pack(pady=5)
        self.role_entry = ctk.CTkEntry(self, placeholder_text="Role")
        self.role_entry.pack(pady=5)
        self.status_entry = ctk.CTkEntry(self, placeholder_text="Status")
        self.status_entry.pack(pady=5)
        self.committee_entry = ctk.CTkEntry(self, placeholder_text="Committee")
        self.committee_entry.pack(pady=5)
        self.sem_entry = ctk.CTkEntry(self, placeholder_text="Semester")
        self.sem_entry.pack(pady=5)
        self.year_entry = ctk.CTkEntry(self, placeholder_text="Academic Year")
        self.year_entry.pack(pady=5)

        ctk.CTkButton(self, text="Join", command=self.join_org).pack(pady=10)
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(UserDashboardPage)).pack(pady=5)

    def join_org(self):
        print("DEBUG: self.master.user =", self.master.user)

        try:
            member_id = self.master.user["member_id"]
            org_id = int(self.org_entry.get())
            role = self.role_entry.get()
            status = self.status_entry.get()
            committee = self.committee_entry.get()
            semester = int(self.sem_entry.get())
            year = self.year_entry.get()

            if not all([org_id, role, status, committee, semester, year]):
                messagebox.showerror("Error", "All fields are required.")
                return

            orgsystem.cursor.execute("""
                INSERT INTO serves (memberid, organizationid, role, status, committee, semester, academicyear)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (member_id, org_id, role, status, committee, semester, year))
            orgsystem.db.commit()

            messagebox.showinfo("Success", f"You have successfully joined organization {org_id}")
            self.master.show_frame(UserDashboardPage)

        except Exception as e:
            messagebox.showerror("Join Failed", str(e))


class AdminDashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Admin Dashboard", font=("Arial", 18)).pack(pady=20)

        ctk.CTkButton(self, text="Select Organization", command=lambda: master.show_frame(OrgSelectPage)).pack(pady=10)
        ctk.CTkButton(self, text="Sign Out", command=self.logout).pack(pady=20)

    def logout(self):
        self.master.user = None
        self.master.show_frame(StartPage)

def open_admin_dashboard(master):
    # master is your main window or controller that manages frames
    master.show_frame(AdminDashboardPage)

class OrgSelectPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="Select Organization", font=("Arial", 16)).pack(pady=10)

        self.org_entry = ctk.CTkEntry(self, placeholder_text="Enter Organization ID")
        self.org_entry.pack(pady=5)

        ctk.CTkButton(self, text="Set Organization", command=self.set_org).pack(pady=5)

        self.new_org_name = ctk.CTkEntry(self, placeholder_text="New Organization Name")
        self.new_org_name.pack(pady=5)
        ctk.CTkButton(self, text="Add Organization", command=self.add_org).pack(pady=5)

        # ctk.CTkButton(self, text="Manage Members", command=lambda: master.show_frame(AdminMemberPage)).pack(pady=5)
        # ctk.CTkButton(self, text="Manage Fees", command=lambda: master.show_frame(AdminFeePage)).pack(pady=5)
        # ctk.CTkButton(self, text="Reports", command=lambda: master.show_frame(AdminReportPage)).pack(pady=5)
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(AdminDashboardPage)).pack(pady=10)

    def set_org(self):
        org_id = self.org_entry.get()
        if not org_id.isdigit():
            messagebox.showerror("Error", "Organization ID must be numeric.")
            return
        self.master.selected_org = int(org_id)
        messagebox.showinfo("Success", f"Managing Organization {org_id}")
        
        # Pass the org ID to MemberPage
        self.master.show_frame(MemberPage, organization_id=self.master.selected_org)



    def add_org(self):
        name = self.new_org_name.get()
        if not name:
            messagebox.showerror("Error", "Organization name is required.")
            return
        try:
            org_id = orgsystem.get_next_id("organization", "organizationid")
            orgsystem.cursor.execute("INSERT INTO organization (organizationid, organizationname) VALUES (%s, %s)", (org_id, name))
            orgsystem.db.commit()
            messagebox.showinfo("Success", f"Added '{name}' with ID {org_id}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

class AdminOrgDashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Manage Selected Organization", font=("Arial", 16)).pack(pady=10)
        self.org_label = ctk.CTkLabel(self, text="")
        self.org_label.pack(pady=5)

        ctk.CTkButton(self, text="Manage Members", command=lambda: master.show_frame(MemberPage)).pack(pady=5)
        ctk.CTkButton(self, text="Manage Fees", command=lambda: master.show_frame(AdminFeePage)).pack(pady=5)
        ctk.CTkButton(self, text="Generate Report", command=lambda: master.show_frame(AdminReportPage)).pack(pady=5)
        ctk.CTkButton(self, text="Back to Dashboard", command=lambda: master.show_frame(AdminDashboardPage)).pack(pady=10)

    def tkraise(self, *args, **kwargs):
        selected_org = self.master.selected_org
        self.org_label.configure(text=f"Organization ID: {selected_org}" if selected_org else "No organization selected.")
        super().tkraise(*args, **kwargs)



class AdminMemberPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Manage Members", font=("Arial", 16)).pack(pady=10)

        # self.search_entry = ctk.CTkEntry(self, placeholder_text="Search (Name/Role)")
        # self.search_entry.pack(pady=3)

        # ctk.CTkButton(self, text="Search", command=self.search_members).pack(pady=3)

        self.result_box = ctk.CTkTextbox(self, height=300)
        self.result_box.pack(pady=10)

        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(OrgSelectPage)).pack(pady=10)

    # def search_members(self):
    #     org_id = self.master.selected_org
    #     if not org_id:
    #         messagebox.showerror("Error", "No organization selected.")
    #         return

    #     term = self.search_entry.get()
    #     query = """
    #         SELECT m.firstname, m.lastname, s.role, s.committee, s.status
    #         FROM member m JOIN serves s ON m.memberid = s.memberid
    #         WHERE s.organizationid = %s AND (
    #             m.firstname LIKE %s OR m.lastname LIKE %s OR s.role LIKE %s
    #             OR s.status LIKE %s OR s.committee LIKE %s
    #         )
    #     """
    #     like = f"%{term}%"
    #     try:
    #         orgsystem.cursor.execute(query, (org_id, like, like, like, like, like))
    #         results = orgsystem.cursor.fetchall()
    #         self.result_box.delete("1.0", "end")
    #         for r in results:
    #             self.result_box.insert("end", f"{r[0]} {r[1]} | Role: {r[2]}, Committee: {r[3]}, Status: {r[4]}\n")
    #     except Exception as e:
    #         messagebox.showerror("Error", str(e))


class AdminFeePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Manage Fees", font=("Arial", 16)).pack(pady=20)
        ctk.CTkLabel(self, text="Fee management UI goes here...").pack(pady=10)
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(OrgSelectPage)).pack(pady=10)

class AdminReportPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Reports", font=("Arial", 16)).pack(pady=10)

        ctk.CTkButton(self, text="View Members", command=self.view_members).pack(pady=5)

        self.report_box = ctk.CTkTextbox(self, height=300)
        self.report_box.pack(pady=10)

        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(OrgSelectPage)).pack(pady=10)

    def view_members(self):
        org_id = self.master.selected_org
        if not org_id:
            messagebox.showerror("Error", "No organization selected.")
            return

        try:
            query = """
                SELECT m.firstname, m.lastname, s.role, s.status
                FROM member m
                JOIN serves s ON m.memberid = s.memberid
                WHERE s.organizationid = %s
            """
            orgsystem.cursor.execute(query, (org_id,))
            results = orgsystem.cursor.fetchall()
            self.report_box.delete("1.0", "end")
            for row in results:
                self.report_box.insert("end", f"{row[0]} {row[1]} | Role: {row[2]}, Status: {row[3]}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))




# Run the app
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    orgsystem.set_role("admin", 1)

    app = OrgApp()
    app.mainloop()
