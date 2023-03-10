# This module was coded by Carick brandt on 3/2023
# This module takes the dataframe from Duvalcounty.py for probates and cleans it up and searches for the names of the deceased on https://paopropertysearch.coj.net/Basic/Results.aspx

# Importing the necessary modules
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import time
import requests

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

PropertyUse = {
    "0000 Vacant Res < 20 Acres",
    "0041 Res Condo Vac",
    "0100 Single Family",
    "0200 Mobile Home",
    "0400 Residential Condo",
    "0700 Misc Residence",
    "0800 Multi-Family Units 2-9"
}

def CleanUp():
    # This function will find any rows that have a "Case Number" deleting any rows that do not have a case number,
    # and then it will save the csv file to be used in the next function

    # Open the CSV File in Downloads/SearchResults.csv if it does not exist then the function will return a message
    if os.path.exists(os.getcwd() + "/Downloads/SearchResults.csv"):
        DataFrame = pd.read_csv(os.getcwd() + "/Downloads/SearchResults.csv")
    else:
        return print("No File to Clean")

    # Create the RE# column
    DataFrame["RE#"] = ""

    # Copy the DirectName Column to a list and then replace any instance of "DECEASED" with "" and then
    # copy the list back to the DirectName Column
    directName = DataFrame["DirectName"].tolist()
    for i in range(len(directName)):
        directName[i] = directName[i].replace("DECEASED", "")
        directName[i] = " ".join(directName[i].split())
    DataFrame["DirectName"] = directName
    # pd.set_option("display.max_rows", None, "display.max_columns", None)
    # print(df)

    # Check if DocLegalDescription is empty if it is then add NO PIN to the RE# column
    # if it is not empty then extract the RE# from the DocLegalDescription column
    # and then add it to the RE# column
    DataFrame["RE#"] = DataFrame["DocLegalDescription"].str.extract(
                r"(\d{4}-\d{4}|\d{6}-\d{4}|\d{4}-\d{4}|\d{4} \d{4})")


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
    print(DataFrame)

    # Save the csv file to the Downloads/Probate folder good for comparing the data
    # savePath = os.getcwd() + "/Downloads/" + docType + ".csv"
    # DataFrame.to_csv(savePath, index=False)
    # DataFrame.to_csv(os.getcwd() + "/Downloads/Probate.csv", index=False)
    return DataFrame

def PropertySearch(dataframe: pd.DataFrame):
    # create a list of RE# from the Dataframe
    REList = dataframe["RE#"].tolist()
    REListCheckLater = []
    # create a list of Full Name from the Dataframe
    # NameList = dataframe["Full Name"].tolist()
    NameList = []
    # create a list of Doc Type from the Dataframe
    DocTypeList = dataframe["Doc Type"].tolist()
    recordDate = dataframe["RecordDate"].tolist()
    indirectName = dataframe["IndirectName"].tolist()
    directName = dataframe["Full Name"].tolist()
    directNameCheckLater = []
    docTypeCheckLater = []
    recordDateCheckLater = []
    indirectNameCheckLater = []
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

    # loop through the RE# list and search for the RE# on https://paopropertysearch.coj.net/Basic/Results.aspx
    URLList = []
    for i in range(len(REList)):
        REList[i] = REList[i].replace("-", "")
        REList[i] = REList[i].replace(" ", "")
        URLList.append("https://paopropertysearch.coj.net/Basic/Results.aspx?ParcelNumber=" + REList[i])
        if URLList[i] == "https://paopropertysearch.coj.net/Basic/Results.aspx?ParcelNumber=00000000000":
        # open selenium and go to https://paopropertysearch.coj.net/Basic/Search.aspx
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get("https://paopropertysearch.coj.net/Basic/Search.aspx")
            # wait for the page to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ctl00_cphBody_tbName")))
            driver.find_element(By.ID, "ctl00_cphBody_tbName").send_keys(directName[i])
            driver.find_element(By.ID, "ctl00_cphBody_tbName").send_keys(Keys.ENTER)
            time.sleep(3)
            if driver.find_elements(By.ID, "ctl00_cphBody_divNoResults1"):
                print("No Results Found")
                REList[i] = "N/A"
                driver.quit()
                continue
            elif driver.find_elements(By.ID, "ctl00_cphBody_gridResults"):
                table = driver.find_element(By.ID, "ctl00_cphBody_gridResults")
                for tableRow in table.find_elements(By.CSS_SELECTOR, "tr"):
                    for tableColumn in tableRow.find_elements(By.CSS_SELECTOR, "td"):
                        if directName[i] in tableColumn.text:
                            checkLater = tableRow.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                            print(checkLater)
                            REListCheckLater.append(checkLater)
                            docTypeCheckLater.append(DocTypeList[i])
                            recordDateCheckLater.append(recordDate[i])
                            indirectNameCheckLater.append(indirectName[i])
                            # set all of those to N/A for now
                            REList[i] = "N/A"

                driver.quit()

    # Delete any list index that has N/A in the columns RE#, Full Name, Doc Type, RecordDate, IndirectName
    for i in range(len(REList) - 1, -1, -1):
        if REList[i] == "N/A":
            del REList[i]
            del DocTypeList[i]
            del recordDate[i]
            del indirectName[i]
            del URLList[i]

    URLList.extend(REListCheckLater)
    DocTypeList.extend(docTypeCheckLater)
    recordDate.extend(recordDateCheckLater)
    indirectName.extend(indirectNameCheckLater)
    print(len(URLList))
    for i in range(len(URLList)):
        r = requests.get(URLList[i])
        soup = BeautifulSoup(r.content, "html.parser")
        # (soup.prettify)
        try:
            NameList.append(soup.find(id="ctl00_cphBody_repeaterOwnerInformation_ctl00_lblOwnerName").text)
        except:
            NameList.append("Not Found")

        # find id="ctl00_cphBody_repeaterOwnerInformation_ctl00_lblMailingAddressLine1"
        # and save it to MailingAddressStreet
        # if the id is not found then append "Not Found" to the list
        try:
            MailingAddress1.append(
                soup.find(id="ctl00_cphBody_repeaterOwnerInformation_ctl00_lblMailingAddressLine1").text)
            for prefix in RoadPrefixList:
                if prefix in MailingAddress1[i]:
                    MailingAddress1[i] = MailingAddress1[i].split(prefix)[0] + prefix
        except:
            MailingAddress1.append("Not Found")
        try:
            MailingAddress2.append(
                soup.find(id="ctl00_cphBody_repeaterOwnerInformation_ctl00_lblMailingAddressLine3").text)
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
    CompletedData = pd.DataFrame(
        list(zip(DocTypeList, recordDate, indirectName, FirstName, LastName, StreetAddress1, StreetCity, StreetState,
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
    NewCSVFile = os.getcwd() + "\\Parsed\\" + DocType +".csv"
    EstateCSVFile = os.getcwd() + "\\Parsed\\" + DocType + "-" + "Estate.csv"

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

