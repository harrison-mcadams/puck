def plotShotDensityMap(ax, gameID):
    import requests
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib.colors as mcolors
    import makeStruct
    import getpass


    # Parameters
    sigma_x, sigma_y = 5, 5  # Standard deviations

    # Define savePath
    username = getpass.getuser()
    if username == 'harrisonmcadams':
        savePath = '/Users/harrisonmcadams/Desktop/'
    else:
        savePath = './'

    # Get and parse the play-by-play data
    playByPlayAddress = 'https://api-web.nhle.com/v1/gamecenter/' + str(gameID) + '/play-by-play'
    response = requests.get(playByPlayAddress)
    data = response.json()

    # Figure out who's playing
    if data['homeTeam']['commonName']['default'] == 'Flyers':
        homeTeam = 'Flyers'
        awayTeam = data['awayTeam']['commonName']['default']
        otherTeam = awayTeam
    else:
        awayTeam = 'Flyers'
        homeTeam = data['homeTeam']['commonName']['default']
        otherTeam = homeTeam


    # Assemble Flyers roster
    flyersRoster = []
    for player in data['rosterSpots']:
        if player['teamId'] == 4:
            flyersRoster.append(player['playerId'])

    # Define x and y range. We will ultimately plot over these values
    x, y = np.meshgrid(np.linspace(-102, 102, 205), np.linspace(-50, 50, 101))

    # Stats to pool
    statLabelsToPool = ['shot-on-goal', 'missed-shot', 'goal', 'blocked-shot']
    stats = makeStruct.makeStruct([statLabelsToPool, [homeTeam, awayTeam], ['xs', 'ys']])

    # Initialize shotDensity maps
    shotDensities = makeStruct.makeStruct([homeTeam, awayTeam, 'combined'])
    shotDensities[homeTeam] = np.zeros((101,205))
    shotDensities[awayTeam] = np.zeros((101,205))
    shotDensities['combined'] = np.zeros((101,205))


    # Loop over plays
    for ii in data['plays']:

        # Identify the event in question
        statType = ii['typeDescKey']

        # Pool all shots-on-goal, goals, missed-shots, and blocked-shots
        if statType in statLabelsToPool:

            ## Get some information about the event
            # Deal with flipping sides between periods. Specifying use cases depending on if the Flyers are the home or awway team
            if ii['homeTeamDefendingSide'] == 'left' and data['homeTeam']['commonName']['default'] == 'Flyers':
                rotationMultiplier = -1

            elif ii['homeTeamDefendingSide'] == 'right' and data['homeTeam']['commonName']['default'] == 'Flyers':
                rotationMultiplier = 1

            else:
                if ii['homeTeamDefendingSide'] == 'left':
                    rotationMultiplier = 1

                if ii['homeTeamDefendingSide'] == 'right':
                    rotationMultiplier = -1

            # Extract eventPlayerID
            if ii['typeDescKey'] == 'goal':
                eventPlayerID = int(ii['details']['scoringPlayerId'])

            else:
                eventPlayerID = int(ii['details']['shootingPlayerId'])

            # Get the team of the eventPlayer
            if eventPlayerID in flyersRoster:
                eventTeam = 'Flyers'

            else:
                eventTeam = otherTeam

            # Obtain the x and y locations
            xLocation = ii['details']['xCoord']
            yLocation = ii['details']['yCoord']

            # Adjust location per period
            x_rotated, y_rotated = xLocation*rotationMultiplier, yLocation*rotationMultiplier  # Mean values

            # Stash the location
            stats[statType][eventTeam]['xs'].append(x_rotated)
            stats[statType][eventTeam]['ys'].append(y_rotated)

            # Smooth the location data
            z = (1 / (2 * np.pi * sigma_x * sigma_y)) * np.exp(
                -(((x - x_rotated) ** 2) / (2 * sigma_x ** 2) + ((y - y_rotated) ** 2) / (2 * sigma_y ** 2)))

            # Stash the smoothed data on the shotDensity map
            shotDensities[eventTeam] = z + shotDensities[eventTeam]



    ## Do the plotting of the shotDensity maps
    # Define min and max shotDensity map values, so we can set a symmetric color bar
    vmax = np.max([np.abs(shotDensities[homeTeam]), np.abs(shotDensities[awayTeam])])

    # Censor values close to 0
    threshold = 0.001
    mask = shotDensities[homeTeam] < threshold
    shotDensities[homeTeam][mask] = 0

    mask = shotDensities[awayTeam] < threshold
    shotDensities[awayTeam][mask] = 0

    # Combine shotDensity map
    shotDensities['combined'] = shotDensities['Flyers'] - shotDensities[otherTeam]

    # Define colormap
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "orange_white_black",
        ["orange", "white", "black"]
    )

    ## Do the plotting

    # Plot shot density underneath
    shotDensity = ax.pcolormesh(x, y, shotDensities['combined'], vmin=vmax*-1, vmax=vmax, cmap=cmap, alpha=0.8, shading='auto', zorder=2)

    # Plot shots on goal
    plt.plot(stats['shot-on-goal']['Flyers']['xs'], stats['shot-on-goal']['Flyers']['ys'], marker='o', color='black', markersize=2, linestyle='none')
    plt.plot(stats['shot-on-goal'][otherTeam]['xs'], stats['shot-on-goal'][otherTeam]['ys'], marker='o', color='orange', markersize=2, linestyle='none')

    # Plot shots on goal
    plt.plot(stats['goal']['Flyers']['xs'], stats['goal']['Flyers']['ys'], marker='x', color='black', markersize=8, linestyle='none')
    plt.plot(stats['goal'][otherTeam]['xs'], stats['goal'][otherTeam]['ys'], marker='x', color='orange', markersize=8, linestyle='none')

    # Turn of axes
    ax.set_axis_off()

    # Make it square
    plt.gca().set_aspect('equal', adjustable='box')

    # Save the plot
    plt.savefig(savePath + 'shotDensityMap.png',  bbox_inches='tight')


