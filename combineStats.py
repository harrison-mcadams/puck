def combineStats(team, stat, year):
    from datetime import datetime
    import numpy as np
    import requests
    import json
    import pandas as pd
    import getPlayerData

    minGamesPlayed = 50

    full_url = 'http://statsapi.web.nhl.com/api/v1/teams'

    response = requests.get(full_url)
    teams = json.loads(response.content)


    for ii in teams['teams']:
        if team in ii['name']:
            teamID = ii['id']
            teamID = list(range(teamID,teamID+1))

    if team == 'league':
        teamID = []
        for ii in teams['teams']:
            teamID.append(ii['id'])
        #teamID = list(range(1, len(teams['teams'])))


    combinedData = []
    combinedRoster = []

    for tt in teamID:
    #for tt in list(range(11,11+1)):
        team_url = 'http://statsapi.web.nhl.com/api/v1/teams/' + str(tt) + '/roster'
        response = requests.get(team_url)
        teamRoster = json.loads(response.content)

        for rr in teamRoster['roster']:
            playerID = rr['person']['id']
            print(rr['person']['fullName'])

            gamesPlayed = getPlayerData.getPlayerData(playerID, 'games', year)

            if gamesPlayed > minGamesPlayed:
                playerData = getPlayerData.getPlayerData(playerID, stat, year)
                combinedData.append(playerData)
                combinedRoster.append(playerID)
                print('- stat: ' + str(playerData))

    # remove duplicates
    noDuplicatePlayers = set(combinedRoster)

    return combinedData