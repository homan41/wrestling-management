from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd

def remove_team_name_from_wrestler_name_two(nameOfWrestler):
    nameOfWrestler = nameOfWrestler.split(" (")
    return nameOfWrestler[0]

def get_table_from_web():
    """Get the table from the Penn State Wrestling Club website."""
    # Set up the Selenium WebDriver
    driver = webdriver.Chrome()

    # Navigate to the login page
    driver.get('https://pennstatewrestlingclub.org/login/')

    # Log into the website
    username = driver.find_element(By.NAME, 'log')
    password = driver.find_element(By.NAME, 'pwd')
    username.send_keys('jholenda')
    password.send_keys('jared25')
    password.send_keys(Keys.RETURN)

    # Navigate to the data page and wait for content to load
    driver.get('https://pennstatewrestlingclub.org/team_scores/?id=31&type=individual')
    driver.implicitly_wait(10)  # Wait for elements to load

    # Extract page source and parse with pandas
    html = driver.page_source
    tables = pd.read_html(html)

    # Close the browser
    driver.quit()

    # Use the first table
    return tables[0]


def get_score_dictionary_two():
    """Convert the pandas table to a dictionary of wrestler scores."""
    scoring_dictionary = {}
    scoring_table = get_table_from_web()
    for index, row in scoring_table.iterrows():
        wrestler_name = remove_team_name_from_wrestler_name_two(row[0])
        wrestler_score = row[1]
        scoring_dictionary[wrestler_name] = wrestler_score

    return scoring_dictionary


