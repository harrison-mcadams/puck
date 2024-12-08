def getPlayerData(playerID, stat, year):
    from datetime import datetime
    import numpy as np
    import requests
    import json
    import pandas as pd


    url = 'https://statsapi.web.nhl.com/api/v1/people/' + str(playerID) + '/stats/?stats=yearByYear'
    response = requests.get(url)
    content = json.loads(response.content)['stats']
    splits = content[0]['splits']

    df_splits = (pd.json_normalize(splits, sep="_")
                 .query('league_name == "National Hockey League"')
                 )

    if df_splits.empty:
        data = np.nan
        return data

    if 'stat_evenSaves' in list(df_splits.columns):   # player is a goalie
        # don't have to do anything
        print('we have a goalie')
        goalie=True

    else: # player is a skater
        df_splits['goals_per_game'] = df_splits['stat_goals'] / df_splits['stat_games']
        df_splits['stat_goals_per_60'] = np.nan
        goalie = False

    df_splits['player_id'] = playerID
    df_splits['season_end'] = [x[4:8] for x in df_splits['season']]
    df_splits['season_start_yr'] = [x[0:4] for x in df_splits['season']]
    df_splits['season_start_dt'] = [datetime.strptime(x + '0930', "%Y%m%d") for x in df_splits['season_start_yr']]
    buffer = [x.split(':') for x in df_splits['stat_timeOnIce']]
    df_splits['timeOnIce_inMinutes'] = [float(x[0]) + float(x[1])/60 for x in buffer]

    if 'stat_' + stat in df_splits.loc[df_splits['season_start_yr'] == year].columns:
        if stat != 'goals_per_60':
            data = df_splits.loc[df_splits['season_start_yr'] == year]['stat_' + stat].sum()
        else:
            totalTime = df_splits.loc[df_splits['season_start_yr'] == year]['timeOnIce_inMinutes'].sum()
            totalGoals = df_splits.loc[df_splits['season_start_yr'] == year]['stat_goals'].sum()
            data = totalGoals/totalTime*60


    else:
        data = np.nan
        print('No stat found')

    return data


