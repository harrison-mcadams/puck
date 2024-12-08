def getPlayerID(first_name, last_name):
    from datetime import datetime
    import numpy as np
    import requests
    import json
    import pandas as pd

    base_url = 'https://suggest.svc.nhl.com/svc/suggest/v1/minplayers/'

    #num_to_return = '10'

    #full_url = base_url + first_name + '%20' + last_name + '/' + num_to_return
    full_url = base_url + first_name + '%20' + last_name + '/'

    response = requests.get(full_url)
    suggestion = json.loads(response.content)['suggestions']

    if len(suggestion) > 1:
        print("Potential name conflict")

    suggestion = suggestion[0]


    playerInfo = str.split(suggestion, "|")
    playerID = playerInfo[0]

    return playerID