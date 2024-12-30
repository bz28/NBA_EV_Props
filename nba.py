import sys
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, teamgamelog
from nba_api.stats.endpoints import playerdashboardbyyearoveryear, teamyearbyyearstats



class player_data_training:

    def __init__(self):
        nba_teams = teams.get_teams()
        self.team_dictionary = {team['abbreviation']: team['id'] for team in nba_teams}
        active_players = players.get_active_players()
        self.player_dictionary = {player['full_name']: player['id'] for player in active_players}


    def season_stats(self, player_name):
        dashboard = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id=self.player_dictionary[player_name])
        season_stats = dashboard.get_data_frames()[1]  
        season_dict = season_stats.to_dict('records')
        stats_2024_25 = None
        for item in season_dict:
            if item['GROUP_VALUE'] == '2024-25':
                stats_2024_25 = item
                break
        if stats_2024_25:
            ppg = stats_2024_25['PTS'] / stats_2024_25['GP']
            reb = stats_2024_25['REB'] / stats_2024_25['GP']
            ast = stats_2024_25['AST'] / stats_2024_25['GP']
            print(f"Player Name: {player_name} 2024-25 Stats - PPG: {ppg}, REB: {reb}, AST: {ast}")
            return [ppg, reb, ast]
        else:
            return [0, 0, 0]

    def was_last_game_bad(self, player_name, stats, season_stats):
        ppg=season_stats[0]
        prev_game_points=stats['PTS'] # called in the game_stats function

        if  (ppg - prev_game_points) > 0.75*ppg: # If the player has 75% less points than their season average
            return 1 # Return 1 if the player has 75% less points than their season average
            
        else:
            return 0 # Return 0 if the player had a good game
    

    def last_five_games(self, game_id, games, season_stats):
        game_index = games[games['Game_ID'] == game_id].index[0]
        start_index = max(0, game_index - 5)
        last_five_games = games.iloc[start_index:game_index]

        above_avg = True

        below_avg = True

        
        for index, game in last_five_games.iterrows():
            points = game['PTS']
        
            if points > season_stats[0]:
                below_avg = False
            else:
                above_avg = False
            
        if above_avg:
            return 1
        elif below_avg:
            return 0 
        else:
            return 2



    def home_or_away(self, game_logs):
        games = game_logs.get_data_frames()[0]  # The first DataFrame contains the game logs
        games = games.iloc[::-1].reset_index(drop=True)
        for index, game in games.iterrows():
            matchup = game['MATCHUP']

            # Determine if the game is home or away
            home_or_away = "away" if "@" in matchup else "home"

            # home = 1; away = 0
            home_or_away_parameter = 1 if home_or_away == 'home' else 0

            # Display game details
            print(f"Home/Away: {home_or_away_parameter}")
            return home_or_away_parameter


    def opponent_win_percentage(self, game_logs): 
        games = game_logs.get_data_frames()[0]  # The first DataFrame contains the game logs
        last_game_stats = None
        games = games.iloc[::-1].reset_index(drop=True)
        for index, game in games.iterrows():
            game_date = game['GAME_DATE']
            matchup = game['MATCHUP']
            opponent = matchup.split(' ')[2] if '@' in matchup else matchup.split(' ')[2]
            opponent_id = self.team_dictionary[opponent]

            # Determine if the game is home or away

            team_stats = teamyearbyyearstats.TeamYearByYearStats(team_id=opponent_id)
            team_stats_df = team_stats.get_data_frames()[0]
            current_season_stats = team_stats_df[team_stats_df['YEAR'] == '2024-25']

            if not current_season_stats.empty:
                win_percentage = current_season_stats.iloc[0]['WIN_PCT']
            else:
                win_percentage = 0

            if last_game_stats:
                print(f"Last Game Stats: {last_game_stats}")
                print(f"Date: {last_game_stats['GAME_DATE']}, Points: {last_game_stats['PTS']}, Rebounds: {last_game_stats['REB']}, Assists: {last_game_stats['AST']}")
                print("-----")

            last_game_stats = {
                'GAME_DATE': game_date,
                'PTS': game['PTS'],
                'REB': game['REB'],
                'AST': game['AST']
            }

            # winning season = 1; losing season = 0
            win_percentage_parameter = 1 if win_percentage > 0.5 else 0 

            
            # Display game details
            print(f"Opponent Win Percentage: {win_percentage}")
            return win_percentage_parameter
            

    def game_stats(self, player_name):
        player_id = self.player_dictionary[player_name]
        game_logs = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25')
        games = game_logs.get_data_frames()[0]  # The first DataFrame contains the game logs
        season_stat = player_data_training().season_stats(player_name)
        last_game_stats = None
        games = games.iloc[::-1].reset_index(drop=True)
        for index, game in games.iterrows():
            game_date = game['GAME_DATE']
            matchup = game['MATCHUP']
            opponent = matchup.split(' ')[2] if '@' in matchup else matchup.split(' ')[2]

            if last_game_stats:
                print(f"Last Game Stats: {last_game_stats}")
                print(f"Date: {last_game_stats['GAME_DATE']}, Points: {last_game_stats['PTS']}, Rebounds: {last_game_stats['REB']}, Assists: {last_game_stats['AST']}")
                print("-----")

            last_game_stats = {
                'GAME_DATE': game_date,
                'PTS': game['PTS'],
                'REB': game['REB'],
                'AST': game['AST']
            }
            # parameters to train the model
            home_or_away_parameter = player_data_training().home_or_away(game_logs)
            opponent_win_percentage_parameter = player_data_training().opponent_win_percentage(game_logs)
            last_game_bad_parameter = player_data_training().was_last_game_bad(player_name, last_game_stats, season_stat)
            last_five_parameter = player_data_training().last_five_games(game['Game_ID'],games, season_stat)

            
            # Display game details
            print(f"Home/Away: {home_or_away_parameter}")
            print(f"Opponent Win Percentage: {opponent_win_percentage_parameter}")
            print(f"Last 5 Games: {last_five_parameter}")
            print(f"Last Game Bad: {last_game_bad_parameter}")
            print(f"Game Date: {game_date}")
            print(f"Opponent: {opponent}")
            
            print(f"Points: {game['PTS']}, Rebounds: {game['REB']}, Assists: {game['AST']}")
            print("-----")


# Example usage
player_data_training().game_stats('Jalen Green')





