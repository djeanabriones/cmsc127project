import os
import platform
import sys


def clear_console():
    system_platform = platform.system()
    if system_platform == 'Windows':
        os.system('cls')
    else:
        os.system('clear')
    print()

def landingpage():

    while True:
        print("============================================================".center(100))
        print("|                                                          |".center(100))
        print("|                       Welcome to                         |".center(100))
        print("|                                                          |".center(100))
        print("|              ORGANIZATION MANAGEMENT SYSTEM              |".center(100))
        print("|               Sign in or Sign up to start.               |".center(100))
        print("|                                                          |".center(100))
        print("|                      (1) SIGN IN                         |".center(100))
        print("|                      (2) SIGN UP                         |".center(100))
        print("|                      (3) QUIT                            |".center(100))
        print("|                                                          |".center(100))
        print("============================================================".center(100))

        signin_choice = input("Enter choice (number only): ".rjust(60))

        if signin_choice.isdigit():
                signin_choice = int(signin_choice)
                if 1 <= signin_choice <= 3:
                    clear_console()
                    return signin_choice
                elif signin_choice == 3:
                    print("============================================================".center(100))
                    print(" ")
                    print(" ")
                    print(" ")
                    print("Goodbye!".center(100))
                    print(" ")
                    print(" ")
                    print(" ")
                    print("============================================================".center(100))
                    sys.exit()
                
        print("Invalid choice. Please enter a valid option (1-3).".center(100))

def signin(signin_choice):
     
     if signin_choice == 1:
          
          username = input("Enter username: ")
          password = input("Enter your password: ")

def signup(signin_choice):
        print("============================================================".center(100))
        print("|                                                          |".center(100))
        print("|                    CREATE AN ACCOUNT                     |".center(100))
        print("|                Please enter your details.                |".center(100))
        print("|                                                          |".center(100))
        print("============================================================".center(100))

        first_name = input("Enter your first name: ")
        last_name = input("Enter your last name: ")
        print("\n")
        batch = input("Enter your batch: ")
        gender = input("Enter your gender: ")
        degreeprogram = input("Enter your degree program: ")
        # member id = auto generated

        # insert authentication here

def successmessage():
     success= input("You have successfully created an account. Press any key to continue.")

