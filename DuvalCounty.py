# This Module is for duval county and will be run daily

import os
import pandas as pd
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import JudgementDuvalCounty


# chrome settings
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-gpu")

# get today and yesterday's date formatted into 1/1/2021
Today = date.today()
Yesterday = Today - timedelta(days=1)
# Today = Today.strftime("%m/%d/%Y")

# Start Date and End Date for search
StartDate = '1/13/2021'
EndDate = '1/13/2021'


# Create Dictionary for Doc Types
docTypes = {
    "probate": "PROBATE (PROB)",
    "lis pendens": "LIS PENDENS (LP)",
    "tax deed": "TAX DEED (TXD)",
    "lien": "LIEN (LN)",
    "judgment": "JUDGMENT (JDG)"
}

# List of Property Uses that matter
PropertyUse = {
    "0000 Vacant Res < 20 Acres",
    "0041 Res Condo Vac",
    "0100 Single Family",
    "0200 Mobile Home",
    "0400 Residential Condo",
    "0700 Misc Residence",
    "0800 Multi-Family Units 2-9"
}

# List of Directions prefixes
Directions = {
    "N",
    "S",
    "E",
    "W",
    "NE",
    "NW",
    "SE",
    "SW"
}

# Road prefixes
RoadPrefixList = {
    "Ave",
    "Blvd",
    "Cir",
    "Ct",
    "Dr",
    "Hwy",
    "Ln",
    "Pkwy",
    "Pl",
    "Rd",
    "St",
    "Ter",
    "Way",
    "EXPY",
    "AVE",
    "BLVD",
    "CIR",
    "CT",
    "DR",
    "HWY",
    "LN",
    "PKWY",
    "PL",
    "RD",
    "ST",
    "WAY",
    "ROAD",
    "LANE",
    "CIRCLE",
    "COURT",
    "DRIVE",
    "EXPRESSWAY",
    "HIGHWAY",
    "PARKWAY",
    "PLACE",
    "STREET",
    "TERRACE",
    "WAY"
}

Cities = {
    "Jacksonville",
    "Jacksonville Beach",
    "Atlantic Beach",
    "Neptune Beach",
    "Baldwin",
    "JACKSONVILLE",
    "JACKSONVILLE BEACH",
    "ATLANTIC BEACH",
    "NEPTUNE BEACH",
    "BALDWIN"
}

# Input the Start Date and End Date for the search if None then it will default to yesterday and today
def SearchDates(startDate=Yesterday, endDate=Today):
    if startDate == Yesterday:
        startDate = Yesterday.strftime("%m/%d/%Y")
    else:
        startDate = datetime.strptime(startDate, "%m/%d/%Y")
        startDate = startDate.strftime("%m/%d/%Y")
    if endDate == Today:
        endDate = Today.strftime("%m/%d/%Y")
    else:
        endDate = datetime.strptime(endDate, "%m/%d/%Y")
        endDate = endDate.strftime("%m/%d/%Y")
    return startDate, endDate

def Automated():
    date1 = Yesterday.strftime("%m/%d/%Y")
    date2 = Today.strftime("%m/%d/%Y")
    return date1, date2


def UnAutomated():
    input1 = input("Enter Start Date: ")
    if input1 == "":
        StartDate, EndDate = SearchDates()
    else:
        input2 = input("Enter End Date: ")
        StartDate, EndDate = SearchDates(input1, input2)
    return StartDate, EndDate


def onCoreScrape(doctype):
    # This function will scrape the Website: {https://oncore.duvalclerk.com/search/SearchTypeDocType}
    # for Doc Type: {"PROBATE", "LIS PENDENS", "TAX DEED", "LIENS", "JUDGEMENT"} From either the
    # Date Range: {"Yesterday"} or {From Record Date: Argument} to {To Record Date: Argument}

    # if Downloads/SearchResults.csv exists then delete it
    if os.path.exists(os.getcwd() + "/Downloads/SearchResults.csv"):
        os.remove(os.getcwd() + "/Downloads/SearchResults.csv")
    else:
        pass

    # URL for Duval County
    url = "https://oncore.duvalclerk.com/search/SearchTypeDocType"

    download_path =  os.getcwd() + "\\Downloads\\"
    prefs = {"download.default_directory": download_path,
             "download.prompt_for_download": False,
             "download.directory_upgrade": True,
             "safebrowsing_for_trusted_sources_enabled": False,
             "safebrowsing.enabled": False
             }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(60)
    driver.find_element(By.ID, "btnButton").click()
    driver.implicitly_wait(60)
    driver.find_element(By.ID, "DocTypesDisplay-input").click()
    driver.find_element(By.ID, "DocTypesDisplay-input").send_keys(Keys.CONTROL + "a")
    driver.find_element(By.ID, "DocTypesDisplay-input").send_keys(Keys.BACKSPACE)
    driver.find_element(By.ID, "DocTypesDisplay-input").send_keys(docTypes[doctype])
    driver.find_element(By.ID, "RecordDateFrom").click()
    driver.find_element(By.ID, "RecordDateFrom").send_keys(Keys.CONTROL + "a")
    driver.find_element(By.ID, "RecordDateFrom").send_keys(Keys.BACKSPACE)
    driver.find_element(By.ID, "RecordDateFrom").send_keys(StartDate)
    driver.find_element(By.ID, "RecordDateTo").click()
    driver.find_element(By.ID, "RecordDateTo").send_keys(Keys.CONTROL + "a")
    driver.find_element(By.ID, "RecordDateTo").send_keys(Keys.BACKSPACE)
    driver.find_element(By.ID, "RecordDateTo").send_keys(EndDate)
    time.sleep(3)
    driver.find_element(By.ID, "btnSearch").click()
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "btnCsvButton"))).click()
    time.sleep(5)
    driver.quit()
    return print("Downloaded " + doctype + " for " + StartDate + " to " + EndDate)


def CleanUp():
    # This function will find any rows that have a "Case Number" deleting any rows that do not have a case number,
    # and then it will save the csv file to be used in the next function

    # Open the CSV File in Downloads/Probate
    DataFrame = pd.read_csv("Downloads/SearchResults.csv")
    # drop any rows that contain a NaN value in the DocLegalDescription column
    DataFrame.dropna(subset=["DocLegalDescription"], inplace=True)
    # Drop any rows that do not contain "PIN" in the DocLegalDescription column
    DataFrame = DataFrame[DataFrame["DocLegalDescription"].str.contains("PIN")]
    DataFrame.reset_index(drop=True, inplace=True)

    # Copy the DirectName Column to a list and then replace any instance of "DECEASED" with "" and then
    # copy the list back to the DirectName Column
    directName = DataFrame["DirectName"].tolist()
    for i in range(len(directName)):
        directName[i] = directName[i].replace("DECEASED", "")
        directName[i] = " ".join(directName[i].split())
    DataFrame["DirectName"] = directName
    # pd.set_option("display.max_rows", None, "display.max_columns", None)
    # print(df)

    # use regex to find the PIN which looks like this: 1234-5678 from the DocLegalDescription Column
    # it could also be in the formats of xxxxxx-xxxx, xxxx-xxxx, xxxx xxxx
    # and then copy the PIN to a new column called "RE#"
    DataFrame["RE#"] = DataFrame["DocLegalDescription"].str.extract(r"(\d{4}-\d{4}|\d{6}-\d{4}|\d{4}-\d{4}|\d{4} \d{4})")

    # if the row of RE# does not have 11 characters place 0's in front of the RE# till it has 11 characters
    RENumber = DataFrame["RE#"].tolist()
    for i in range(len(RENumber)):
        # if the RE# is Nan then replace it with 0
        if pd.isna(RENumber[i]):
            RENumber[i] = "0"
        if len(RENumber[i]) < 11:
            RENumber[i] = RENumber[i].zfill(11)
        # if the RE# is Nan then drop the row
    DataFrame["RE#"] = RENumber

    # only keep the columns DirectName, and PIN
    # rename DirectName to Full Name
    DataFrame.rename(columns={"DirectName": "Full Name", "DocTypeDescription": "Doc Type"}, inplace=True)
    DataFrame = DataFrame[["Doc Type", "RE#", "Full Name", "RecordDate", "IndirectName"]]
    # print(df)

    # Save the csv file to the Downloads/Probate folder good for comparing the data
    # savePath = os.getcwd() + "/Downloads/" + docType + ".csv"
    # DataFrame.to_csv(savePath, index=False)
    return DataFrame


def PropertySearch(dataframe):
    # This Function will Search the Property appraiser website using the RE# from the Dataframe and then check if
    # "Property Use" is in the Property Use list. If it is then it will record the Mailing Address, Mailing City,
    # Mailing Zip, Primary Street Address, Street City, Street Zip, Property Use, and Full Name to a new Dataframe

    # print(df)

    # create a list of RE# from the Dataframe
    REList = dataframe["RE#"].tolist()
    # create a list of Full Name from the Dataframe
    # NameList = dataframe["Full Name"].tolist()
    NameList = []
    # create a list of Doc Type from the Dataframe
    DocTypeList = dataframe["Doc Type"].tolist()
    recordDate = dataframe["RecordDate"].tolist()
    indirectName = dataframe["IndirectName"].tolist()
    FirstName = []
    LastName = []
    MiddleName = []
    MailingAddress1 = []
    MailingAddress2 = []
    MailingCity = []
    MailingZip = []
    MailingState = []
    StreetAddress1 = []
    StreetAddress2 = []
    StreetCity = []
    StreetZip = []
    StreetState = []
    PropertyUsage = []
    DocType = DocTypeList[0]

    # iterate through the REList and create a list of URLS that are formatted as such:
    # https://paopropertysearch.coj.net/Basic/Detail.aspx?RE=xxxxxxxxxxx where the xxxxxxxxxx is the RE# without dashes
    URLList = []
    for i in range(len(REList)):
        URLList.append("https://paopropertysearch.coj.net/Basic/Detail.aspx?RE=" + REList[i].replace("-", ""))
    # print(URLList)

    # Iterate through the URLList and open each URL using requests and then use BeautifulSoup to parse the HTML
    # and print the Mailing Address, Mailing City, Mailing Zip, Primary Street Address, Street City, Street Zip,
    # Property Use, and Full Name to a new Dataframe
    for i in range(len(URLList)):
        r = requests.get(URLList[i])
        soup = BeautifulSoup(r.content, "html.parser")
        # print(soup.prettify())

        #
        try:
            NameList.append(soup.find(id="ctl00_cphBody_repeaterOwnerInformation_ctl00_lblOwnerName").text)
        except:
            NameList.append("Not Found")

        # find id="ctl00_cphBody_repeaterOwnerInformation_ctl00_lblMailingAddressLine1"
        # and save it to MailingAddressStreet
        # if the id is not found then append "Not Found" to the list
        try:
            MailingAddress1.append(soup.find(id="ctl00_cphBody_repeaterOwnerInformation_ctl00_lblMailingAddressLine1").text)
            for prefix in RoadPrefixList:
                if prefix in MailingAddress1[i]:
                    MailingAddress1[i] = MailingAddress1[i].split(prefix)[0] + prefix
        except:
            MailingAddress1.append("Not Found")
        try:
            MailingAddress2.append(soup.find(id="ctl00_cphBody_repeaterOwnerInformation_ctl00_lblMailingAddressLine3").text)
        except:
            MailingAddress2.append("Not Found")

        # Separate the MailingAddress2 into city state zip if the MailingAddress2 is not "Not Found"
        if MailingAddress2[i] != "Not Found":
            # Separate the MailingAddress2 into city state zip
            MailingCity.append(MailingAddress2[i].split(",")[0])
            # remove the comma from the city
            MailingCity[i] = MailingCity[i].replace(",", "")
            MailingState.append(MailingAddress2[i].split(",")[1].split(" ")[1])
            MailingZip.append(MailingAddress2[i].split(",")[1].split(" ")[2])
        # else drop rows that have "Not Found" in the MailingAddress2
        else:
            MailingCity.append("Not Found")
            MailingState.append("Not Found")
            MailingZip.append("Not Found")

        # find id="ctl00_cphBody_lblPrimarySiteAddressLine1" and save it to StreetAddressStreet
        try:
            StreetAddress1.append(soup.find(id="ctl00_cphBody_lblPrimarySiteAddressLine1").text)
            # if the text contains anything from roadPrefixList have the string end at the end of the prefix
            for prefix in RoadPrefixList:
                if prefix in StreetAddress1[i]:
                    StreetAddress1[i] = StreetAddress1[i].split(prefix)[0] + prefix
        except:
            StreetAddress1.append("Not Found")
        try:
            StreetAddress2.append(soup.find(id="ctl00_cphBody_lblPrimarySiteAddressLine2").text)
        except:
            StreetAddress2.append("Not Found")

        # Separate StreetAddress2 by white space if StreetAddress2 is not "Not Found"
        # Sometimes the Address contains a city that's two words we need to check if the length of the list is 4
        # if it is then we need to combine the first two words in the list to get the city
        # if it is not then we can just use the first word in the list to get the city
        if StreetAddress2[i] != "Not Found":
            if len(StreetAddress2[i].split(" ")) == 4:
                StreetCity.append(StreetAddress2[i].split(" ")[0] + " " + StreetAddress2[i].split(" ")[1])
                StreetState.append(StreetAddress2[i].split(" ")[2])
                StreetZip.append(StreetAddress2[i].split(" ")[3])
            else:
                StreetCity.append(StreetAddress2[i].split(" ")[0])
                StreetState.append(StreetAddress2[i].split(" ")[1])
                StreetZip.append(StreetAddress2[i].split(" ")[2])

        # try to find ctl00_cphBody_lblPropertyUse and check if it matches any of the property uses in the list
        # if it does then append it to the PropertyUsage list
        # if it does not then append "Not Found" to the PropertyUsage list
        try:
            if soup.find(id="ctl00_cphBody_lblPropertyUse").text in PropertyUse:
                PropertyUsage.append(soup.find(id="ctl00_cphBody_lblPropertyUse").text)
            else:
                PropertyUsage.append("Not Found")
        except:
            PropertyUsage.append("Not Found")

        # Full Name should be formatted like LastName FirstName MiddleName so split the Full Name by white space
        # and then save the LastName, FirstName, and MiddleName to their own lists. Somtimes there is no Middle name
        # so if there is no MiddleName then just save "" to the MiddleName list
        LastName.append(NameList[i].split(" ")[0])
        FirstName.append(NameList[i].split(" ")[1])
        if len(NameList[i].split(" ")) == 3:
            MiddleName.append(NameList[i].split(" ")[2])
        else:
            MiddleName.append("")

    # Create a new Dataframe with the lists in this order: Doc Type, First Name, Last Name, Street Address, Street City,
    # Street State, Street Zip, Mailing Address, Mailing City, Mailing State, Mailing Zip
    CompletedData = pd.DataFrame(list(zip(DocTypeList, recordDate, indirectName, FirstName, LastName, StreetAddress1, StreetCity, StreetState,
                                          StreetZip, MailingAddress1, MailingCity, MailingState, MailingZip,
                                          PropertyUsage)), columns=["Doc Type", "Record Date", "Indirect Name", "First Name", "Last Name",
                                                                    "Street Address", "Street City", "Street State",
                                                                    "Street Zip", "Mailing Address", "Mailing City",
                                                                    "Mailing State", "Mailing Zip", "Property Usage"])
    # Drop all rows that have "Not Found" in any column
    CompletedData = CompletedData[CompletedData["Street Address"] != "Not Found"]
    CompletedData = CompletedData[CompletedData["Street City"] != "Not Found"]
    CompletedData = CompletedData[CompletedData["Street State"] != "Not Found"]
    CompletedData = CompletedData[CompletedData["Street Zip"] != "Not Found"]
    CompletedData = CompletedData[CompletedData["Mailing Address"] != "Not Found"]
    CompletedData = CompletedData[CompletedData["Mailing City"] != "Not Found"]
    CompletedData = CompletedData[CompletedData["Mailing State"] != "Not Found"]
    CompletedData = CompletedData[CompletedData["Mailing Zip"] != "Not Found"]
    CompletedData = CompletedData[CompletedData["Property Usage"] != "Not Found"]
    # print(CompletedData)

    # Limit the number of characters in the Mailing Zip and Street Zip columns to 5
    CompletedData["Mailing Zip"] = CompletedData["Mailing Zip"].str[:5]
    CompletedData["Street Zip"] = CompletedData["Street Zip"].str[:5]

    # Date1 is a string of yesterday in the format of "Jan012020", date2 is a string of today in the format of "Jan022020"
    # and then the two strings are combined to create a string of "Jan012020-Jan022020"
    SaveDate1 = datetime.strptime(StartDate, "%m/%d/%Y").strftime("%b%d%Y")
    SaveDate2 = datetime.strptime(EndDate, "%m/%d/%Y").strftime("%b%d%Y")
    NewCSVFile = "Parsed/" + DocType + "-" + SaveDate1 + "-" + SaveDate2 + ".csv"
    EstateCSVFile = "Parsed/" + DocType + "-" + SaveDate1 + "-" + SaveDate2 + "Estate.csv"

    # IF "IndirectName": "ESTATE" in completedData. Create a new Dataframe to store the rows that have "ESTATE" in the IndirectName column
    # Then drop the rows that have "ESTATE" in the IndirectName column from the CompletedData Dataframe
    # Then save the new Dataframe to a csv file in the Parsed/Probate folder
    # Then save the CompletedData Dataframe to a csv file in the Parsed/Probate folder
    # Then delete the SearchResults.csv file
    if "ESTATE" in CompletedData["Indirect Name"].values:
        EstateData = CompletedData[CompletedData["Indirect Name"] == "ESTATE"]
        # rename the Indirect Name column to "Estate?"
        EstateData = EstateData.rename(columns={"Indirect Name": "Estate?"})
        CompletedData = CompletedData[CompletedData["Indirect Name"] != "ESTATE"]
        print(EstateData)
        print("Saving CSV to: " + EstateCSVFile)
        EstateData.to_csv(EstateCSVFile, index=False)
        if not CompletedData.empty:
            print("Saving CSV to: " + NewCSVFile)
            # Drop the Indirect Name column from the CompletedData Dataframe
            CompletedData = CompletedData.drop(columns=["Indirect Name"])
            CompletedData.to_csv(NewCSVFile, index=False)
        os.remove("Downloads/SearchResults.csv")
    else:
        CompletedData = CompletedData.drop(columns=["Indirect Name"])
        print(CompletedData)
        print("Saving CSV to: " + NewCSVFile)
        CompletedData.to_csv(NewCSVFile, index=False)
        os.remove("Downloads/SearchResults.csv")


# StartDate, EndDate = Automated()
StartDate, EndDate = UnAutomated()
onCoreScrape("probate")
df = CleanUp()
PropertySearch(df)
onCoreScrape("lien")
df = CleanUp()
PropertySearch(df)
onCoreScrape("tax deed")
df = CleanUp()
PropertySearch(df)
# StartDate, EndDate = UnAutomated()
onCoreScrape("lis pendens")
df = CleanUp()
PropertySearch(df)
StartDate, EndDate = UnAutomated()
onCoreScrape("judgment")
df = JudgementDuvalCounty.CleanJudgement()
JudgementDuvalCounty.PropertySearch()

