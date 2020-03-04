import requests


class DDHQ:
    def __init__(self, state, alignment):
        self.url = "https://results.decisiondeskhq.com/api/v1/elections/?limit=1000&featured=true"
        self.state = state  # string representing state, should be like "ia", "IA", "Iowa", "IOWA", etc.
        self.alignment = alignment

        """ CANDIDATE IDs USED BY DDHQ:
            klobuchar: 8233
            sanders: 8
            warren: 8284
            steyer: 11921
            biden: 11918
            buttigieg: 11919
            yang: 11920
            bloomberg: 11954
            """

    def get_data(self):
        """
        Uses API to get json vote data
        :return: A dictionary of the raw vote data from DDHQ
        """
        response = requests.get(url=self.url)
        return response.json()

    def get_race_url(self):
        data = self.get_data()
        races = data['results']
        countyurl = 'County data not found.'
        # Identify which race matches the passed in state:
        for i in range(0, len(races)):
            print(races[i]['state'])
            if ((races[i]['state'].lower() == self.state.lower() or races[i][
                'stateAbbr'].lower() == self.state.lower()) and races[i]['party'] == 'Democratic' and races[i][
                'office'] == 'president'):
                if races[i]['electionType'] == 'caucus_round_1' and self.alignment == 1:
                    countyurl = "https://results.decisiondeskhq.com/api/v1/results/?election=" + races[i][
                        'id'] + "&electionType=primary&limit=1&offset=0"
                    break
                elif races[i]['electionType'] == 'caucus_round_2' and self.alignment == 2:
                    countyurl = "https://results.decisiondeskhq.com/api/v1/results/?election=" + races[i][
                        'id'] + "&electionType=primary&limit=1&offset=0"
                    break
                elif races[i]['electionType'] == 'caucus' or races[i]['electionType'] == 'primary':
                    countyurl = "https://results.decisiondeskhq.com/api/v1/results/?election=" + races[i][
                        'id'] + "&electionType=primary&limit=1&offset=0"
                    break
        return countyurl

    def get_totals(self):
        """
        :return: A dictionary of how many votes each candidate has in the state
        {"sanders": 1234, "biden":1200, ..., "precinct_total": 400, "precinct_counted": 132, etc}
        """
        data = self.get_data()
        races = data['results']
        x = -1
        countyurl = 'County data not found.'
        # Identify which race matches the passed in state:
        for i in range(0, len(races)):
            if ((races[i]['state'].lower() == self.state.lower() or races[i][
                'stateAbbr'].lower() == self.state.lower()) and races[i]['party'] == 'Democratic' and races[i][
                'office'] == 'president'):
                if races[i]['electionType'] == 'caucus_round_1' and self.alignment == 1:
                    x = i
                    countyurl = "https://results.decisiondeskhq.com/api/v1/results/?election=" + races[i][
                        'id'] + "&electionType=primary&limit=1&offset=0"
                elif races[i]['electionType'] == 'caucus_round_2' and self.alignment == 2:
                    x = i
                    countyurl = "https://results.decisiondeskhq.com/api/v1/results/?election=" + races[i][
                        'id'] + "&electionType=primary&limit=1&offset=0"
                elif races[i]['electionType'] == 'caucus' or races[i]['electionType'] == 'primary':
                    x = i
                    countyurl = "https://results.decisiondeskhq.com/api/v1/results/?election=" + races[i][
                        'id'] + "&electionType=primary&limit=1&offset=0"
        # Initialize vote totals to 0 and assign list of candidates for specified race:
        votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                 'Bloomberg': 0, 'Total': 0}
        candidates = races[x]['candidates']
        # Count Votes and vote total for each candidate we're counting for (the ones initialized to 0 above)
        for i in range(0, len(candidates)):
            votes['Total'] += candidates[i]['votes']
            if candidates[i]['lastName'] in votes.keys():
                votes[candidates[i]['lastName']] = candidates[i]['votes']
        countydata = requests.get(countyurl).json()
        votes['precinct_total'] = countydata['results'][0]['precincts']['total']
        votes['precinct_counted'] = countydata['results'][0]['precincts']['reporting']
        return votes

    def get_national_totals(self):
        """
        :return: A dictionary of how many votes each candidate has nationally across all states
        {"sanders": 1234, "biden":1200, ..., "precinct_total": 400, "precinct_counted": 132, etc}
        """
        data = self.get_data()
        races = data['results']
        votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                 'Bloomberg': 0, 'Total': 0}
        for i in range(0, len(races)):
            if races[i]['electionType'].lower() == "primary" or races[i]['electionType'].lower() == "caucus_round_2":
                candidates = races[i]['candidates']
                for i in range(0, len(candidates)):
                    votes['Total'] += candidates[i]['votes']
                    if candidates[i]['lastName'] in votes.keys():
                        votes[candidates[i]['lastName']] += candidates[i]['votes']
        return votes

    def get_totals_sum(self, states):
        """
        :input: list of strings representing the states you wish summed, ex for super tuesday:
                ["ca","ut","co","tx","ok","mn","ar","tn","al","nc","va","ma","vt","me","da","as"]
                also works for a single state, ex: ["ia"]
        :return: A dictionary of how many votes each candidate has summed up across designated states
        {"sanders": 1234, "biden":1200, ..., "precinct_total": 400, "precinct_counted": 132, etc}
        """
        data = self.get_data()
        races = data['results']
        votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                 'Bloomberg': 0, 'Total': 0}
        for state in states:
            state = state.lower()
        for i in range(0, len(races)):
            if (races[i]['state'].lower() in states or races[i]['stateAbbr'].lower() in states) and races[i][
                'electionType'].lower() == "primary" or races[i]['electionType'].lower() == "caucus_round_2":
                candidates = races[i]['candidates']
                for i in range(0, len(candidates)):
                    votes['Total'] += candidates[i]['votes']
                    if candidates[i]['lastName'] in votes.keys():
                        votes[candidates[i]['lastName']] += candidates[i]['votes']
        return votes

    def get_all_counties(self):
        county_results = {}
        data = self.get_data()
        races = data['results']
        countyurl = self.get_race_url()

        countydata = requests.get(countyurl).json()
        county_raw = countydata['results'][0]['counties']
        for i in range(0, len(county_raw)):
            votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                     'Bloomberg': 0, 'Total': 0}

            for cid in county_raw[i]['votes']:
                if cid == '8233':
                    votes['Klobuchar'] = county_raw[i]['votes'][cid]
                elif cid == '8':
                    votes['Sanders'] = county_raw[i]['votes'][cid]
                elif cid == '8284':
                    votes['Warren'] = county_raw[i]['votes'][cid]
                elif cid == '11921':
                    votes['Steyer'] = county_raw[i]['votes'][cid]
                elif cid == '11918':
                    votes['Biden'] = county_raw[i]['votes'][cid]
                elif cid == '11919':
                    votes['Buttigieg'] = county_raw[i]['votes'][cid]
                elif cid == '11920':
                    votes['Yang'] = county_raw[i]['votes'][cid]
                elif cid == '11954':
                    votes['Bloomberg'] = county_raw[i]['votes'][cid]
                votes['Total'] += county_raw[i]['votes'][cid]
            county_results[county_raw[i]['county'].lower()] = votes

        # FOR DEBUGGING, MAYBE ADD LATER:
        votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                 'Bloomberg': 0, 'Total': 0}
        for county in county_results:
            # votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            #    'Bloomberg': 0, 'Total': 0}
            for candidate in county_results[county].keys():
                votes[candidate] += county_results[county][candidate]

        county_results['Total'] = votes
        # """

        return county_results

    def get_all_precincts(self):
        precinct_results = {}
        data = self.get_data()
        races = data['results']
        countyurl = self.get_race_url()

        countydata = requests.get(countyurl).json()
        precinct_raw = countydata['results'][0]['vcus']['counties']
        for i in range(0, len(precinct_raw)):
            for j in range(0, len(precinct_raw[i]['vcus'])):
                votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                         'Bloomberg': 0, 'Total': 0}
                for cid in precinct_raw[i]['vcus'][j]['votes']:
                    if cid == '8233':
                        votes['Klobuchar'] = precinct_raw[i]['vcus'][j]['votes'][cid]
                    elif cid == '8':
                        votes['Sanders'] = precinct_raw[i]['vcus'][j]['votes'][cid]
                    elif cid == '8284':
                        votes['Warren'] = precinct_raw[i]['vcus'][j]['votes'][cid]
                    elif cid == '11921':
                        votes['Steyer'] = precinct_raw[i]['vcus'][j]['votes'][cid]
                    elif cid == '11918':
                        votes['Biden'] = precinct_raw[i]['vcus'][j]['votes'][cid]
                    elif cid == '11919':
                        votes['Buttigieg'] = precinct_raw[i]['vcus'][j]['votes'][cid]
                    elif cid == '11920':
                        votes['Yang'] = precinct_raw[i]['vcus'][j]['votes'][cid]
                    elif cid == '11954':
                        votes['Bloomberg'] = precinct_raw[i]['vcus'][j]['votes'][cid]
                    votes['Total'] += precinct_raw[i]['vcus'][j]['votes'][cid]
                precinct_results[precinct_raw[i]['vcus'][j]['vcu'].lower()] = votes

        return precinct_results

    def get_county(self, county_name):
        """
        :return: A dictionary of how many votes each candidate has in the county
        {"sanders": 100, "biden":20, ..., "precinct_total": 50, "precinct_counted": 12, etc}
        """
        return self.get_all_counties()[county_name.lower()]

    def get_precinct(self, precinct_name):
        """
        :return: A dictionary of how many votes each candidate has in the precinct
        {"sanders": 100, "biden":20, ..., "reported": True, etc}
        """
        return self.get_all_precincts()[precinct_name.lower()]

    def get_reporting(self):
        data = requests.get(self.get_race_url()).json()
        print(data['results'][0]['precincts']['reporting'])
        return data['results'][0]['precincts']['reporting'] / data['results'][0]['precincts']['total'] * 100


class Edison:
    def __init__(self, state):
        # self.url = "https://politics-elex.data.api.cnn.io/graphql?operationName=AllCountyRaces&variables=%7B\"electionDate\"%3A\"_2020\"%2C\"partyCode\"%3A\"D\"%2C\"stateCode\"%3A\"" + state + "\"%2C\"raceTypeCode\"%3A\"P\"%7D&extensions=%7B\"persistedQuery\"%3A%7B\"version\"%3A1%2C\"sha256Hash\"%3A\"1b4b82c69d45307f7406e49751ea10185dce2798d08649764d69c240df529097\"%7D%7D\""

        self.url = "https://politics-elex.data.api.cnn.io/graphql?operationName=AllCountyRaces&variables=%7B%22electionDate%22%3A%22_2020%22%2C%22partyCode%22%3A%22D%22%2C%22stateCode%22%3A%22" + state + "%22%2C%22raceTypeCode%22%3A%22P%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%221b4b82c69d45307f7406e49751ea10185dce2798d08649764d69c240df529097%22%7D%7D"

        # exit polls: https://politics-elex.data.api.cnn.io/graphql?operationName=ExitPolls&variables=%7B%22stateCode%22%3A%22NH%22%2C%22partyCode%22%3A%22D%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22b9de6c88cd0fec6fa431e775cfb1be75182bc6323ba8a0182d4dcf4e319a827b%22%7D%7D
        # NV: https://politics-elex.data.api.cnn.io/graphql?operationName=AllCountyRaces&variables=%7B"electionDate"%3A"_2020"%2C"partyCode"%3A"D"%2C"stateCode"%3A"NV"%2C"raceTypeCode"%3A"P"%7D&extensions=%7B"persistedQuery"%3A%7B"version"%3A1%2C"sha256Hash"%3A"1b4b82c69d45307f7406e49751ea10185dce2798d08649764d69c240df529097"%7D%7D
        # NH: https://politics-elex.data.api.cnn.io/graphql?operationName=AllCountyRaces&variables=%7B%22electionDate%22%3A%22_2020%22%2C%22partyCode%22%3A%22D%22%2C%22stateCode%22%3A%22NH%22%2C%22raceTypeCode%22%3A%22P%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%221b4b82c69d45307f7406e49751ea10185dce2798d08649764d69c240df529097%22%7D%7D

    def get_data(self):
        """
        Uses API to get json vote data
        :return: A dictionary of the raw vote data from DDHQ
        """
        return requests.get(url=self.url).json()

    def get_totals(self):
        """
        :return: A dictionary of how many votes each candidate has in the state
        {"sanders": 1234, "biden":1200, ..., "precinct_total": 400, "precinct_counted": 132, etc}
        """
        county_results = self.get_all_counties()
        votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                 'Bloomberg': 0, 'Total': 0}
        for county in county_results:
            if county != 'Total':
                for candidate in county_results[county].keys():
                    if candidate in votes.keys(): votes[candidate] += county_results[county][candidate]

        return votes

    def get_all_counties(self):
        county_results = {}
        data = self.get_data()
        counties = data['data']['mapCountyPrimariesResults']
        for county in counties:
            votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                     'Bloomberg': 0, 'Total': 0}
            for candidate in county['candidates']:
                if candidate['lastName'] in votes.keys():
                    votes[candidate['lastName']] = candidate['voteNum']
                votes['Total'] += candidate['voteNum']
            county_results[county['countyName'].lower()] = votes

        # GET TOTALS:
        votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                 'Bloomberg': 0, 'Total': 0}
        for county in county_results:
            for candidate in county_results[county].keys():
                votes[candidate] += county_results[county][candidate]
        county_results['Total'] = votes
        # """

        return county_results

    def get_all_precincts(self):
        precinct_results = {}
        return precinct_results

    def get_county(self, county_name):
        """
        :return: A dictionary of how many votes each candidate has in the county
        {"sanders": 100, "biden":20, ..., "precinct_total": 50, "precinct_counted": 12, etc}
        """
        return self.get_all_counties()[county_name.lower()]

    def get_precinct(self, precinct_name):
        """
        :return: A dictionary of how many votes each candidate has in the precinct
        {"sanders": 100, "biden":20, ..., "reported": True, etc}
        """
        return self.get_all_precincts()[precinct_name.lower()]

    def get_reporting(self):
        return 0


class AP:
    def __init__(self, state, alignment):
        self.alignment = alignment
        self.state = state
        self.url = "https://int.nyt.com/applications/elections/2020/data/api/2020-{}/{}/president/democrat.json".format(
            self.get_date(), state)

    def get_date(self):
        schedule = {'iowa': '02-03',
                    'new-hampshire': '02-11',
                    'nevada': '02-22',
                    'south-carolina': '02-29',
                    'alabama': '03-03',
                    'american-samoa': '03-03',
                    'arkansas': '03-03',
                    'california': '03-03',
                    'colorado': '03-03',
                    'democrats-abroad': '03-03',
                    'maine': '03-03',
                    'massachusetts': '03-03',
                    'minnesota': '03-03',
                    'north-carolina': '03-03',
                    'oklahoma': '03-03',
                    'tennessee': '03-03',
                    'texas': '03-03',
                    'utah': '03-03',
                    'vermont': '03-03',
                    'virginia': '03-03',
                    'idaho': '03-10',
                    'michigan': '03-10',
                    'mississippi': '03-10',
                    'missouri': '03-10',
                    'washington': '03-10',
                    'arizona': '03-17',
                    'florida': '03-17',
                    'georgia': '03-24',
                    'puerto-rico': '03-29',
                    'alaska': '04-04',
                    'hawaii': '04-04',
                    'louisiana': '04-04',
                    'wyoming': '04-04',
                    'wisconsin': '04-07',
                    'connecticut': '04-28',
                    'delaware': '04-28',
                    'maryland': '04-28',
                    'new-york': '04-28',
                    'pennsylvania': '04-28',
                    'rhode-island': '04-28',
                    'guam': '05-02',
                    'kansas': '05-02',
                    'indiana': '05-05',
                    'nebraska': '05-12',
                    'west-virginia': '05-12',
                    'kentucky': '05-19',
                    'oregon': '05-19',
                    'district-of-columbia': '06-02',
                    'montana': '06-02',
                    'new-jersey': '06-02',
                    'new-mexico': '06-02',
                    'south-dakota': '06-02',
                    'virgin-islands': '06-07', }
        return schedule[self.state]

    def get_data(self):
        """
        Uses API to get json vote data
        :return: A dictionary of the raw vote data from AP
        """
        return requests.get(url=self.url).json()

    def get_totals(self):
        """
        :return: A dictionary of how many votes each candidate has in the state
        {"sanders": 1234, "biden":1200, ..., "precinct_total": 400, "precinct_counted": 132, etc}
        """
        data = self.get_data()
        votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                 'Bloomberg': 0, 'Total': 0, 'Precincts': 0, 'Reporting': 0}
        for candidate in data['data']['races'][0]['candidates']:
            try:
                if self.alignment == 1:
                    votes[candidate['last_name']] += candidate['votes_align1']
                elif self.alignment == 2:
                    votes[candidate['last_name']] += candidate['votes_alignfinal']
                else:
                    votes[candidate['last_name']] += candidate['votes']
            except KeyError:
                pass
            votes['Total'] += candidate['votes']
        votes['Precincts'] = data['data']['races'][0]['precincts_reporting']
        votes['Reporting'] = data['data']['races'][0]['precincts_total']
        return votes

    def get_all_counties(self):
        county_results = {}
        data = self.get_data()
        county_raw = data['data']['races'][0]['counties']
        results = "results"
        for place in county_raw:
            votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                     'Bloomberg': 0, 'Total': 0}
            if self.alignment == 1:
                results = "results_align1"
            elif self.alignment == 2:
                results = "results_alignfinal"
            for name, num in place[results].items():
                for key in votes.keys():
                    if key.lower() in name:
                        votes[key] = num
                votes['Total'] += num
            county_results[place['name'].lower()] = votes

        # GET TOTALS:
        votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                 'Bloomberg': 0, 'Total': 0}
        for county in county_results:
            for candidate in county_results[county].keys():
                votes[candidate] += county_results[county][candidate]
        county_results['Total'] = votes
        # """
        return county_results

    def get_county(self, county_name):
        """
        :return: A dictionary of how many votes each candidate has in the county
        {"sanders": 100, "biden":20, ..., "precinct_total": 50, "precinct_counted": 12, etc}
        """
        return self.get_all_counties()[county_name.lower()]

    def get_all_precincts(self):
        precinct_results = {}
        data = self.get_data()
        town_results = data['data']['races'][0]['townships']
        for place in town_results:
            votes = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
                     'Bloomberg': 0, 'Total': 0}
            for name, num in place['results'].items():
                for key in votes.keys():
                    if key.lower() in name:
                        votes[key] = num
                votes['Total'] += num
            precinct_results[place['name'].lower()] = votes
        return precinct_results

    def get_precinct(self, precinct_name):
        return self.get_all_precincts()[precinct_name.lower()]

    def get_reporting(self):
        data = requests.get(self.url).json()
        print(data['data']['races'][0]['precincts_reporting'])
        return data['data']['races'][0]['precincts_reporting'] / data['data']['races'][0]['precincts_total'] * 100


def MergeResults(APres, DDHQres):
    mergedData = {}

    for precinct in APres.keys():
        if precinct in DDHQres.keys():
            if APres[precinct]['Total'] > DDHQres[precinct]['Total']:
                mergedData[precinct] = APres[precinct]
            else:
                mergedData[precinct] = DDHQres[precinct]
        else:
            mergedData[precinct] = APres[precinct]
    for precinct in DDHQres.keys():
        if precinct in APres.keys():
            if APres[precinct]['Total'] > DDHQres[precinct]['Total']:
                mergedData[precinct] = APres[precinct]
            else:
                mergedData[precinct] = DDHQres[precinct]
        else:
            mergedData[precinct] = DDHQres[precinct]

    # FOR DEBUGGING: identify differing precincts:
    """
    for precinct in APres.keys():
        if precinct in mergedData:
            if APres[precinct] != mergedData[precinct]:
                print("DISCREPENCY FOUND: " + precinct)
                print("AP, DDHQ, merged: ")
                print(APres[precinct])
                print(DDHQres[precinct])
                print(mergedData[precinct])
    """

    mergedData['Total'] = {'Klobuchar': 0, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0,
                           'Buttigieg': 0, 'Bloomberg': 0, 'Total': 0}
    for precinct in mergedData:
        if precinct != 'Total':
            mergedData['Total']['Klobuchar'] += mergedData[precinct]['Klobuchar']
            mergedData['Total']['Sanders'] += mergedData[precinct]['Sanders']
            mergedData['Total']['Warren'] += mergedData[precinct]['Warren']
            mergedData['Total']['Yang'] += mergedData[precinct]['Yang']
            mergedData['Total']['Steyer'] += mergedData[precinct]['Steyer']
            mergedData['Total']['Biden'] += mergedData[precinct]['Biden']
            mergedData['Total']['Buttigieg'] += mergedData[precinct]['Buttigieg']
            mergedData['Total']['Bloomberg'] += mergedData[precinct]['Bloomberg']
            mergedData['Total']['Total'] += mergedData[precinct]['Total']
    return mergedData


def MergeAllResults(data):
    mergedData = data[0]
    for i in range(1, len(data)):
        mergedData = MergeResults(mergedData, data[i])
    return mergedData
