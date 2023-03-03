# This bot is designed to run daily or retroactively and pull data from county websites in the state of florida
# and parse it and search for properties that are eligible and saves them to a csv file

import DuvalCounty
import JudgementDuvalCounty


def automated():
    pass
# main function
def main():
    # create a small cmd menu for the user to select automated or manual
    print("Welcome to the Florida Property Bot")
    print("Please select an option below")
    print("1. Automated")
    print("2. Manual")
    print("3. Exit")
    # get user input
    user_input = input("Please enter a number: ")
    # check user input
    if user_input == "1":
        # run automated function
        pass
    elif user_input == "2":
        # run manual function
        pass
    elif user_input == "3":
        # exit the program
        exit()
    else:
        pass



# call main function
if __name__ == "__main__":
    main()

