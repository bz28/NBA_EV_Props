class player_stats:
    def __init__(self, player_name, player_team, bankroll):
        self.player_name = player_name
        self.player_team = player_team
        self.bankroll = bankroll # how much total money the player has to bet

    def player_info(self): # Ensure correct input of player information
        print(f"Player Name: {self.player_name}")
        print(f"Player Team: {self.player_team}")

    def prop_over_probability(self, prop, betting_line): # probability of a player prop being over a certain number

        # machine learning model to predict the probability of a player prop

        return 0.5 # placeholder for testing
    
    def prop_under_probability(self, prop, betting_line): # probability of a player prop being under a certain number
        return 1 - self.prop_over_probability(prop, betting_line)

    def expected_value_calculator(self, prop, betting_line, over_betting_odds, under_betting_odds):
        probability_over=self.prop_over_probability(prop, betting_line) # calculate the probability of the player prop over
        probability_under=self.prop_under_probability(prop, betting_line)
        recommended_bet_size=0  

        if over_betting_odds<0:
            expected_over_profit=100/-over_betting_odds
        else:
            expected_over_profit=over_betting_odds/100
                
        if under_betting_odds<0:
            expected_under_profit=100/-under_betting_odds
        else:   
            expected_under_profit=under_betting_odds/100

        ev_over_prop=(probability_over*expected_over_profit)-(probability_under*expected_under_profit)
        ev_under_prop=(probability_under*expected_under_profit)-(probability_over*expected_over_profit)

        if ev_over_prop>0.05:  # must have at least a 5% edge to bet
            if ev_over_prop>0.2:
                recommended_bet_size=0.05*self.bankroll
            elif ev_over_prop>0.1:
                recommended_bet_size=0.02*self.bankroll
            else:
                recommended_bet_size=0.01*self.bankroll
            print('Bet the over!!!')
            print(f"EV: {ev_over_prop}")
            print(f'Bet: ${recommended_bet_size}')
            return
            
        
        elif ev_under_prop>0.05:  # must have at least a 5% edge to bet
            if ev_under_prop>0.2:
                recommended_bet_size=0.05*self.bankroll
            elif ev_under_prop>0.1:
                recommended_bet_size=0.02*self.bankroll
            else:
                recommended_bet_size=0.01*self.bankroll
            print('Bet the under!!!')
            print(f"EV: {ev_under_prop}")
            print(f'Bet: ${recommended_bet_size}')
            return
        
        else:
            print("No high EV bets")
            return
        

# Testing Accuracy of the Expected Value Calculator
test_case_1=player_stats("Lebron James", "Los Angeles Lakers", 10000).expected_value_calculator('points', 25.5, -120, -130)
assert test_case_1==None
