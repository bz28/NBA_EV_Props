import sys
from nba_api.stats.static import players
from nba_api.stats.endpoints import playerdashboardbyyearoveryear



# Fetch all active NBA players
active_players = players.get_active_players()
player_dictionary =  {}
# Print each player's name and ID
for player in active_players:
    player_dictionary[player['full_name']] = player['id']






