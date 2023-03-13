import ClayCounty
import DuvalCounty
import time

# call main function
if __name__ == "__main__":
    try:
        ClayCounty.RunDaily()
    except:
        print("Clay County failed. Legal Columns may be completely blank for today.")
    try:
        DuvalCounty.RunToday()
    except:
        print("Duval County failed. Legal Columns may be completely blank for today.")

