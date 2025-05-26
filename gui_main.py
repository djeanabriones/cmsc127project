import customtkinter as ctk
from tkinter import messagebox
import backend as orgsystem# Your backend module

# Initialize DB
orgsystem.create_tables()

# Main App
class OrgApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Org Management")
        self.geometry("600x400")
        self.resizable(False, False)
        self.user = None

        self.frames = {}
        for F in (
            StartPage, SignUpPage, SignInPage, DashboardPage, FeePage, MemberPage, ReportPage,
            UserDashboardPage, JoinOrgPage, AdminDashboardPage, OrgSelectPage,
            AdminMemberPage, AdminFeePage, AdminReportPage
        ):

            if F in (SignUpPage, SignInPage):
                frame = F(self, self)  # master, app
            else:
                frame = F(self)  # only master
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(StartPage)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

    def show_home(self):
        if self.current_user["memberid"] == 1:
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
            ("Degree Program", "degreeprogram")
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

        result = orgsystem.signup(
            data["firstname"], data["lastname"],
            int(data["batch"]), data["gender"], data["degreeprogram"]
        )

        if result["success"]:
            messagebox.showinfo("Success", result["message"])
            self.app.show_frame(SignInPage)
        else:
            messagebox.showerror("Sign Up Failed", result["message"])



class SignInPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.pack(padx=20, pady=20)

        ctk.CTkLabel(self, text="Member ID").pack(pady=10)
        self.member_id_entry = ctk.CTkEntry(self)
        self.member_id_entry.pack(pady=5)

        self.signin_button = ctk.CTkButton(self, text="Sign In", command=self.sign_in)
        self.signin_button.pack(pady=20)

    def sign_in(self):
        member_id = self.member_id_entry.get()
        if not member_id.isdigit():
            messagebox.showerror("Error", "Member ID must be a number.")
            return

        result = orgsystem.signin(int(member_id))
        if result["success"]:
            self.app.current_user = result["user"]
            self.app.show_home()
        else:
            messagebox.showerror("Sign In Failed", result["message"])

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.label = ctk.CTkLabel(self, text="", font=("Arial", 18))
        self.label.pack(pady=30)
        ctk.CTkButton(self, text="Manage Fees", command=lambda: master.show_frame(FeePage)).pack(pady=10)
        ctk.CTkButton(self, text="Manage Members", command=lambda: master.show_frame(MemberPage)).pack(pady=10)
        ctk.CTkButton(self, text="Generate Report", command=lambda: master.show_frame(ReportPage)).pack(pady=10)
        ctk.CTkButton(self, text="Logout", command=self.logout).pack(pady=20)

    def tkraise(self, *args, **kwargs):
        self.label.configure(text=f"Welcome, {self.master.user}")
        super().tkraise(*args, **kwargs)

    def logout(self):
        self.master.user = None
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
        fees = orgsystem.get_fees(self.master.user)
        for fee in fees:
            self.fees_text.insert("end", f"{fee[1]}\n")

    def add_fee(self):
        amount = self.amount_entry.get()
        try:
            amt = float(amount)
            orgsystem.add_fee(self.master.user, amt)
            self.refresh_fees()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")


class MemberPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.members_text = ctk.CTkTextbox(self, height=150, width=400)
        self.members_text.pack(pady=10)

        self.name = ctk.CTkEntry(self, placeholder_text="Name")
        self.name.pack(pady=3)
        self.pos = ctk.CTkEntry(self, placeholder_text="Position")
        self.pos.pack(pady=3)
        self.yr = ctk.CTkEntry(self, placeholder_text="Year Level")
        self.yr.pack(pady=3)

        ctk.CTkButton(self, text="Add Member", command=self.add_member).pack(pady=3)
        ctk.CTkButton(self, text="Remove Member", command=self.remove_member).pack(pady=3)
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(DashboardPage)).pack(pady=10)

    def tkraise(self, *args, **kwargs):
        self.refresh_members()
        super().tkraise(*args, **kwargs)

    def refresh_members(self):
        self.members_text.delete("1.0", "end")
        members = orgsystem.get_members(self.master.user)
        for m in members:
            self.members_text.insert("end", f"{m[0]} - {m[1]} ({m[2]})\n")

    def add_member(self):
        orgsystem.add_member(
            self.master.user,
            self.name.get(),
            self.pos.get(),
            self.yr.get()
        )
        self.refresh_members()

    def remove_member(self):
        orgsystem.remove_member(self.master.user, self.name.get())
        self.refresh_members()


class ReportPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.report_text = ctk.CTkTextbox(self, height=200, width=500)
        self.report_text.pack(pady=20)
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(DashboardPage)).pack(pady=10)

    def tkraise(self, *args, **kwargs):
        self.report_text.delete("1.0", "end")
        report = orgsystem.generate_report(self.master.user)
        self.report_text.insert("end", report)
        super().tkraise(*args, **kwargs)

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
        # Placeholder
        messagebox.showinfo("Organizations", "Display of user organizations goes here.")

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
        # Placeholder only
        messagebox.showinfo("Info", "Joining organization is not yet implemented.")

class AdminDashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Admin Dashboard", font=("Arial", 18)).pack(pady=20)

        ctk.CTkButton(self, text="Select Organization", command=lambda: master.show_frame(OrgSelectPage)).pack(pady=10)
        ctk.CTkButton(self, text="Sign Out", command=self.logout).pack(pady=20)

    def logout(self):
        self.master.user = None
        self.master.show_frame(StartPage)

class OrgSelectPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="Select Organization", font=("Arial", 16)).pack(pady=20)

        # Placeholder org selection
        self.org_entry = ctk.CTkEntry(self, placeholder_text="Enter Organization ID")
        self.org_entry.pack(pady=10)

        ctk.CTkButton(self, text="Manage Members", command=lambda: master.show_frame(AdminMemberPage)).pack(pady=5)
        ctk.CTkButton(self, text="Manage Fees", command=lambda: master.show_frame(AdminFeePage)).pack(pady=5)
        ctk.CTkButton(self, text="Reports", command=lambda: master.show_frame(AdminReportPage)).pack(pady=5)
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(AdminDashboardPage)).pack(pady=20)

class AdminMemberPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Manage Members", font=("Arial", 16)).pack(pady=20)
        # Placeholder
        ctk.CTkLabel(self, text="Add/Update/Delete/Search Members...").pack(pady=10)
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(OrgSelectPage)).pack(pady=10)

class AdminFeePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Manage Fees", font=("Arial", 16)).pack(pady=20)
        ctk.CTkLabel(self, text="Fee management UI goes here...").pack(pady=10)
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(OrgSelectPage)).pack(pady=10)

class AdminReportPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Reports", font=("Arial", 16)).pack(pady=20)
        ctk.CTkLabel(self, text="Reporting and analytics UI goes here...").pack(pady=10)
        ctk.CTkButton(self, text="Back", command=lambda: master.show_frame(OrgSelectPage)).pack(pady=10)



# Run the app
if __name__ == "__main__":
    ctk.set_appearance_mode("light")  # You can change to "dark"
    ctk.set_default_color_theme("blue")
    app = OrgApp()
    app.mainloop()
