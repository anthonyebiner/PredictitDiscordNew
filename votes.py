import requests
import pandas as pd
from datetime import datetime
import pytz


class WisconsinRecount:
    def __init__(self):
        self.data = None
        self.reload_data()

    def reload_data(self):
        date = datetime.utcnow().replace(tzinfo=pytz.timezone('America/Chicago'))
        try:
            response = requests.get("https://elections.wi.gov/sites/elections.wi.gov/files/2020-11/2020%20General%20Election%20Recount%2011-" + str(date.day-1) + "-20.xlsx")
            self.data = pd.read_excel(response.content)
        except:
            response = requests.get(
                "https://elections.wi.gov/sites/elections.wi.gov/files/2020-11/2020%20General%20Election%20Recount%2011-" + str(
                    date.day) + "-20.xlsx")
            self.data = pd.read_excel(response.content)

    def count(self):
        data = self.data
        row = 0
        for i, column in enumerate(data.columns):
            if "Vote Count Change Due to Recount" in column:
                row = i
        biden_row = data.iloc[:, [row]]
        trump_row = data.iloc[:, [row+1]]

        biden_votes = 0
        trump_votes = 0
        for value in biden_row.values[1:]:
            if value != "inc":
                biden_votes += value
        for value in trump_row.values[1:]:
            if value != "inc":
                trump_votes += value

        return biden_votes, trump_votes
