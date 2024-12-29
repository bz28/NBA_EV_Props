import sys
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.endpoints import playerdashboardbyyearoveryear


# Fetch all active NBA players
active_players = players.get_active_players()
player_dictionary = {}
# Print each player's name and ID
for player in active_players:
    player_dictionary[player['full_name']] = player['id']

    if player['full_name'] == 'Jalen Green':
        # Fetch player dashboard data by year over year
        dashboard = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id=player['id'])
        # Extract data for the 2022-23 season
        season_stats = dashboard.get_data_frames()[1]  # Assuming the second DataFrame contains seasonal stats
        # Convert DataFrame to dictionary for the 2022-23 season
        season_dict = season_stats.to_dict('records')
        print(season_dict)
        # Simplified search for the 2022-23 season data in the dictionary
        stats_2022_23 = None
        for item in season_dict:
            if item['GROUP_VALUE'] == '2022-23':
                stats_2022_23 = item
                break
        if stats_2022_23:
            # Extract PPG, REB, and AST
            ppg = stats_2022_23['PTS'] / stats_2022_23['GP']
            reb = stats_2022_23['REB'] / stats_2022_23['GP']
            ast = stats_2022_23['AST'] / stats_2022_23['GP']
            print(f"Jalen Green 2022-23 Stats - PPG: {ppg}, REB: {reb}, AST: {ast}")






    if player['full_name'] == 'Amen Thompson':
        # Fetch player game logs for the 2024-25 season










    


        game_logs = playergamelog.PlayerGameLog(player_id=player['id'], season='2024-25')
        games = game_logs.get_data_frames()[0]  # The first DataFrame contains the game logs

        # Iterate through each game log
        away_games = []
        home_games = []
        for index, game in games.iterrows():
            print(f"Game Date: {game['GAME_DATE']}")
            print(f"Opponent: {game['MATCHUP']}")
            if "@" in game['MATCHUP']:
                away_games.append(game)
            else:
                home_games.append(game)
            print(f"Points: {game['PTS']}, Rebounds: {game['REB']}, Assists: {game['AST']}")
            print("-----")








