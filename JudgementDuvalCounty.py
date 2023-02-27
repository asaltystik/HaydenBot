# This Module was Created by: Carick Brandt on 2/27/2023
# It Cleans up SearchResults.csv for judgement data and then searches the property appraiser site for the relevant data
import os
import time
import datetime

import dateutil.utils
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

PropertyUse = {
    "0000 Vacant Res < 20 Acres",
    "0041 Res Condo Vac",
    "0100 Single Family",
    "0200 Mobile Home",
    "0400 Residential Condo",
    "0700 Misc Residence",
    "0800 Multi-Family Units 2-9"
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


def PropertySearch():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=chrome_options)

    # for each row in the JudgementAddresses.csv file search the property appraiser site for the relevant data
    df = pd.read_csv(os.getcwd() + "/Downloads/JudgementAddresses.csv")
    Pins = pd.read_csv(os.getcwd() + "/Downloads/JudgementPINS.csv")

    # create a list of Full Name from the Dataframe
    # NameList = dataframe["Full Name"].tolist()
    NameList = []
    # create a list of Doc Type from the Dataframe
    DocTypeList = df["Doc Type"].tolist()
    recordDate = df["RecordDate"].tolist()
    DirectName = df["DirectName"].tolist()
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
    URLList = []

    for index, row in df.iterrows():
        driver.get("https://paopropertysearch.coj.net/Basic/Search.aspx")
        # driver.find_element(By.ID, "ctl00_cphBody_tbName").click()
        # driver.find_element(By.ID, "ctl00_cphBody_tbName").send_keys(row["DirectName"])
        driver.find_element(By.ID, "ctl00_cphBody_tbStreetNumber").click()
        driver.find_element(By.ID, "ctl00_cphBody_tbStreetNumber").send_keys(row["Street Number"])
        driver.find_element(By.ID, "ctl00_cphBody_tbStreetName").click()
        driver.find_element(By.ID, "ctl00_cphBody_tbStreetName").send_keys(row["Street Name"])
        driver.find_element(By.ID, "ctl00_cphBody_tbStreetName").send_keys(Keys.ENTER)
        driver.implicitly_wait(60)
        # Click the First Link in the table
        driver.find_element(By.CSS_SELECTOR, "td:nth-child(1)").click()
        URLList.append(driver.current_url)

    # Grab the PINS from the PIN dataframe
    PINList = Pins["PIN"].tolist()
    # add https://paopropertysearch.coj.net/Basic/Detail.aspx?RE= to the beginning of each PIN
    for i in range(len(PINList)):
        # remove the - from the PIN
        PINList[i] = PINList[i].replace("-", "")
        URLList.append("https://paopropertysearch.coj.net/Basic/Detail.aspx?RE=" + PINList[i])

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

    CompletedData = pd.DataFrame(list(zip(DocTypeList, recordDate, DirectName, StreetAddress1, StreetCity, StreetState,
                            StreetZip, MailingAddress1, MailingCity, MailingState, MailingZip, PropertyUsage)),
                            columns=["DocType", "Record Date", "Direct Name", "Street Address 1", "Street City",
                            "Street State", "Street Zip", "Mailing Address 1", "Mailing City",
                            "Mailing State", "Mailing Zip", "Property Usage"])
    # Drop all rows that have "Not Found" in the any column
    CompletedData.drop(CompletedData[CompletedData["Street Address 1"] == "Not Found"].index, inplace=True)
    CompletedData.drop(CompletedData[CompletedData["Street City"] == "Not Found"].index, inplace=True)
    CompletedData.drop(CompletedData[CompletedData["Street State"] == "Not Found"].index, inplace=True)
    CompletedData.drop(CompletedData[CompletedData["Street Zip"] == "Not Found"].index, inplace=True)
    CompletedData.drop(CompletedData[CompletedData["Mailing Address 1"] == "Not Found"].index, inplace=True)
    CompletedData.drop(CompletedData[CompletedData["Mailing City"] == "Not Found"].index, inplace=True)
    CompletedData.drop(CompletedData[CompletedData["Mailing State"] == "Not Found"].index, inplace=True)
    CompletedData.drop(CompletedData[CompletedData["Mailing Zip"] == "Not Found"].index, inplace=True)
    CompletedData.drop(CompletedData[CompletedData["Property Usage"] == "Not Found"].index, inplace=True)

    # Both Zip codes should only be 5 digits long
    CompletedData["Street Zip"] = CompletedData["Street Zip"].str[:5]
    CompletedData["Mailing Zip"] = CompletedData["Mailing Zip"].str[:5]

    # Get todays date and add it to the file name
    today = datetime.date.today()
    # make today a string
    today = str(today)
    FileName = os.getcwd() + "/Parsed/JudgementParsed-" + today + ".csv"
    CompletedData.to_csv(FileName, index=False)

def CleanJudgement():
    df = pd.read_csv(os.getcwd() + "/Downloads/SearchResults.csv")

    df.dropna(subset=["DocLegalDescription"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # if the DirectName Column contains "AS MANAGER" then replace is with " "
    df["DirectName"] = df["DirectName"].str.replace("AS MANAGER", "")

    # if the DirectName Column Contains "TRUST" at the end of the string then replace it with " "
    df["DirectName"] = df["DirectName"].str.replace("TRUST$", "", regex=True)

    # Copy any rows that have "PHYSICAL STREET ADDRESS" in the "DocLegalDescription" column to a new column called
    # "Street Address"
    df["Street Address"] = df["DocLegalDescription"].where(df["DocLegalDescription"].str.contains("PHYSICAL STREET ADDRESS"))
    df["Street Address"] = df["Street Address"].str.split("PHYSICAL STREET ADDRESS").str[1]

    # Copy any rows that have a string that looks like "PIN xxxxxx-xxxx" in the "DocLegalDescription" column to a new column
    # called "PIN"
    df["PIN"] = df["DocLegalDescription"].where(df["DocLegalDescription"].str.contains("PIN \d{6}-\d{4}"))
    df["PIN"] = df["PIN"].str.extract(r'(\\d{4}-\d{4}|\d{6}-\d{4}|\d{4}-\d{4}|\d{4} \d{4})')

    # Only Keep the DirectName, DocTypeDescription, RecordDate, Street Address, and PIN columns
    df = df[["DirectName", "DocTypeDescription", "RecordDate", "Street Address", "PIN"]]
    pinDF = df[["DirectName", "DocTypeDescription", "RecordDate", "PIN"]]
    df = df[["DirectName", "DocTypeDescription", "RecordDate", "Street Address"]]
    # Rename DocTypeDescription to "Doc Type"
    df.rename(columns={"DocTypeDescription": "Doc Type"}, inplace=True)
    # Drop any empty rows in the Street Address column of df
    df.dropna(subset=["Street Address"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    # Drop any empty rows in the PIN column of pinDF
    pinDF.dropna(subset=["PIN"], inplace=True)
    pinDF.reset_index(drop=True, inplace=True)

    # Take the First Number and First Word in the Street Address column of df and put them in their own columns
    df["Street Number"] = df["Street Address"].str.extract(r'(\d+)')
    # Remove the Street Number from the Street Address column
    df["Street Address"] = df["Street Address"].str.replace(r'\d+', '', regex=True)
    # Take the First Word in the Street Address column of df and put it in its own column
    df["Street Name"] = df["Street Address"].str.extract(r'(\w+)')
    # Remove the Street Name from the Street Address column
    # df["Street Address"] = df["Street Address"].str.replace(r'\w+', '', regex=True)
    # drop any row in the street address column that contains any Direction input
    df.drop(df[df["Street Name"].str.contains(
        "North|South|East|West|N|S|E|W|NE|NW|SE|SW")].index, inplace=True)
    # Street name must be longer then 2 characters
    df.drop(df[df["Street Name"].str.len() < 3].index, inplace=True)
    df.reset_index(drop=True, inplace=True)

    #get todays date


    df.to_csv(os.getcwd() + "/Downloads/JudgementAddresses.csv", index=False)
    pinDF.to_csv(os.getcwd() + "/Downloads/JudgementPINS.csv", index=False)



# Old code
# def CleanupJudgement():
#
#     judgementData = pd.read_csv(os.getcwd() + "/Downloads/SearchResults.csv")
#
#     Drop all rows that have NaN in the "DocLegalDescription" column
    # judgementData.dropna(subset=["DocLegalDescription"], inplace=True)
    # judgementData.reset_index(drop=True, inplace=True)
    #
    # Copy any Rows that have "PhysicalStreetAddress" in the "DocLegalDescription" column to a new column called "StreetAddress"
    # judgementData["StreetAddress"] = judgementData["DocLegalDescription"].where(judgementData["DocLegalDescription"].str.contains("PHYSICAL STREET ADDRESS"))
    # Only keep what comes after "PhysicalStreetAddress" in the "StreetAddress" column
    # judgementData["StreetAddress"] = judgementData["StreetAddress"].str.split("PHYSICAL STREET ADDRESS").str[1]
    #
    # Copy the first Set of numbers that look like 445 or 1810 or 10204 in the "StreetAddress" column to a new column called "StreetNumber"
    # judgementData["StreetNumber"] = judgementData["StreetAddress"].str.extract(r'(\b\d{3,5}\b)')
    # Drop just the first set of numbers
    # judgementData["StreetAddress"] = judgementData["StreetAddress"].str.replace(r'(\b\d{3,5}\b)', "", 1, regex=True)
    #
    # Using the global list "RoadPrefixList", Copy the first instance of a road prefix in the "StreetAddress" column to a new column called "StreetPrefix"
    # judgementData["StreetPrefix"] = judgementData["StreetAddress"].str.extract(r'(\b' + '|'.join(RoadPrefixList) + r'\b)')
    # Drop just the first instance of a road prefix
    # judgementData["StreetAddress"] = judgementData["StreetAddress"].str.replace(r'(\b' + '|'.join(RoadPrefixList) + r'\b)', "", 1, regex=True)
    #
    # if there is a number that looks like "#402" in the street address column, copy that number to a new column called
    # Unit"
    # and then drop the number from the "StreetAddress" column
    # judgementData["Unit"] = judgementData["StreetAddress"].str.extract(r'(\#\d{1,4})')
    # judgementData["StreetAddress"] = judgementData["StreetAddress"].str.replace(r'(\#\d{1,4})', "", regex=True)
    # if there is a number that looks like "APT 402" in the street address column, copy that number to a new column called "Unit"
    # and then drop the number from the "StreetAddress" column
    # judgementData["Unit"] = judgementData["StreetAddress"].str.extract(r'(\b[A-Z]{3}\s\d{1,4}\b)')
    # judgementData["StreetAddress"] = judgementData["StreetAddress"].str.replace(r'(\b[A-Z]{3}\s\d{1,4}\b)', "", regex=True)
    # Drop any instance of "APT" in the "StreetAddress" column but keep the rest of the string
    # judgementData["StreetAddress"] = judgementData["StreetAddress"].str.replace(r'(\b[A-Z]{3}\b)', "", regex=True)
    #
    # Remove any Cardinal Directions from the "StreetAddress" column and put it into its own column called "CardinalDirection"
    # include NW, NE, SW, SE, N, S, E, W and replace the characters with a space
    # judgementData["CardinalDirection"] = judgementData["StreetAddress"].str.extract(r'(\b[NW|NE|SW|SE|N|S|E|W]{1,2}\b)')
    # judgementData["StreetAddress"] = judgementData["StreetAddress"].str.replace(r'(\b[NW|NE|SW|SE|N|S|E|W]{1,2}\b)', "", regex=True)
    #
    # Copy any Rows that Contain a "PIN" in the "DocLegalDescription" column to a new column called "PIN"
    # judgementData["PIN"] = judgementData["DocLegalDescription"].where(judgementData["DocLegalDescription"].str.contains("PIN"))
    # If There is a PIN Find the PIN that will look like xxxxxx-xxxx and drop the rest of the text
    # judgementData["PIN"] = judgementData["PIN"].str.extract(r'(\\d{4}-\d{4}|\d{6}-\d{4}|\d{4}-\d{4}|\d{4} \d{4})')
    #
    # The Last 5 numbers in street address will be the Zip Code
    # judgementData["ZipCode"] = judgementData["StreetAddress"].str.extract(r'(\d{5})')
    # Drop the last 5 numbers from the "StreetAddress" column
    # judgementData["StreetAddress"] = judgementData["StreetAddress"].str.replace(r'(\d{5})', "", regex=True)
    # the Last Two Characters in the "StreetAddress" column will be the State
    # judgementData["State"] = judgementData["StreetAddress"].str.extract(r'(\b[A-Z]{2}\b)')
    # Drop the last two characters from the "StreetAddress" column
    # judgementData["StreetAddress"] = judgementData["StreetAddress"].str.replace(r'(\b[A-Z]{2}\b)', "", regex=True)
    # The City Should match a city in the "CityList" global list
    # judgementData["City"] = judgementData["StreetAddress"].str.extract(r'(\b' + '|'.join(Cities) + r'\b)')
    # Drop the City from the "StreetAddress" column
    # judgementData["StreetAddress"] = judgementData["StreetAddress"].str.replace(r'(\b' + '|'.join(Cities) + r'\b)', "", regex=True)
    #
    # Remove any extra spaces from the "StreetAddress" column
    # judgementData["StreetAddress"] = judgementData["StreetAddress"].str.replace(r'(\s{2,})', " ", regex=True)
    #
    # Drop the "DocLegalDescription" column
    # judgementData = judgementData.drop(columns=["DocLegalDescription", "Consideration", "DocLink", "BookType", "BookPage", "InstrumentNumber"])
    #
    # reorder columns as DirectName,IndirectName,RecordDate,DocTypeDescription,StreetNumber, StreetAddress, StreetPrefix, Unit, CardinalDirection, City, State, ZipCode, PIN
    #
    # No limit on number of columns shown
    # pd.set_option('display.max_columns', None)
    # print(judgementData)
    # judgementData.to_csv(os.getcwd() + "/Downloads/Judgement.csv", index=False)
    # return judgementData