import DuvalCounty
import ClayCounty


# call main function
if __name__ == "__main__":
    active = True
    while active:
        print("Property Search Bot")
        print("Select a county to search")
        print("1. Duval County")
        print("2. Clay County")
        print("3. Exit")
        # get user input
        county = input("Enter a number: ")
        # check user input
        if county == "1":
            DuvalCounty.Menu()
        elif county == "2":
            ClayCounty.Menu()
        elif county == "3":
            active = False
            exit()
        else:
            print("Invalid input")

