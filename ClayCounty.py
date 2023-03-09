# This module was coded by Carick Brandt in 3/2023
# This module is used to get various document information from clay county's
# website: https://landmark.claycountygov.com/LandmarkWeb/search/index?theme=.blue&section=searchCriteriaDocuments&quickSearchSelection=
# Using the selenium module, we will be able to automate the process of getting the data we need.
# we are looking for document types in this list of strings: {CD, J, LN, LP, LPC, PRO}. This will not be ran on a regular
# basis, So It will ask the user for the date range the want to search for. We also only want the first 5000 records so
# make sure that dropdown is set to "Show first 5000 records", Submit that form and then download the csv file to the
# folder /Downloads/, Renaming it to "SearchResults.csv". Once that is done, we will open the csv file using pandas and
# keep the following columns: {Direct Name, Record Date, Doc Type, Legal}. we will then navigate to the Clay County
# Property Appraiser's website: https://qpublic.schneidercorp.com/Application.aspx?AppID=830&LayerID=15008&PageTypeID=2&PageID=6754
# and fill out the Search by legal information form with the Legal column from the csv file. We will then use beautiful
# soup to Scrape the Property Address, Owner Name, and Mailing Address. We will then add those columns to the csv file
# and save it as "{Doc_Type}_Parsed_{Start_Date}_{End_Date}.csv". We will then delete the SearchResults.csv file and
# exit this module.

# Importing the necessary modules
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import undetected_chromedriver as uc

global workingDir
workingDir = os.getcwd()

# List of Document Types we are looking for
doc_types = ["CD", "J", "LN", "LP", "LPC", "PRO"]

# This function will get the user input for the date range they want to search for
def get_date_range():
    print("Dates must be in the format MM/DD/YYYY. If the month or day is a single digit, you must add a 0 in front of it.")
    print("Example: 1/1/2021 = 01/01/2021")
    start_date = input("Enter the Start Date (MM/DD/YYYY): ")
    end_date = input("Enter the End Date (MM/DD/YYYY): ")

    if start_date > end_date:
        print("Start Date must be before End Date")
        return get_date_range()
    else:
        return start_date, end_date

# This function will get the user input for the document type they want to search for
def get_doc_type():
    # Print the list of Document Types
    print("Document Types: ", doc_types)
    doc_type = input("Enter the Document Type you want to search for: ")
    if doc_type in doc_types:
        return doc_type
    else:
        print("Invalid Document Type")
        return get_doc_type()

# This Function will initialize the selenium webdriver and return it
def init_driver():
    options = Options()
    # options.add_argument("--headless")
    # Set Downloads folder to the current directory + /Downloads/
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    download_dir = workingDir + "\\Downloads\\"
    options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
    })

    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    print(driver.execute_script("return navigator.userAgent;"))
    options.add_argument('--disable-blink-features=AutomationControlled')

    return driver

# This function will go to the Clay County Landmark Website and fill out the form with the user input
def fill_out_form(start_date, end_date, doc_type):

    # Delete any .xlsx files in the downloads folder
    for file in os.listdir(workingDir + "\\Downloads\\"):
        if file.endswith(".xlsx"):
            os.remove(workingDir + "\\Downloads\\" + file)

    driver = init_driver()
    # Go to the Clay County Landmark Website
    driver.get("https://landmark.clayclerk.com/LandmarkWeb")
    driver.find_element(By.CSS_SELECTOR, ".divInside:nth-child(2) .icon_home").click()
    driver.find_element(By.ID, "idAcceptYes").click()
    # Set the Document Type
    driver.implicitly_wait(30)
    doc_type_input = driver.find_element(By.ID, "documentType-DocumentType")
    doc_type_input.send_keys(doc_type)

    # Set the Start Date
    start_date_input = driver.find_element(By.ID, "beginDate-DocumentType")
    start_date_input.click()
    start_date_input.send_keys(Keys.CONTROL + "a")
    start_date_input.send_keys(Keys.DELETE)
    start_date_input.send_keys(start_date)

    # Set the End Date
    end_date_input = driver.find_element(By.ID, "endDate-DocumentType")
    end_date_input.click()
    end_date_input.send_keys(Keys.CONTROL + "a")
    end_date_input.send_keys(Keys.DELETE)
    end_date_input.send_keys(end_date)

    # Set the Number of Records to 5000
    num_records = Select(driver.find_element(By.ID, "numberOfRecords-DocumentType"))
    num_records.select_by_visible_text("Show first 5000 records")

    # Click the Submit Button
    submit_button = driver.find_element(By.ID, "submit-DocumentType")
    submit_button.click()
    time.sleep(45)

    # Click the Export Button
    export_button = driver.find_element(By.ID, "results-Export")
    export_button.click()

    # Wait for the file to download
    time.sleep(10)

    # rename the file that contains "_ExportResults_" in the name to "SearchResults.xlsx"
    for file in os.listdir(workingDir + "\\Downloads\\"):
        if "_ExportResults_" in file:
            os.rename(workingDir + "\\Downloads\\" + file, workingDir + "\\Downloads\\SearchResults.xlsx")

# This Function will parse the SearchResults.xlsx file and return a pandas dataframe Containing the {Doc Type,
# Record Date, Direct Name, Legal} columns
def parse_excel():
    # Read the SearchResults.xlsx file
    df = pd.read_excel(workingDir + "\\Downloads\\SearchResults.xlsx")

    # only keep {Doc Type, Record Date, Direct Name, Legal} Columns
    df = df[["Doc Type", "Record Date", "Legal"]]
    # Drop any legal descriptions that are null
    df.dropna(subset=["Legal"], inplace=True)
    # if the legal column contains "LOT:" then replace "LOT:" with ""
    df["Legal"] = df["Legal"].str.replace("LOT: ", "")
    df["Legal"] = df["Legal"].str.replace("LOT:", "")
    # if the legal column contains "SUB/CON" then replace "SUB/CON" with ""
    df["Legal"] = df["Legal"].str.replace("SUB: ", "")
    df["Legal"] = df["Legal"].str.replace("SUB:", "")
    df["Legal"] = df["Legal"].str.replace("CON: ", "")
    df["Legal"] = df["Legal"].str.replace("UNI: ", "Unit ")
    df["Legal"] = df["Legal"].str.replace("UNI:", "Unit ")
    df["Legal"] = df["Legal"].str.replace("BDG: ", "BLDG ")
    df["Legal"] = df["Legal"].str.replace("Addition NO ", "")
    # if the legal column contains "BLK: xx" where x is a number then replace "BLK: xx" with ""
    df["Legal"] = df["Legal"].str.replace("BLK: \d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("BLK: \s+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("BLK:\d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("BLK:\s+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("TPW: \d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("TPW:\d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("TPW:\s+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("TPW: \s+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("RGE: \d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("RGE:\d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("RGE: \s+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("RGE:\s+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("SEC: \d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("SEC:\d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("SEC: \s+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("SEC:\s+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("PHA: \d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("PHA:\d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("PHA: \s+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("PHA:\s+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("TWP: \d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("TWP:\d+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("TWP: \s+", "", regex=True)
    df["Legal"] = df["Legal"].str.replace("TWP:\s+", "", regex=True)

    # don't keep anything in legal that comes after a new line
    df["Legal"] = df["Legal"].str.split("\n").str[0]
    df.drop(df[df["Legal"].str.len() < 10].index, inplace=True)
    df.drop(df[~df["Legal"].str.contains("\d")].index, inplace=True)
    df.drop(df[df["Legal"].str.contains("\d{4}-\d+-\w{2}")].index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(df)
    # save the dataframe to a csv file
    # df.to_csv(workingDir + "\\SearchResults.csv", index=False)
    return df

# This function will take the dataframe and search https://qpublic.schneidercorp.com/Application.aspx?AppID=830&LayerID=15008&PageTypeID=2&PageID=6754
# using the legal columns in the Search by Legal Information Section
def search_by_legal(df):
    driver = uc.Chrome()
    driver.get("https://qpublic.schneidercorp.com/Application.aspx?AppID=830&LayerID=15008&PageTypeID=2&PageID=6754")
    driver.implicitly_wait(60)
    driver.find_element(By.LINK_TEXT, "Agree").click()

    PropertyAddress = []
    PropertyCity = []
    PropertyState = []
    PropertyZip = []
    Name = []
    MailingAddress = []
    MailingCity = []
    MailingState = []
    MailingZip = []
    # Loop through the dataframe
    for index, row in df.iterrows():
        # Open the website
        if index != 0:
            driver.get("https://qpublic.schneidercorp.com/Application.aspx?AppID=830&LayerID=15008&PageTypeID=2&PageID=6754")
        # Wait for the page to load
        driver.implicitly_wait(5)
        # Find the search by legal information section
        search_by_legal_info = driver.find_element(By.ID, "ctlBodyPane_ctl05_ctl01_txtName")
        search_by_legal_info.send_keys(row["Legal"])
        search_by_legal_info.send_keys(Keys.ENTER)
        driver.implicitly_wait(10)
        # if ctlBodyPane_ctl00_ctl01_gvwParcelResults is found then the search is too broad, append the PropertyAddress, PropertyCity, PropertyState, PropertyZip, Name, MailingAddress, MailingCity, MailingState, MailingZip with "N/A"
        if driver.find_elements(By.CSS_SELECTOR, ".module-content > .tabular-data-two-column tr:nth-child(2) span"):
            text = driver.find_element(By.CSS_SELECTOR,
                                   ".module-content > .tabular-data-two-column tr:nth-child(2) span").text
            PropertyAddress.append(text.split("\n")[0])
            print("Street: " + PropertyAddress[index])
            PropertyCity.append(text.split("\n")[1])
            # Take the number at the very end of PropertyCity and put it in PropertyZip
            PropertyZip.append(PropertyCity[index].split(" ")[-1])
            PropertyCity[index] = " ".join(PropertyCity[index].split(" ")[:-1])
            PropertyState.append("FL")
            print("City: " + PropertyCity[index])
            print("State: " + PropertyState[index])
            print("Zip: " + PropertyZip[index])

            text = driver.find_element(By.CSS_SELECTOR, ".three-column-blocks:nth-child(1)").text
            Name.append(text.split("\n")[0])
            print("Name: " + Name[index])
            MailingAddress.append(text.split("\n")[1])
            print("Mailing Address: " + MailingAddress[index])
            MailingCity.append(text.split("\n")[2])

            # Take the number at the very end of MailingCity and put it in MailingZip
            MailingZip.append(MailingCity[index].split(" ")[-1])
            MailingCity[index] = " ".join(MailingCity[index].split(" ")[:-1])

            # take the last word from MailingCity and put it in MailingState
            MailingState.append(MailingCity[index].split(" ")[-1])
            MailingCity[index] = " ".join(MailingCity[index].split(" ")[:-1])
            print("Mailing City: " + MailingCity[index])
            print("mailing State: " + MailingState[index])
            print("Mailing Zip: " + MailingZip[index])
        else:
            PropertyAddress.append("N/A")
            PropertyCity.append("N/A")
            PropertyState.append("N/A")
            PropertyZip.append("N/A")
            Name.append("N/A")
            MailingAddress.append("N/A")
            MailingCity.append("N/A")
            MailingState.append("N/A")
            MailingZip.append("N/A")
            print("No Result for row: " + str(index))
            continue
    df["Name"] = Name
    df["PropertyAddress"] = PropertyAddress
    df["PropertyCity"] = PropertyCity
    df["PropertyState"] = PropertyState
    df["PropertyZip"] = PropertyZip
    df["MailingAddress"] = MailingAddress
    df["MailingCity"] = MailingCity
    df["MailingState"] = MailingState
    df["MailingZip"] = MailingZip
    # Drop any rows that have "N/A" in the Name column
    df.drop(df[df["Name"] == "N/A"].index, inplace=True)
    # if Mailing address does not contain a number then drop the row
    df.drop(df[~df["MailingAddress"].str.contains("\d")].index, inplace=True)
    # Mailing Zip Must be 5 digits without any characters
    df.drop(df[~df["MailingZip"].str.contains("\d{5}")].index, inplace=True)
    # Drop any rows that have Mailing City Empty
    df.drop(df[df["MailingCity"] == ""].index, inplace=True)
    # Drop any rows that have Mailing State as anything but 2 Capital letters
    df.drop(df[~df["MailingState"].str.contains("[A-Z]{2}")].index, inplace=True)
    # Drop any rows with an empty column
    df.dropna(inplace=True)
    print(df)
    df.to_csv(workingDir + "\\SearchResults.csv", index=False)






# docType = get_doc_type()
# start_date, end_date = get_date_range()
# driver = init_driver()
fill_out_form(start_date="01/01/2023", end_date="03/01/2023", doc_type="CD, J, LN, LP, LPC, PRO")
df = parse_excel()
search_by_legal(df)


