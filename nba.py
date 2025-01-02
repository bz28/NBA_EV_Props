import sys
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, teamgamelog
from nba_api.stats.endpoints import playerdashboardbyyearoveryear, teamyearbyyearstats
import time 



class player_data_training:

    def __init__(self):
        self.nba_teams = teams.get_teams()
        self.team_dictionary = {team['abbreviation']: team['id'] for team in self.nba_teams}
        self.active_players = players.get_active_players()
        self.player_dictionary = {player['full_name']: player['id'] for player in self.active_players}

    def make_api_call(self, func, *args, **kwargs):
        max_retries = 5
        backoff_factor = 1  # seconds
        for attempt in range(max_retries):
            try:
                response = func(*args, **kwargs)
                return response
            except Exception as e:
                print(f"API call failed: {e}, retrying in {backoff_factor} seconds...")
                time.sleep(backoff_factor)
                backoff_factor *= 2  # Exponential backoff
        print("Failed to retrieve data after several attempts.")
        return None

    def season_stats(self, player_name):
        dashboard = self.make_api_call(playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear, player_id=self.player_dictionary[player_name])
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

    def was_last_game_bad(self,  stats, season_stats):
        ppg=season_stats[0]
        prev_game_points=stats['PTS'] # called in the game_stats function
        print(f"Ppg: {ppg}, Prev Game Points: {prev_game_points}")
        if  (ppg - prev_game_points) >= 0.5*ppg: # If the player has 50% less points than their season average
            return 1 # Return 1 if the player has 50% less points than their season average
            
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



    def home_or_away(self, game):
        
        matchup = game['MATCHUP']

            # Determine if the game is home or away
        home_or_away = "away" if "@" in matchup else "home"

            # home = 1; away = 0
        home_or_away_parameter = 1 if home_or_away == 'home' else 0

            # Display game details
        print(f"Home/Away: {home_or_away_parameter}")
        return home_or_away_parameter


    def opponent_win_percentage(self, opponent_id): 
        Opponent_stats = self.make_api_call(teamyearbyyearstats.TeamYearByYearStats, team_id=opponent_id)
        Opponent_stats_df = Opponent_stats.get_data_frames()[0]
        current_season_stats = Opponent_stats_df[Opponent_stats_df['YEAR'] == '2024-25']

        if not current_season_stats.empty:
            win_percentage = current_season_stats.iloc[0]['WIN_PCT']
        else:
            win_percentage = 0

        if win_percentage > 0.5:
            return 1
        else:
            return 0

    def game_stats(self, player_name):
        player_id = self.player_dictionary[player_name]
        game_logs = self.make_api_call(playergamelog.PlayerGameLog, player_id=player_id, season='2024-25')
        if game_logs is None:
            return
        games = game_logs.get_data_frames()[0]
        season_stat = player_data_training().season_stats(player_name)
        last_game_stats = None
        
        games = games.iloc[::-1].reset_index(drop=True)
        for index, game in games.iterrows():
            time.sleep(0.5)  # Sleep for 1 second between requests
            game_date = game['GAME_DATE']
            matchup = game['MATCHUP']
            opponent = matchup.split(' ')[2] if '@' in matchup else matchup.split(' ')[2]
            opponent_id = self.team_dictionary[opponent]
            
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
            home_or_away_parameter = player_data_training().home_or_away(game)
            opponent_win_percentage_parameter = player_data_training().opponent_win_percentage(opponent_id)
            last_game_bad_parameter = player_data_training().was_last_game_bad( last_game_stats, season_stat)
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
        time.sleep(5)

# Example usage
example =  player_data_training()
count = 0
for player in example.player_dictionary:
    if count == 20:
        break
    example.game_stats(player)
    count += 1





