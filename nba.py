import sys
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, teamgamelog
from nba_api.stats.endpoints import playerdashboardbyyearoveryear, teamyearbyyearstats
from datetime import datetime
import time 

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib  # For saving/loading the model



class player_data_training:

    def __init__(self):
        self.nba_teams = teams.get_teams()
        self.team_dictionary = {team['abbreviation']: team['id'] for team in self.nba_teams}
        self.active_players = players.get_active_players()
        self.player_dictionary = {player['full_name']: player['id'] for player in self.active_players}
        self.season_stats_dictionary = {}
        self.season_games_dictionary = {}
        self.data = pd.DataFrame(columns=[
           'player_id','home_or_away', 'opponent_win_percentage', 'last_game_bad', 'last_five', 'starter','target'
        ])
        self.model = None

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
        
    def was_last_game_bad(self,  stats, season):
        season_stats = self.season_stats_dictionary[season]
        ppg=season_stats[0]
        prev_game_points=stats['PTS'] 
        #print(f"Ppg: {ppg}, Prev Game Points: {prev_game_points}")
        if  (ppg - prev_game_points) >= 0.5*ppg: 
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
        home_or_away = "away" if "@" in matchup else "home"
        # home = 1; away = 0
        home_or_away_parameter = 1 if home_or_away == 'home' else 0
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
            return 1     
        else:
            return 0     
        
    def season_stats(self, player_name ):
        dashboard = self.make_api_call(playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear, player_id=self.player_dictionary[player_name])
        season_stats = dashboard.get_data_frames()[1]  
        season_dict = season_stats.to_dict('records')
        #adding all season stats to the dictionary
        for item in season_dict:
            ###
            ###
            # how should we handle if they play for multiple teams in a season?    
            if item['GROUP_VALUE'] in self.season_stats_dictionary:
                ppg=item['PTS'] /  item['GP']
                self.season_stats_dictionary[item['GROUP_VALUE']].append(ppg)
                continue
            ###
            ###        
            ppg =  item['PTS'] /  item['GP']
            self.season_stats_dictionary[item["GROUP_VALUE"]] = [ppg]  # value=list of season stats including rpg and apg
        return None
    


    def back_to_back_parameter(self, previous_game_date, current_game_date):
        # Convert string dates to datetime objects using the NBA API format
        prev_date = datetime.strptime(previous_game_date.title(), '%b %d, %Y')
        curr_date = datetime.strptime(current_game_date.title(), '%b %d, %Y')

        # Calculate the difference in days
        days_difference = (curr_date - prev_date).days

        # Return 1 if it's a back-to-back (1 day difference), 0 otherwise
        return 1 if days_difference == 1 else 0

    def game_stats(self, player_name):
        player_id = self.player_dictionary[player_name]
        season_stat = self.season_stats(player_name) # must be called to invoke season_stats_dictionary
        last_game_stats = None
        new_rows = [] 
        count=0  # track total # of seasons
        previous_season = None # previous season to use if the player has played for less than 10 games in a season
        sorted_seasons = sorted(self.season_stats_dictionary.keys()) # want to get the seasons in order
        
        sorted_seasons = [season for season in sorted_seasons if int(season[5:7]) >= 23] # only get the last 3 seasons
     
        for season in sorted_seasons:
            # calculate average points per game for the current season up to the current game
            current_season_games_count = 0
            current_season_games_points_sum = 0
            current_season_games_points_avg = 0
            ###
            ###
            # if the player has played for more than 1 team in a season, we need to handle this
            #season_points_avg=sum(self.season_stats_dictionary[season])/len(self.season_stats_dictionary[season])
            ###
            ###
            game_logs = self.make_api_call(playergamelog.PlayerGameLog, player_id=player_id, season=season)
            if game_logs is None:
                return
            games = game_logs.get_data_frames()[0]
            games = games.iloc[::-1].reset_index(drop=True)
            self.season_games_dictionary[season] = games
            for index, game in games.iterrows():
                time.sleep(0.5) # Avoid rate limiting
                current_season_games_count +=1
                current_season_games_points_sum += game['PTS']
              
                current_season_games_points_avg = current_season_games_points_sum/current_season_games_count
       

                game_date = game['GAME_DATE']
                matchup = game['MATCHUP']
                opponent = matchup.split(' ')[2] if '@' in matchup else matchup.split(' ')[2]
                opponent_id = self.team_dictionary[opponent]

                if last_game_stats:
                    last_game_bad_parameter = self.was_last_game_bad( last_game_stats, season)
                    back_to_back_parameter = self.back_to_back_parameter(last_game_stats['GAME_DATE'], game_date)
                else:
                    last_game_bad_parameter= -1
                    back_to_back_parameter = -1 # If there is no last game, return -1
                # parameters to train the model
                home_or_away_parameter = self.home_or_away(game)
                opponent_win_percentage_parameter = self.opponent_win_percentage(opponent_id, season) # 1 if the opponent has a win percentage greater than 50%, 0 if the opponent has a win percentage less than 50% 
                last_five_parameter = self.last_five_games(game['Game_ID'],games, season) # 1 if the player has scored more than 50% of their season average in the last 5 games, 0 if the player has scored less than 50% of their season average in the last 5 games, 2 if the player has scored more than 50% of their season average in the last 5 games
                starter_parameter = 1 if game['MIN'] >= 25 else 0  # 1 if the player has played more than 25 minutes, 0 if the player has played less than 25 minutes
                last_game_stats = {
                    'GAME_DATE': game_date,
                    'PTS': game['PTS'],
                    'REB': game['REB'],
                    'AST': game['AST']
                }
                # Define target variable (example: `1` if player scored over a certain threshold, otherwise `0`)
  
               
               # if the player has played for less than 10 games in a season, we need to use the previous season's stats
                if current_season_games_count < 10 and previous_season:
                    season_points_avg = sum(self.season_stats_dictionary[previous_season])/len(self.season_stats_dictionary[previous_season])
                elif current_season_games_count < 10 and not previous_season:
                    season_points_avg = 0
                else:
                    season_points_avg = current_season_games_points_avg
              
                
           
                
                target = 1 if game['PTS'] > season_points_avg else 0
                
               

                new_rows.append({
                    'player_id': player_id,
                    'home_or_away': home_or_away_parameter,
                    'opponent_win_percentage': opponent_win_percentage_parameter,
                    'last_game_bad': last_game_bad_parameter,
                    'last_five': last_five_parameter,
                    'starter': starter_parameter,
                    'back_to_back': back_to_back_parameter,
                    'target': target
                })
                #Display game details
                # print(f"Player ID: {player_id}")
                # print(f"Home/Away: {home_or_away_parameter}")
                # print(f"Opponent Win Percentage: {opponent_win_percentage_parameter}")
                # print(f"Last 5 Games: {last_five_parameter}")
                # print(f"Last Game Bad: {last_game_bad_parameter}")
                # print(f"Back to Back: {back_to_back_parameter}")
                # print(f"Game Date: {game_date}")
                # print(f"Opponent: {opponent}")
                # print(f"Points: {game['PTS']}, Rebounds: {game['REB']}, Assists: {game['AST']}")
                # print("-----")

        
            previous_season = season
            
                
        self.data = pd.concat([self.data, pd.DataFrame(new_rows)], ignore_index=True)
        self.train_model()
        time.sleep(2)
   
    def train_model(self):
        X = self.data[['player_id','home_or_away', 'opponent_win_percentage', 'last_game_bad', 'last_five', 'starter', 'back_to_back']]
        y = self.data['target']
        y = y.astype(int)
        print("y data type:", y.dtype)
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        # Train a Random Forest model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        # Evaluate the model
        y_pred = self.model.predict(X_test)
        print("Model Accuracy:", accuracy_score(y_test, y_pred))
        baseline_accuracy = max(y.value_counts(normalize=True))
        print(f"Baseline Accuracy: {baseline_accuracy:.2f}")
        # Save the model for future use
        #joblib.dump(self.model, 'player_performance_model.pkl')


# Example usage
player_data_training().game_stats('Fred VanVleet')
# example =  player_data_training()
# count = 0
# for player in example.player_dictionary:
#     if count == 1:
#         break
#     example.game_stats(player)
#     count += 1




