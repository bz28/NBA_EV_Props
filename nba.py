import sys
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, teamgamelog
from nba_api.stats.endpoints import playerdashboardbyyearoveryear, teamyearbyyearstats
import time 

# import pandas as pd
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score
# import joblib  # For saving/loading the model



class player_data_training:

    def __init__(self):
        self.nba_teams = teams.get_teams()
        self.team_dictionary = {team['abbreviation']: team['id'] for team in self.nba_teams}
        self.active_players = players.get_active_players()
        self.player_dictionary = {player['full_name']: player['id'] for player in self.active_players}
        self.season_stats_dictionary = {}
        self.season_games_dictionary = {}

       # self.data = pd.DataFrame(columns=[
       #     'player_id','home_or_away', 'opponent_win_percentage', 'last_game_bad', 'last_five', 'target'
       # ])
        #self.model = None


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

    def season_stats(self, player_name ):
        dashboard = self.make_api_call(playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear, player_id=self.player_dictionary[player_name])
        season_stats = dashboard.get_data_frames()[1]  
        season_dict = season_stats.to_dict('records')
        stats_2024_25 = None
        stats_2023_24 = None
        stats_2022_23 = None
        stats_2021_22 = None
        stats_2020_21 = None
        for item in season_dict:
            if item['GROUP_VALUE'] == '2024-25':
                print("hi")
                stats_2024_25 = item
               
            if item['GROUP_VALUE'] == '2023-24':
                
                stats_2023_24 = item
              
            if item['GROUP_VALUE'] == '2022-23':
                stats_2022_23 = item
              
            if item['GROUP_VALUE'] == '2021-22':
                stats_2021_22 = item
               
            if item['GROUP_VALUE'] == '2020-21':
                stats_2020_21 = item
            
        if stats_2024_25:
            print("hi")
            ppg = stats_2024_25['PTS'] / stats_2024_25['GP']
            reb = stats_2024_25['REB'] / stats_2024_25['GP']
            ast = stats_2024_25['AST'] / stats_2024_25['GP']
            print(f"Player Name: {player_name} 2024-25 Stats - PPG: {ppg}, REB: {reb}, AST: {ast}")
            self.season_stats_dictionary["2024-25"] = [ppg, reb, ast]
            print(self.season_stats_dictionary)
         
        if stats_2023_24:
            print("gay")
            ppg = stats_2023_24['PTS'] / stats_2023_24['GP']
            reb = stats_2023_24['REB'] / stats_2023_24['GP']
            ast = stats_2023_24['AST'] / stats_2023_24['GP']
            print(f"Player Name: {player_name} 2023-24 Stats - PPG: {ppg}, REB: {reb}, AST: {ast}")
            self.season_stats_dictionary["2023-24"] = [ppg, reb, ast]
            print(self.season_stats_dictionary)
        if stats_2022_23:
            ppg = stats_2022_23['PTS'] / stats_2022_23['GP']
            reb = stats_2022_23['REB'] / stats_2022_23['GP']
            ast = stats_2022_23['AST'] / stats_2022_23['GP']
            self.season_stats_dictionary["2022-23"] = [ppg, reb, ast]
           
        if stats_2021_22:
            ppg = stats_2021_22['PTS'] / stats_2021_22['GP']
            reb = stats_2021_22['REB'] / stats_2021_22['GP']
            ast = stats_2021_22['AST'] / stats_2021_22['GP']
            self.season_stats_dictionary["2021-22"] = [ppg, reb, ast]
            
        if stats_2020_21:
            ppg = stats_2020_21['PTS'] / stats_2020_21['GP']
            reb = stats_2020_21['REB'] / stats_2020_21['GP']
            ast = stats_2020_21['AST'] / stats_2020_21['GP']
            self.season_stats_dictionary["2020-21"] = [ppg, reb, ast]
           
        
        return [0, 0, 0]
        

    def was_last_game_bad(self,  stats, season):
        season_stats = self.season_stats_dictionary[season]
        ppg=season_stats[0]
        prev_game_points=stats['PTS'] # called in the game_stats function
        #print(f"Ppg: {ppg}, Prev Game Points: {prev_game_points}")
        if  (ppg - prev_game_points) >= 0.5*ppg: # If the player has 50% less points than their season average
            return 1 # Return 1 if the player has 50% less points than their season average
            
        else:
            return 0 # Return 0 if the player had a good game
    

    def last_five_games(self, game_id, games, season):
       
        season_stats = self.season_stats_dictionary[season]  
        game_index = games[games['Game_ID'] == game_id].index[0]
        start_index = max(0, game_index - 5)
        last_five_games = games.iloc[start_index:game_index]
        total_points=0
        
        for index, game in last_five_games.iterrows():
            points = game['PTS']
        
            total_points+=points
        
        avg_points = total_points/5
            
        if avg_points >= season_stats[0]*1.25:
            return 1
        elif avg_points <= season_stats[0]*0.75: 
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
        #print(f"Home/Away: {home_or_away_parameter}")
        return home_or_away_parameter


    def opponent_win_percentage(self, opponent_id, season): 
        Opponent_stats = self.make_api_call(teamyearbyyearstats.TeamYearByYearStats, team_id=opponent_id)
        Opponent_stats_df = Opponent_stats.get_data_frames()[0]
        current_season_stats = Opponent_stats_df[Opponent_stats_df['YEAR'] == season]

        if not current_season_stats.empty:
            win_percentage = current_season_stats.iloc[0]['WIN_PCT']
        else:
            win_percentage = 0

        if win_percentage > 0.5:
            return 1     # 1 if the opponent has a win percentage greater than 50%
        else:
            return 0     # 0 if the opponent has a win percentage less than 50%
        

    def game_stats(self, player_name):
        player_id = self.player_dictionary[player_name]
        
        print("hi", self.season_stats_dictionary)
        season_stat = self.season_stats(player_name)
        last_game_stats = None

        season_points_avg=season_stat[0]
     

        
       
        new_rows = []  # Use a list to collect new rows
        for season in self.season_stats_dictionary:
            game_logs = self.make_api_call(playergamelog.PlayerGameLog, player_id=player_id, season=season)

            if game_logs is None:
                return
            games = game_logs.get_data_frames()[0]
            games = games.iloc[::-1].reset_index(drop=True)
            self.season_games_dictionary[season] = games


        

            for index, game in games.iterrows():
                time.sleep(0.5)  # Sleep for 1 second between requests
                game_date = game['GAME_DATE']
                matchup = game['MATCHUP']
                opponent = matchup.split(' ')[2] if '@' in matchup else matchup.split(' ')[2]
                opponent_id = self.team_dictionary[opponent]
                
                if last_game_stats:
                    last_game_bad_parameter = self.was_last_game_bad( last_game_stats, season) # 1 if the player has 50% less points than their season average, 0 if the player had a good game

                    #print(f"Last Game Stats: {last_game_stats}")
                    #print(f"Date: {last_game_stats['GAME_DATE']}, Points: {last_game_stats['PTS']}, Rebounds: {last_game_stats['REB']}, Assists: {last_game_stats['AST']}")
                    #print("-----")

                else:
                    last_game_bad_parameter= -1 # If there is no last game, return -1
                # parameters to train the model
                home_or_away_parameter = self.home_or_away(game)
                opponent_win_percentage_parameter = self.opponent_win_percentage(opponent_id, season) # 1 if the opponent has a win percentage greater than 50%, 0 if the opponent has a win percentage less than 50% 
                last_five_parameter = self.last_five_games(game['Game_ID'],games, season) # 1 if the player has scored more than 50% of their season average in the last 5 games, 0 if the player has scored less than 50% of their season average in the last 5 games, 2 if the player has scored more than 50% of their season average in the last 5 games
                
                last_game_stats = {
                    'GAME_DATE': game_date,
                    'PTS': game['PTS'],
                    'REB': game['REB'],
                    'AST': game['AST']
                }

                # Define target variable (example: `1` if player scored over a certain threshold, otherwise `0`)
                target = 1 if game['PTS'] > season_points_avg else 0
                #print(target)

                # append data to new list
                # new_rows.append({
                #     'player_id': player_id,
                #     'home_or_away': home_or_away_parameter,
                #     'opponent_win_percentage': opponent_win_percentage_parameter,
                #     'last_game_bad': last_game_bad_parameter,
                #     'last_five': last_five_parameter,
                #     'target': target
                # })


                # Display game details
                print(f"Player ID: {player_id}")
                print(f"Home/Away: {home_or_away_parameter}")
                print(f"Opponent Win Percentage: {opponent_win_percentage_parameter}")
                print(f"Last 5 Games: {last_five_parameter}")
                print(f"Last Game Bad: {last_game_bad_parameter}")
                print(f"Game Date: {game_date}")
                print(f"Opponent: {opponent}")
                
                print(f"Points: {game['PTS']}, Rebounds: {game['REB']}, Assists: {game['AST']}")
                print("-----")

        # self.data = pd.concat([self.data, pd.DataFrame(new_rows)], ignore_index=True)

            # Train the model if we have enough data
            #if len(self.data) > 50:  # Example threshold
        # self.train_model()
            

            time.sleep(5)
        time.sleep(2)



   
    # def train_model(self):
    #     # Split data into features (X) and target (y)
    #     X = self.data[['player_id','home_or_away', 'opponent_win_percentage', 'last_game_bad', 'last_five']]
    #     y = self.data['target']
    #     y = y.astype(int)
    #     print("y data type:", y.dtype)
    #     # Split into training and testing sets
    #     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #     # Train a Random Forest model
    #     self.model = RandomForestClassifier(n_estimators=100, random_state=42)
    #     self.model.fit(X_train, y_train)

    #     # Evaluate the model
    #     y_pred = self.model.predict(X_test)
    #     print("Model Accuracy:", accuracy_score(y_test, y_pred))
    #     baseline_accuracy = max(y.value_counts(normalize=True))
    #     print(f"Baseline Accuracy: {baseline_accuracy:.2f}")
    #     # Save the model for future use
    #     #joblib.dump(self.model, 'player_performance_model.pkl')


# Example usage
example =  player_data_training()
count = 0
for player in example.player_dictionary:
    if count == 1:
        break
    example.game_stats(player)
    count += 1





