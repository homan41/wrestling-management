import pandas as pd
import requests
from bs4 import BeautifulSoup

def removeTeamNameFromWrestlerName(nameOfWrestler):
    nameOfWrestler = nameOfWrestler.split(" (")
    return nameOfWrestler[0]

def get_scoring_table_from_web():
    userAgent = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
    }
    html = requests.get("https://pennstatewrestlingclub.org/team_scores/?id=31&type=individual", auth = ("jholenda", "jared25"), headers = userAgent)

    soup = BeautifulSoup(html.text, features = "lxml")

    table = soup.find('table', attrs = {'class': 'benresponsive'})
    data = []
    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            row_data.append(cell.text)
        data.append(row_data)

    return pd.DataFrame(data)

def get_score_dictionary():
    scoring_dictionary = {}
    scoring_table = get_scoring_table_from_web()
    for row in range(len(scoring_table)):
        if scoring_table.loc[row, 0] is None: continue
        wrestlerName = removeTeamNameFromWrestlerName(scoring_table.loc[row, 0])
        wrestlerScore = scoring_table.loc[row, 1]
        scoring_dictionary[wrestlerName] = wrestlerScore

    return scoring_dictionary