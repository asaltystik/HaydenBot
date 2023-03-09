@echo off

rem Change to the directory where this batch file is located
cd %~dp0

rem Set the name of the Python script to run
set SCRIPT_NAME=main.py

rem Find the root folder of the Python script
set ROOT_FOLDER=%~dp0

rem update pip
pip3 install --upgrade pip

rem Check if pip installed pandas
pip3 show pandas > nul 2>&1
if errorlevel 1 (
    echo "Pandas is not installed. Installing..."
    pip3 install pandas
)

rem check if pip installed Selenium
pip3 show selenium > nul 2>&1
if errorlevel 1 (
    echo "Selenium is not installed. Installing..."
    pip3 install selenium
)

rem check if pip installed BeautifulSoup4
pip3 show bs4 > nul 2>&1
if errorlevel 1 (
    echo "BeautifulSoup4 is not installed. Installing..."
    pip3 install bs4
)

rem check if pip installed chromedriver
pip3 show chromedriver > nul 2>&1
if errorlevel 1 (
    echo "Chromedriver is not installed. Installing..."
    pip3 install chromedriver
)

rem check if pip installed requests
pip3 show requests > nul 2>&1
if errorlevel 1 (
    echo "Requests is not installed. Installing..."
    pip3 install requests
)

rem check if pip installed undetected-chromedriver
pip3 show undetected-chromedriver > nul 2>&1
if errorlevel 1 (
    echo "Undetected-chromedriver is not installed. Installing..."
    pip3 install undetected-chromedriver
)

rem create a folder named "Downloads" and "Parsed" in the working directory if it doesn't exist
if not exist "%ROOT_FOLDER%Downloads" mkdir "%ROOT_FOLDER%Downloads"
if not exist "%ROOT_FOLDER%Parsed" mkdir "%ROOT_FOLDER%Parsed"

rem Run the Python script
python3 "%ROOT_FOLDER%%SCRIPT_NAME%"
