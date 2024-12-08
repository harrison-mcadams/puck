def getGameID():

    import requests
    from datetime import date

    # Get today's date in the format YYYY-MM-DD
    today = date.today().strftime("%Y-%m-%d")

    url = f"https://api-web.nhle.com/v1/schedule/{today}"
    response = requests.get(url)
    games = response.json()

    for ii in range(0,7):
        if games['gameWeek'][ii]['date'] == today:
            for game in games['gameWeek'][ii]['games']:
                if game['awayTeam']['commonName']['default'] == 'Flyers' or game['homeTeam']['commonName']['default'] == 'Flyers':
                    gameID = game['id']


    return gameID