import sys
from nba_api.stats.static import players
from nba_api.stats.endpoints import playerdashboardbyyearoveryear



# Fetch all active NBA players
active_players = players.get_active_players()
player_dictionary =  {}
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

        

        
        
        
        
            # Fetch team's win percentage
        '''
        
        
        print(season_dict)
        for game_data in season_dict:
            if game_data['SEASON_ID'] == '2024-25':
                # Check if the game is home or away
                if 'vs.' in game_data['MATCHUP']:
                    home_game = True
                else:
                    home_game = False
                team_id = game_data['TEAM_ID']
                team_dashboard = teamdashboardbylastngames.TeamDashboardByLastNGames(team_id=team_id)
                team_stats = team_dashboard.get_data_frames()[0]  # Assuming the first DataFrame contains team stats
                win_percentage = team_stats['W_PCT'].iloc[0]

                # Display stats based on conditions
                print(f"Game: {game_data['MATCHUP']}, Date: {game_data['GAME_DATE']}")
                if home_game:
                    print(f"Home Game Stats - PTS: {game_data['PTS']}, REB: {game_data['REB']}, AST: {game_data['AST']}")
                else:
                    print(f"Away Game Stats - PTS: {game_data['PTS']}, REB: {game_data['REB']}, AST: {game_data['AST']}")

                if win_percentage > 0.5:
                    print(f"High Win% Stats - PTS: {game_data['PTS']}, REB: {game_data['REB']}, AST: {game_data['AST']}")
                else:
                    print(f"Low Win% Stats - PTS: {game_data['PTS']}, REB: {game_data['REB']}, AST: {game_data['AST']}")

        '''






