class player_stats:
    def __init__(self, player_name, player_age, player_team):
        self.player_name = player_name
        self.player_team = player_team

    def player_info(self): # Ensure correct input of player information
        print(f"Player Name: {self.player_name}")
        print(f"Player Team: {self.player_team}")

    def prop_over_probability(self, prop, betting_line): # probability of a player prop being over a certain number
        # machine learning model to predict the probability of a player prop
        pass
    
    def prop_under_probability(self, prop, betting_line): # probability of a player prop being under a certain number
        return 1 - self.prop_over_probability(prop, betting_line)

    def expected_value_calculator(self, prop, betting_line, over_betting_odds, under_betting_odds):
        probability_over=self.prop_over_probability(prop, betting_line) # calculate the probability of the player prop over
        probability_under=self.prop_under_probability(prop, betting_line)
        
        if over_betting_odds<0:
            expected_profit=100/-over_betting_odds
        else:
            expected_profit=over_betting_odds/100
        
        if under_betting_odds<0:
            expected_loss=100/-under_betting_odds
        else:   
            expected_loss=under_betting_odds/100
        

        ev_over_prop=(probability_over*expected_profit)-(probability_under*expected_loss)
        ev_under_prop=(probability_under*expected_profit)-(probability_over*expected_loss)

        if ev_over_prop>0 and ev_under_prop>0:
            print(f"Both the over and under have a positive expected value")
            return(f"The under has an expected value of {ev_under_prop} and the over has an expected value of {ev_over_prop}")


        elif ev_over_prop>0:
            return f"The over has an expected value of {ev_over_prop}"
        
        elif ev_under_prop>0:
            return f"The under has an expected value of {ev_under_prop}"
        
        else:
            return "No positive expected value"



        

