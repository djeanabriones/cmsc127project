import datetime
from doctest import master
import random
import string
import customtkinter as ctk
from tkinter import dialog, messagebox, Toplevel, simpledialog, ttk
from tkcalendar import Calendar, DateEntry
import backend as orgsystem
from db_connection import db, cursor
from utility import get_next_id

# Create table if it doesn't exist
orgsystem.create_tables()

class OrgApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.selected_org = None
        self.title("Student Org Management")
        self.geometry("600x400")
        self.attributes("-fullscreen", True)
        # Exit fullscreen with ESC
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.user = None
        self.current_user = None  #Track current signed in user

        self.frames = {}
        for F in (
            StartPage, SignUpPage, SignInPage, DashboardPage, FeePage, ReportPage,
            UserDashboardPage, AdminDashboardPage, OrgSelectPage,
            AdminMemberPage, AdminFeePage, AdminReportPage, AdminOrgDashboardPage
        ):
            #Pass app instance only to SignUpPage, SignInPage
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
            if 'organization_id' in kwargs and hasattr(frame, 'set_organization'):
                frame.set_organization(kwargs['organization_id'])
        frame.tkraise()

    def open_admin_dashboard(self, member_id=None, org_id=None):
        self.show_frame(AdminDashboardPage)

    def open_user_dashboard(self, member_id):
        self.show_frame(UserDashboardPage, member_id=member_id)


    def show_home(self):
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

        ctk.CTkButton(
            self,
            text="Sign In as User",
            command=lambda: master.show_frame(SignInPage, as_admin=False)
        ).pack(pady=10)

        ctk.CTkButton(
            self,
            text="Sign In as Admin",
            command=lambda: master.show_frame(SignInPage, as_admin=True)
        ).pack(pady=10)



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

        # Call signup function 
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

#Sign in page where you can sign in as user / admin
class SignInPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        ctk.CTkLabel(self, text="Username").pack(pady=(20, 5))
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Password").pack(pady=(10, 5))
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self, text="Sign In as User", command=lambda: self.sign_in(as_admin=False)).pack(pady=(15, 5))
        ctk.CTkButton(self, text="Sign In as Admin", command=lambda: self.sign_in(as_admin=True)).pack(pady=(0, 20))
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(StartPage)).pack(pady=10)
    
    def sign_in(self, as_admin=False):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        try:
            cursor.execute("""
                SELECT m.memberid, m.password, s.role, s.organizationid, m.firstname, m.lastname
                FROM member m
                LEFT JOIN serves s ON m.memberid = s.memberid
                WHERE m.username = %s
            """, (username,))

            result = cursor.fetchone()

            if result is None:
                messagebox.showerror("Login Failed", "User not found.")
                return

            member_id, stored_password, role, org_id, firstname, lastname = result

            if password != stored_password:
                messagebox.showerror("Login Failed", "Incorrect password.")
                return

            self.master.user = {
                "member_id": member_id,
                "role": role,
                "organization_id": org_id,
                "firstname": firstname,
                "lastname": lastname
            }

            if as_admin:
                if member_id == 1 or role in ("President", "Vice President", "Secretary", "Treasurer"):
                    self.master.open_admin_dashboard(member_id, org_id)
                else:
                    messagebox.showerror("Access Denied", "You do not have admin privileges.")
            else:
                self.master.open_user_dashboard(member_id)

        except Exception as e:
            messagebox.showerror("Error", str(e))



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
        self.organization_id = organization_id

        # Add Member Button
        self.add_member_btn = ctk.CTkButton(self, text="Add Member", command=self.open_add_member_dialog)
        self.add_member_btn.pack(pady=10)

        self.show_chart_btn = ctk.CTkButton(self, text="Show Active/Inactive Chart", command=self.show_status_chart)
        self.show_chart_btn.pack(pady=10)

        # Search Frame (above filters)
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.pack(fill="x", pady=(10,5))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search member by Name or ID", textvariable=self.search_var, width=250)
        self.search_entry.pack(side="left", padx=(10,5))

        self.search_button = ctk.CTkButton(self.search_frame, text="Search", command=self.search_members)
        self.search_button.pack(side="left", padx=(0,10))

        # --- FILTERS ---
        self.filters_frame = ctk.CTkFrame(self)
        self.filters_frame.pack(fill="x", padx=20, pady=(10, 0))

        # Add number of semesters input
        self.semesters_var = ctk.StringVar(value="4")  # default 4 semesters
        self.semesters_entry = ctk.CTkEntry(self.filters_frame, textvariable=self.semesters_var, width=50)
        self.semesters_entry.pack(side="left", padx=5)

        # Role filter
        self.role_filter = ctk.CTkOptionMenu(self.filters_frame, values=["All", "President", "Vice President", "Secretary", "Treasurer", "Member"], command=lambda _: self.refresh_members())
        self.role_filter.set("All")
        self.role_filter.pack(side="left", padx=5)

        # Status filter
        self.status_filter = ctk.CTkOptionMenu(self.filters_frame, values=["All", "Active", "Inactive", "Alumni"], command=lambda _: self.refresh_members())
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=5)   

        # As of date (readonly entry) and calendar button inside filters_frame for consistent layout
        self.as_of_date_var = ctk.StringVar()
        self.as_of_date_entry = ctk.CTkEntry(self.filters_frame, textvariable=self.as_of_date_var, placeholder_text="As of date (YYYY-MM-DD)", state="readonly", width=120)
        self.as_of_date_entry.pack(side="left", padx=5)

        self.calendar_btn = ctk.CTkButton(self.filters_frame, text="Pick Date", width=80, command=self.open_calendar_popup)
        self.calendar_btn.pack(side="left", padx=5)

        # Refresh members after date changes
        self.as_of_date_var.trace_add("write", lambda *args: self.refresh_members())

        # Other filters
        self.gender_filter = ctk.CTkOptionMenu(self.filters_frame, values=["All", "Male", "Female"], command=lambda _: self.refresh_members())
        self.gender_filter.set("All")
        self.gender_filter.pack(side="left", padx=5)

        self.degree_filter = ctk.CTkEntry(self.filters_frame, placeholder_text="Degree Program")
        self.degree_filter.pack(side="left", padx=5)
        self.degree_filter.bind("<KeyRelease>", lambda event: self.refresh_members())

        self.batch_filter = ctk.CTkEntry(self.filters_frame, placeholder_text="Batch")
        self.batch_filter.pack(side="left", padx=5)
        self.batch_filter.bind("<KeyRelease>", lambda event: self.refresh_members())

        self.academic_year_filter = ctk.CTkEntry(self.filters_frame, placeholder_text="Academic Year")
        self.academic_year_filter.pack(side="left", padx=5)
        self.academic_year_filter.bind("<KeyRelease>", lambda event: self.refresh_members())

        self.academic_sort_filter = ctk.CTkOptionMenu(
            self.filters_frame,
            values=["Newest First", "Oldest First"],
            command=lambda _: self.refresh_members()
        )
        self.academic_sort_filter.set("Newest First")
        self.academic_sort_filter.pack(side="left", padx=5)

        self.committee_filter = ctk.CTkEntry(self.filters_frame, placeholder_text="Committee")
        self.committee_filter.pack(side="left", padx=5)
        self.committee_filter.bind("<KeyRelease>", lambda event: self.refresh_members())

        self.reset_btn = ctk.CTkButton(self.filters_frame, text="Reset", command=self.reset_filters)
        self.reset_btn.pack(side="left", padx=5)

        # Member frame for the list
        self.member_frame = ctk.CTkScrollableFrame(self)
        self.member_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_members()

        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(OrgSelectPage)).pack(pady=10)

    def open_calendar_popup(self):
        def on_date_selected():
            selected_date = cal.selection_get()
            self.as_of_date_var.set(selected_date.strftime("%Y-%m-%d"))
            popup.destroy()

        popup = Toplevel(self)
        popup.title("Select Date")
        cal = Calendar(popup, selectmode='day')
        cal.pack(padx=10, pady=10)

        ok_btn = ctk.CTkButton(popup, text="OK", command=on_date_selected)
        ok_btn.pack(pady=5)

    def refresh_members(self, members=None):
        for widget in self.member_frame.winfo_children():
            widget.destroy()

        headers = ["Mem ID", "Name", "Role", "Status", "Gender", "Degree", "Batch", "Academic Year", "Committee", "Username", "Password", "Edit", "Delete"]

        for col, text in enumerate(headers):
            label = ctk.CTkLabel(self.member_frame, text=text, font=("Arial", 12, "bold"))
            label.grid(row=0, column=col, padx=5, pady=5)

        # If members not passed, fetch all members and apply filters
        if members is None:
            all_members = orgsystem.get_members_by_org(self.organization_id)

            # Gather filter values
            role_val = self.role_filter.get()
            status_val = self.status_filter.get()
            gender_val = self.gender_filter.get()
            degree_val = self.degree_filter.get().strip().lower()
            batch_val = self.batch_filter.get().strip()
            academic_year_val = self.academic_year_filter.get().strip()
            committee_val = self.committee_filter.get().strip().lower()

            # Get the "as of" date
            as_of_date_str = self.as_of_date_var.get().strip()
            as_of_date = None
            try:
                as_of_date = datetime.datetime.strptime(as_of_date_str, "%Y-%m-%d").date() if as_of_date_str else None
            except ValueError:
                as_of_date = None  # fallback if format is invalid

            filtered_members = []
            for member in all_members:
                mem_id, name, role, status, gender, degree, batch, academicyear, committee, username, password = member[:11]



                if role_val != "All" and role != role_val:
                    continue
                if status_val != "All" and status != status_val:
                    continue
                if gender_val != "All" and gender != gender_val:
                    continue
                if degree_val and degree_val not in degree.lower():
                    continue
                if batch_val and str(batch) != batch_val:
                    continue
                if committee_val and committee_val not in (committee or "").lower():
                    continue
                if academic_year_val and academic_year_val not in (academicyear or ""):
                    continue

                # Filter alumni based on as_of_date
                if status == "Alumni" and as_of_date:
                    cursor.execute("""
                        SELECT alumni_date FROM serves WHERE memberid = %s AND organizationid = %s
                    """, (mem_id, self.organization_id))
                    result = cursor.fetchone()
                    if result and result[0]:
                        alumni_date = result[0]
                        if alumni_date is not None and as_of_date is not None and alumni_date > as_of_date:
                            continue

                filtered_members.append(member)

            # Sort by academic year string descending/ascending
            sort_order = self.academic_sort_filter.get()
            reverse_sort = sort_order == "Newest First"
            filtered_members.sort(
                key=lambda m: m[7] if m[7] is not None else "",  # default to empty string
                reverse=reverse_sort
            )
            # index 7 = academicyear

            members = filtered_members

        # Now display members passed or filtered
        for row, member in enumerate(members, start=1):
            mem_id, name, role, status, gender, degree, batch, academicyear, committee, username, password = member[:11]

            ctk.CTkLabel(self.member_frame, text=str(mem_id)).grid(row=row, column=0, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=name).grid(row=row, column=1, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=role).grid(row=row, column=2, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=status).grid(row=row, column=3, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=gender).grid(row=row, column=4, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=degree).grid(row=row, column=5, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=str(batch)).grid(row=row, column=6, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=str(academicyear)).grid(row=row, column=7, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=committee or "").grid(row=row, column=8, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=username).grid(row=row, column=9, padx=5, pady=2)
            ctk.CTkLabel(self.member_frame, text=password).grid(row=row, column=10, padx=5, pady=2)

            edit_btn = ctk.CTkButton(self.member_frame, text="Edit", width=50, command=lambda m=member: self.edit_member(m))
            edit_btn.grid(row=row, column=11, padx=5)

            del_btn = ctk.CTkButton(self.member_frame, text="Delete", width=50, fg_color="red", command=lambda m=member: self.delete_member(m))
            del_btn.grid(row=row, column=12, padx=5)

    def reset_filters(self):
        self.role_filter.set("All")
        self.status_filter.set("All")
        self.gender_filter.set("All")
        self.degree_filter.delete(0, "end")
        self.batch_filter.delete(0, "end")
        self.academic_year_filter.delete(0, "end")
        self.as_of_date_var.set("")
        self.committee_filter.delete(0, "end")
        self.refresh_members()


    def open_add_member_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Member")

        # Text Entry Fields
        labels = ["First Name", "Last Name", "Batch", "Degree Program", "Committee", "Semester", "Academic Year"]
        entries = {}

        for i, label in enumerate(labels):
            ctk.CTkLabel(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ctk.CTkEntry(dialog)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[label] = entry

        # Dropdowns
        gender_options = ["Male", "Female"]
        role_options = ["President", "Vice President", "Secretary", "Treasurer", "Member"]
        status_options = ["Active", "Inactive", "Alumni"]

        gender_label_row = len(labels)
        role_label_row = gender_label_row + 1
        status_label_row = role_label_row + 1
        button_row = status_label_row + 1

        ctk.CTkLabel(dialog, text="Gender").grid(row=gender_label_row, column=0, padx=10, pady=5, sticky="e")
        gender_menu = ctk.CTkOptionMenu(dialog, values=gender_options)
        gender_menu.grid(row=gender_label_row, column=1, padx=10, pady=5)

        ctk.CTkLabel(dialog, text="Role").grid(row=role_label_row, column=0, padx=10, pady=5, sticky="e")
        role_menu = ctk.CTkOptionMenu(dialog, values=role_options)
        role_menu.grid(row=role_label_row, column=1, padx=10, pady=5)

        ctk.CTkLabel(dialog, text="Status").grid(row=status_label_row, column=0, padx=10, pady=5, sticky="e")
        status_menu = ctk.CTkOptionMenu(dialog, values=status_options)
        status_menu.grid(row=status_label_row, column=1, padx=10, pady=5)

        def generate_credentials(firstname, lastname):
            base_username = (firstname[0] + lastname).lower()
            suffix = ''.join(random.choices(string.digits, k=3))
            username = base_username + suffix
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            return username, password

        def submit_member():
            data = {key: entry.get().strip() for key, entry in entries.items()}
            data["Gender"] = gender_menu.get()
            data["Role"] = role_menu.get()
            data["Status"] = status_menu.get()

            if not all(data.values()):
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            try:
                firstname = data["First Name"]
                lastname = data["Last Name"]
                username, password = generate_credentials(firstname, lastname)

                # Insert into member
                new_member_id = orgsystem.get_next_id("member", "memberid")
                orgsystem.cursor.execute("""
                    INSERT INTO member (memberid, firstname, lastname, batch, gender, degreeprogram, username, password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    new_member_id,
                    firstname,
                    lastname,
                    data["Batch"],
                    data["Gender"],
                    data["Degree Program"],
                    username,
                    password
                ))

                # Insert into serves
                orgsystem.cursor.execute("""
                    INSERT INTO serves (memberid, organizationid, role, status, committee, semester, academicyear)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    new_member_id,
                    self.organization_id,
                    data["Role"],
                    data["Status"],
                    data["Committee"],
                    data["Semester"],
                    data["Academic Year"]
                ))

                orgsystem.db.commit()
                messagebox.showinfo("Success", f"Member added successfully.\n\nUsername: {username}\nPassword: {password}")
                dialog.destroy()
                self.refresh_members()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                orgsystem.db.rollback()

        ctk.CTkButton(dialog, text="Submit", command=submit_member).grid(row=button_row, columnspan=2, pady=10)

    def open_calendar_popup(self):
        def on_date_selected():
            selected_date = cal.selection_get()
            self.as_of_date_var.set(selected_date.strftime("%Y-%m-%d"))
            popup.destroy()

        popup = Toplevel(self)
        popup.title("Select Date")
        cal = Calendar(popup, selectmode='day')
        cal.pack(padx=10, pady=10)

        ok_btn = ctk.CTkButton(popup, text="OK", command=on_date_selected)
        ok_btn.pack(pady=5)
        
    def edit_member(self, member):
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Member")

        # Unpack all values from the member tuple
        memberid, name, role, status, gender, degreeprogram, batch, academicyear, committee = member
        firstname, lastname = name.split(' ', 1) if ' ' in name else (name, "")

        # Labels & Entry Fields
        ctk.CTkLabel(edit_window, text="First Name").pack()
        fname_entry = ctk.CTkEntry(edit_window)
        fname_entry.insert(0, firstname)
        fname_entry.pack()

        ctk.CTkLabel(edit_window, text="Last Name").pack()
        lname_entry = ctk.CTkEntry(edit_window)
        lname_entry.insert(0, lastname)
        lname_entry.pack()

        ctk.CTkLabel(edit_window, text="Batch").pack()
        batch_entry = ctk.CTkEntry(edit_window)
        batch_entry.insert(0, str(batch))
        batch_entry.pack()

        ctk.CTkLabel(edit_window, text="Degree Program").pack()
        degree_entry = ctk.CTkEntry(edit_window)
        degree_entry.insert(0, degreeprogram)
        degree_entry.pack()

        ctk.CTkLabel(edit_window, text="Gender").pack()
        gender_menu = ctk.CTkOptionMenu(edit_window, values=["Male", "Female"])
        gender_menu.set(gender)
        gender_menu.pack()

        ctk.CTkLabel(edit_window, text="Role").pack()
        role_menu = ctk.CTkOptionMenu(edit_window, values=["President", "Vice President", "Secretary", "Treasurer", "Member"])
        role_menu.set(role)
        role_menu.pack()

        ctk.CTkLabel(edit_window, text="Status").pack()
        status_menu = ctk.CTkOptionMenu(edit_window, values=["Active", "Inactive", "Alumni"])
        status_menu.set(status)
        status_menu.pack()

        def save_changes():
            try:
                updated_firstname = fname_entry.get().strip()
                updated_lastname = lname_entry.get().strip()
                updated_batch = int(batch_entry.get())
                updated_degree = degree_entry.get().strip()
                updated_gender = gender_menu.get()
                updated_role = role_menu.get()
                updated_status = status_menu.get()

                result = orgsystem.update_member_full(
                    memberid=memberid,
                    org_id=self.organization_id,
                    firstname=updated_firstname,
                    lastname=updated_lastname,
                    batch=updated_batch,
                    gender=updated_gender,
                    degreeprogram=updated_degree,
                    role=updated_role,
                    status=updated_status,
                )

                if result["success"]:
                    messagebox.showinfo("Success", "Member updated successfully.")
                    edit_window.destroy()
                    self.refresh_members()
                else:
                    messagebox.showerror("Error", f"Update failed: {result['error']}")

            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid number for Batch.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                print("Error updating member:", e)

        ctk.CTkButton(edit_window, text="Save", command=save_changes).pack(pady=10)

    def show_status_chart(self):
        try:
            n = int(self.semesters_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for semesters")
            return

        data = orgsystem.get_active_inactive_percentages(self.organization_id, n)
        orgsystem.show_overall_status_chart(data)

    def search_members(self):
        query = self.search_entry.get()  # get user input search text
        filtered_members = orgsystem.search_members(self.organization_id, query)
        self.refresh_members(filtered_members)  # pass filtered list here


    def display_members(self, members):
        # Clear current member list in UI (e.g., table or listbox)
        self.members_listbox.delete(0, 'end')
        # Add new members from the list
        for member in members:
            self.members_listbox.insert('end', f"{member[0]} - {member[1]}")  # example format

    def delete_member(self, member):
        confirm = messagebox.askyesno("Confirm Delete", f"Delete member {member[1]}?")
        if confirm:
            orgsystem.delete_member(member[0], self.organization_id)
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
    def __init__(self, master, member_id=None):
        super().__init__(master)
        self.master = master
        self.member_id = member_id  # Save member_id for later use

        ctk.CTkLabel(self, text="User Home", font=("Arial", 18)).pack(pady=20)
        self.welcome_label = ctk.CTkLabel(self, text="")
        self.welcome_label.pack(pady=5)

        ctk.CTkButton(self, text="View My Orgs", command=self.show_orgs).pack(pady=5)
        ctk.CTkButton(self, text="Sign Out", command=self.logout).pack(pady=20)

    def tkraise(self, *args, **kwargs):
        # Use member_id to fetch user info if needed
        # Example: get user from master using member_id, or store user info on master
        user = self.master.user if hasattr(self.master, "user") else None

        if user:
            self.welcome_label.configure(text=f"Welcome, {user.get('firstname', '')} {user.get('lastname', '')}")
        else:
            self.welcome_label.configure(text="Welcome!")

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

        # Container frame for org buttons (for potential scroll later)
        self.org_button_frame = ctk.CTkFrame(self)
        self.org_button_frame.pack(pady=5, fill="both", expand=True)

        # Label for current org - hidden initially
        self.current_org_label = ctk.CTkLabel(self, text="", font=("Arial", 14, "bold"))

        # Menu buttons (initially not packed)
        self.manage_members_btn = ctk.CTkButton(self, text="Manage Members",
                                                command=lambda: master.show_frame(MemberPage, organization_id=master.selected_org))
        self.manage_fees_btn = ctk.CTkButton(self, text="Manage Fees",
                                             command=lambda: master.show_frame(AdminFeePage, organization_id=master.selected_org))
        self.reports_btn = ctk.CTkButton(self, text="Reports",
                                         command=lambda: master.show_frame(AdminReportPage))
        self.back_btn = ctk.CTkButton(self, text="Back",
                                      command=lambda: master.show_frame(AdminDashboardPage))
        
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(pady=5, fill="x")

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search organization name...")
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

        search_button = ctk.CTkButton(search_frame, text="Search", command=self.search_organizations)
        search_button.pack(side="right")

        self.load_organizations()

    def load_organizations(self, search_term=""):
        # Clear existing buttons
        for widget in self.org_button_frame.winfo_children():
            widget.destroy()

        try:
            if search_term:
                orgs = orgsystem.search_organizations_by_name(search_term)
            else:
                orgs = orgsystem.get_all_organizations()

            if not orgs:
                messagebox.showinfo("Info", "No organizations found.")
                return

            for org_id, org_name in orgs:
                btn = ctk.CTkButton(
                    self.org_button_frame,
                    text=f"{org_id} - {org_name}",
                    command=lambda oid=org_id, oname=org_name: self.set_org(oid, oname)
                )
                btn.pack(pady=5, fill="x")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load organizations: {e}")

    def search_organizations(self):
        query = self.search_entry.get().strip()
        self.load_organizations(search_term=query)

    def set_org(self, org_id, org_name):
        self.master.selected_org = org_id

        # Hide the org buttons
        self.org_button_frame.pack_forget()

        # Show current org label
        self.current_org_label.configure(text=f"Currently Managing: {org_name}")
        self.current_org_label.pack(pady=10)

        # Show menu buttons
        self.show_menu_buttons()

        self.update_org_btn = ctk.CTkButton(self, text="Update Organization", command=lambda: self.update_organization(org_id, org_name))
        self.update_org_btn.pack(pady=5)

        self.delete_org_btn = ctk.CTkButton(self, text="Delete Organization", command=lambda: self.delete_organization(org_id))
        self.delete_org_btn.pack(pady=5)


        messagebox.showinfo("Success", f"Managing Organization {org_id}")

    def show_menu_buttons(self):
        self.manage_members_btn.pack(pady=5)
        self.manage_fees_btn.pack(pady=5)
        self.reports_btn.pack(pady=5)
        self.back_btn.pack(pady=20)

    def update_organization(self, org_id, old_name):
        new_name = simpledialog.askstring("Update Organization", f"Enter new name for '{old_name}':")
        if not new_name:
            return

        try:
            orgsystem.update_organization_name(org_id, new_name)
            messagebox.showinfo("Success", "Organization name updated.")
            self.current_org_label.configure(text=f"Currently Managing: {new_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update organization: {e}")

    def delete_organization(self, org_id):
        confirm = messagebox.askyesno("Delete Organization", "Are you sure you want to delete this organization? This cannot be undone.")
        if not confirm:
            return

        try:
            orgsystem.delete_organization(org_id)
            messagebox.showinfo("Success", "Organization deleted.")
            self.master.selected_org = None
            self.current_org_label.configure(text="")
            self.manage_members_btn.pack_forget()
            self.manage_fees_btn.pack_forget()
            self.reports_btn.pack_forget()
            self.back_btn.pack_forget()
            self.update_org_btn.pack_forget()
            self.delete_org_btn.pack_forget()
            self.org_button_frame.pack(pady=5, fill="both", expand=True)
            self.load_organizations()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete organization: {e}")

class AdminOrgDashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Manage Selected Organization", font=("Arial", 16)).pack(pady=10)
        self.org_label = ctk.CTkLabel(self, text="")
        self.org_label.pack(pady=5)

        ctk.CTkButton(self, text="Manage Members", command=lambda: master.show_frame(MemberPage)).pack(pady=5)
        ctk.CTkButton(self, text="Manage Fees", command=lambda: master.show_frame(AdminFeePage, organization_id=master.selected_org)).pack(pady=5)
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

class AdminFeePage(ctk.CTkFrame):
    def __init__(self, master, organization_id=None):
        super().__init__(master)
        self.organization_id = organization_id

        ctk.CTkLabel(self, text="Manage Fees", font=("Arial", 16)).pack(pady=20)

        # Tabs for sections
        self.tab_control = ttk.Notebook(self)
        self.tab_assign = ctk.CTkFrame(self.tab_control)
        self.tab_record = ctk.CTkFrame(self.tab_control)
        self.tab_view = ctk.CTkFrame(self.tab_control)

        self.tab_control.add(self.tab_assign, text="Assign Fees")
        self.tab_control.add(self.tab_record, text="Record Payment")
        self.tab_control.add(self.tab_view, text="View Records")
        self.tab_control.pack(expand=1, fill="both")

        self.create_assign_tab()
        self.create_record_tab()
        self.create_view_tab()

        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(OrgSelectPage)).pack(pady=10)

    def set_organization(self, org_id):
        self.organization_id = org_id
        self.view_fee_records()

    def create_assign_tab(self):
        frame = self.tab_assign

        ctk.CTkLabel(frame, text="Semester (1 or 2):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.assign_semester = ctk.CTkEntry(frame)
        self.assign_semester.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Academic Year (e.g. 2024-2025):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.assign_year = ctk.CTkEntry(frame)
        self.assign_year.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Amount Due:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.assign_amount = ctk.CTkEntry(frame)
        self.assign_amount.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Due Date (YYYY-MM-DD):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.assign_due_date = ctk.CTkEntry(frame)
        self.assign_due_date.grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkButton(frame, text="Assign Fees", command=self.assign_fees).grid(row=4, column=0, columnspan=2, pady=10)

    def assign_fees(self):
        # Validate inputs
        try:
            semester = int(self.assign_semester.get())
            if semester not in (1, 2):
                raise ValueError("Semester must be 1 or 2")
            year = self.assign_year.get().strip()
            amount = float(self.assign_amount.get())
            due_date_str = self.assign_due_date.get().strip()
            due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return

        org_id = self.organization_id
        if not org_id:
            messagebox.showerror("Error", "No organization selected.")
            return

        try:
            # Get active members for org
            cursor.execute("SELECT memberid FROM serves WHERE organizationid = %s AND status = 'active'", (org_id,))
            members = cursor.fetchall()

            assigned_count = 0
            for (member_id,) in members:
                cursor.execute("""
                    SELECT 1 FROM fee 
                    WHERE memberid = %s AND organizationid = %s AND semester = %s AND academicyear = %s AND totaldue = %s AND paymentduedate = %s
                """, (member_id, org_id, semester, year, amount, due_date))

                if cursor.fetchone():
                    continue  # Skip exact duplicate


                fee_id = get_next_id("fee", "feeid")
                cursor.execute("""
                    INSERT INTO fee (semester, academicyear, totaldue, totalpaid, balancedue,
                                    paymentstatus, paymentduedate, memberid, organizationid)
                    VALUES (%s, %s, %s, 0, %s, 'unpaid', %s, %s, %s)
                """, (semester, year, amount, amount, due_date, member_id, org_id))

                assigned_count += 1

            db.commit()
            # print(f"Inserting fee: fee_id={fee_id}, semester={semester}, year={year}, amount={amount}, due_date={due_date}, member_id={member_id}, org_id={org_id}")
            messagebox.showinfo("Success", f"Fees assigned to {assigned_count} members.")
        except Exception as e:
            db.rollback()
            messagebox.showerror("Database Error", str(e))

    def create_record_tab(self):
        frame = self.tab_record

        ctk.CTkLabel(frame, text="Member ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.record_member_id = ctk.CTkEntry(frame)
        self.record_member_id.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Semester (1 or 2):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.record_semester = ctk.CTkEntry(frame)
        self.record_semester.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Academic Year:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.record_year = ctk.CTkEntry(frame)
        self.record_year.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Amount Paid:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.record_amount = ctk.CTkEntry(frame)
        self.record_amount.grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Payment Date (YYYY-MM-DD):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.record_payment_date = ctk.CTkEntry(frame)
        self.record_payment_date.grid(row=4, column=1, padx=5, pady=5)

        ctk.CTkButton(frame, text="Record Payment", command=self.record_payment).grid(row=5, column=0, columnspan=2, pady=10)

    def record_payment(self):
        try:
            member_id = int(self.record_member_id.get())
            semester = int(self.record_semester.get())
            year = self.record_year.get().strip()
            amount = float(self.record_amount.get())
            payment_date_str = self.record_payment_date.get().strip()
            payment_date = datetime.datetime.strptime(payment_date_str, "%Y-%m-%d").date()
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return

        org_id = self.organization_id
        if not org_id:
            messagebox.showerror("Error", "No organization selected.")
            return

        try:
            cursor.execute("""
                SELECT feeid, totaldue, totalpaid FROM fee
                WHERE memberid = %s AND organizationid = %s AND semester = %s AND academicyear = %s
            """, (member_id, org_id, semester, year))
            fee = cursor.fetchone()
            if not fee:
                messagebox.showerror("Error", "No fee record found for this member.")
                return

            new_paid = fee[2] + amount
            new_balance = fee[1] - new_paid
            status = 'paid' if new_balance <= 0 else 'unpaid'

            cursor.execute("""
                UPDATE fee SET totalpaid = %s, balancedue = %s, paymentstatus = %s, datepaid = %s
                WHERE feeid = %s
            """, (new_paid, new_balance, status, payment_date, fee[0]))
            db.commit()
            messagebox.showinfo("Success", "Payment recorded.")
        except Exception as e:
            db.rollback()
            messagebox.showerror("Database Error", str(e))

    def create_view_tab(self):
        frame = self.tab_view

        filter_frame = ctk.CTkFrame(frame)
        filter_frame.pack(pady=10, fill="x")

        ctk.CTkLabel(filter_frame, text="Semester:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.view_semester = ctk.CTkEntry(filter_frame)
        self.view_semester.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(filter_frame, text="Academic Year:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.view_year = ctk.CTkEntry(filter_frame)
        self.view_year.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(filter_frame, text="Status:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.view_status = ctk.CTkEntry(filter_frame)
        self.view_status.grid(row=0, column=5, padx=5, pady=5)

        # New: As of Date input
        ctk.CTkLabel(filter_frame, text="As of Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.view_as_of_date = ctk.CTkEntry(filter_frame)
        self.view_as_of_date.grid(row=1, column=1, padx=5, pady=5)

        # New: Late Payments checkbox
        self.view_late_only = ctk.CTkCheckBox(filter_frame, text="Late Payments Only")
        self.view_late_only.grid(row=1, column=2, padx=5, pady=5)

        self.total_paid_label = ctk.CTkLabel(frame, text="Total Paid: 0.00")
        self.total_paid_label.pack(pady=2)

        self.total_unpaid_label = ctk.CTkLabel(frame, text="Total Unpaid: 0.00")
        self.total_unpaid_label.pack(pady=2)

        ctk.CTkButton(filter_frame, text="Filter", command=self.view_fee_records).grid(row=0, column=6, padx=5, pady=5)

        # New: View Totals button
        ctk.CTkButton(filter_frame, text="View Totals", command=self.view_totals).grid(row=1, column=3, padx=5, pady=5)

        # New: View Highest Debt button
        ctk.CTkButton(filter_frame, text="View Highest Debt", command=self.view_highest_debt).grid(row=1, column=4, padx=5, pady=5)

        self.tree = ttk.Treeview(frame, columns=(
            "ID", "First Name", "Last Name", "Semester", "Academic Year", "Total Due", "Total Paid",
            "Balance Due", "Status", "Due Date", "Date Paid"
        ), show="headings")

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)

        self.view_semester.delete(0, "end")
        self.view_year.delete(0, "end")
        self.view_status.delete(0, "end")
        self.view_as_of_date.delete(0, "end")
        self.view_late_only.deselect()

        self.view_fee_records()

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        if self.organization_id:
            self.view_fee_records()
        else:
            for row in self.tree.get_children():
                self.tree.delete(row)

    def view_fee_records(self):
        org_id = self.organization_id
        if not org_id:
            return

        semester = self.view_semester.get().strip()
        year = self.view_year.get().strip()
        status = self.view_status.get().strip()
        as_of_date = self.view_as_of_date.get().strip()
        late_only = self.view_late_only.get()

        query = """
            SELECT m.memberid, m.firstname, m.lastname,
                   f.semester, f.academicyear, f.totaldue, f.totalpaid,
                   (f.totaldue - f.totalpaid) AS balancedue,
                   f.paymentstatus, f.paymentduedate, f.datepaid
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
        if late_only:
            query += " AND f.datepaid IS NOT NULL AND f.datepaid > f.paymentduedate"
        if as_of_date:
            query += " AND f.paymentduedate <= %s"
            params.append(as_of_date)

        query += " ORDER BY f.academicyear DESC, f.semester DESC"

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in rows:
            self.tree.insert("", "end", values=row)

    def view_totals(self):
        org_id = self.organization_id
        if not org_id:
            messagebox.showerror("Error", "No organization selected.")
            return

        as_of_date_str = self.view_as_of_date.get().strip()

        try:
            as_of_date = datetime.datetime.strptime(as_of_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format. Use YYYY-MM-DD.")
            return

        try:
            # cursor.execute("""
            #     SELECT
            #         COALESCE(SUM(CASE WHEN datepaid <= %s THEN totalpaid ELSE 0 END), 0) AS total_paid_by_date,
            #         COALESCE(SUM(CASE WHEN paymentstatus = 'unpaid' THEN balancedue ELSE 0 END), 0) AS total_unpaid_by_date
            #     FROM fee
            #     WHERE organizationid = %s
            # """, (as_of_date, as_of_date, org_id))

            cursor.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN paymentstatus = 'paid' THEN totalpaid ELSE 0 END), 0) AS total_paid,
                    COALESCE(SUM(CASE WHEN paymentstatus = 'unpaid' THEN balancedue ELSE 0 END), 0) AS total_unpaid
                FROM fee
                WHERE organizationid = %s
            """, (org_id,))

            result = cursor.fetchone()

            total_paid = result[0]
            total_unpaid = result[1]

            if not hasattr(self, "total_paid_label"):
                self.total_paid_label = ctk.CTkLabel(self.tab_view, text="")
                self.total_paid_label.pack(pady=(10,0))
            if not hasattr(self, "total_unpaid_label"):
                self.total_unpaid_label = ctk.CTkLabel(self.tab_view, text="")
                self.total_unpaid_label.pack()

            self.total_paid_label.configure(text=f"Total Paid (as of {as_of_date_str}): {total_paid:.2f}")
            self.total_unpaid_label.configure(text=f"Total Unpaid (as of {as_of_date_str}): {total_unpaid:.2f}")

        except Exception as e:
            messagebox.showerror("Database Error", str(e))


    def view_highest_debt(self):
        org_id = self.organization_id
        if not org_id:
            messagebox.showerror("Error", "No organization selected.")
            return

        semester = self.view_semester.get().strip()
        if not semester:
            messagebox.showerror("Input Error", "Please enter a semester to find highest debt.")
            return

        try:
            cursor.execute("""
                WITH max_debt AS (
                    SELECT MAX(balancedue) AS max_bal FROM fee WHERE organizationid = %s AND semester = %s
                )
                SELECT m.memberid, m.firstname, m.lastname, f.balancedue
                FROM fee f
                JOIN member m ON f.memberid = m.memberid, max_debt md
                WHERE f.organizationid = %s AND f.semester = %s AND f.balancedue = md.max_bal
            """, (org_id, semester, org_id, semester))
            results = cursor.fetchall()
            if not results:
                messagebox.showinfo("Highest Debt", "No records found.")
                return

            msg = "Member(s) with highest debt:\n"
            for memberid, fname, lname, debt in results:
                msg += f"{memberid} - {fname} {lname}: {debt}\n"

            messagebox.showinfo("Highest Debt", msg)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

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
