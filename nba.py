import sys
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, teamgamelog
from nba_api.stats.endpoints import playerdashboardbyyearoveryear, teamyearbyyearstats
#from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
# Fetch all NBA teams
nba_teams = teams.get_teams()
team_dictionary = {team['abbreviation']: team['id'] for team in nba_teams}

# Fetch all active NBA players
active_players = players.get_active_players()
player_dictionary = {player['full_name']: player['id'] for player in active_players}

def season_stats(player_name):
    dashboard = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id=player_dictionary[player_name])
    season_stats = dashboard.get_data_frames()[1]  # Assuming the second DataFrame contains seasonal stats
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

def last_game_bad(player_name, stats, season_stat):
    if  ( season_stat[0] - stats['PTS']) > 0.75*season_stat[0]:
        return 1
   
    elif (season_stat[2] - stats['AST']) > 0.5*season_stat[2]:
        return 1
    else:
        return 0
    return last_game

def last_five_games(player_name, game_id, games, season_stat):

    player_id = player_dictionary[player_name]
    game_index = games[games['Game_ID'] == game_id].index[0]
    start_index = max(0, game_index - 5)
    last_five_games = games.iloc[start_index:game_index]

    above = True

    below = True

    
    for index, game in last_five_games.iterrows():
        points = game['PTS']
       
        if points > season_stat[0]:
            below = False
        else:
            above = False
       
        
    if above:
        return 1
    elif below:
        return 0 
    else:
        return 2


    return None

def game_stats(player_name):
    player_id = player_dictionary[player_name]
    game_logs = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25')
    games = game_logs.get_data_frames()[0]  # The first DataFrame contains the game logs
    season_stat = season_stats(player_name)
    last_game_stats = None
    games = games.iloc[::-1].reset_index(drop=True)
    for index, game in games.iterrows():
        game_date = game['GAME_DATE']
        matchup = game['MATCHUP']
        opponent = matchup.split(' ')[2] if '@' in matchup else matchup.split(' ')[2]
        opponent_id = team_dictionary[opponent]

        # Determine if the game is home or away
        home_or_away = "away" if "@" in matchup else "home"

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

        home_or_away_parameter = 1 if home_or_away == 'home' else 0

        win_percentage_parameter = 1 if win_percentage > 0.5 else 0

        last_game_bad_parameter = last_game_bad(player_name, last_game_stats, season_stat)
       
        last_five_parameter = last_five_games(player_name, game['Game_ID'],games, season_stat)

        
        # Display game details
        print(f"Last 5 Games: {last_five_parameter}")
        print(f"Last Game Bad: {last_game_bad_parameter}")
        print(f"Win Percentage: {win_percentage_parameter}")
        print(f"Home/Away: {home_or_away_parameter}")
        print(f"Game Date: {game_date}")
        print(f"Opponent: {opponent}")
        
        print(f"Points: {game['PTS']}, Rebounds: {game['REB']}, Assists: {game['AST']}")
        print(f"Opponent Win Percentage: {win_percentage}")
        print("-----")

# Example usage
game_stats('Jalen Green')





